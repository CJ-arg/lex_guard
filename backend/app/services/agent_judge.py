import json
import os

import anthropic

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client

_AUTO_WARNING_NO_TEXT = (
    "El fallo fue localizado en las fuentes oficiales pero no se pudo recuperar el texto completo. "
    "Se recomienda verificar el contenido directamente en la fuente antes de presentar el escrito."
)

_AUTO_DANGER_JUSTIFICATION = (
    "El fallo no fue encontrado en las fuentes verificadas. "
    "No es posible confirmar su existencia ni la interpretación invocada."
)

_AUTO_UNVERIFIABLE_JUSTIFICATION = (
    "No fue posible consultar ninguna de las fuentes oficiales (CSJN, SAIJ, JUBA). "
    "El error puede ser transitorio; se recomienda verificar manualmente antes de presentar el escrito."
)

_SYSTEM = """Eres un juez experto en derecho argentino.
Tu tarea es evaluar si la afirmación que hace un abogado sobre un fallo judicial es correcta.

Se te proporcionará:
- claim: lo que el abogado afirma que establece el fallo
- ruling_text: el texto verificado del fallo

Debes responder ÚNICAMENTE con un objeto JSON válido con exactamente estos campos:
- verdict: "approved", "warning" o "danger"
- justification: 2 o 3 oraciones en español claro y directo explicando el veredicto

Criterios:
- "approved": la afirmación es consistente con lo que el fallo efectivamente resolvió
- "warning": el fallo existe pero la correspondencia semántica es incierta o el fallo trata un tema tangencial
- "danger": el contenido del fallo contradice o es ajeno a la afirmación del abogado

Sin explicaciones adicionales, sin markdown, solo el JSON.

Ejemplo:
{"verdict": "approved", "justification": "La afirmación del abogado es consistente con la doctrina del fallo. El precedente efectivamente establece la operatividad directa de las garantías constitucionales sin necesidad de reglamentación."}"""


def _call_judge(claim: str, ruling_text: str) -> dict:
    message = _get_client().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"claim: {claim}\n\nruling_text: {ruling_text}",
            }
        ],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    if not raw:
        raise ValueError("Respuesta vacía del modelo")

    result = json.loads(raw)

    if result.get("verdict") not in ("approved", "warning", "danger"):
        raise ValueError(f"Veredicto inválido: {result.get('verdict')}")

    return result


def judge_citations(citations: list[dict]) -> list[dict]:
    results = []
    for citation in citations:
        if citation.get("unverifiable"):
            results.append({
                **citation,
                "verdict": "unverifiable",
                "justification": _AUTO_UNVERIFIABLE_JUSTIFICATION,
            })
            continue
        if not citation.get("found"):
            results.append({
                **citation,
                "verdict": "danger",
                "justification": _AUTO_DANGER_JUSTIFICATION,
            })
            continue

        if not citation.get("ruling_text"):
            results.append({
                **citation,
                "verdict": "warning",
                "justification": _AUTO_WARNING_NO_TEXT,
            })
            continue

        try:
            judgement = _call_judge(
                claim=citation.get("claim", ""),
                ruling_text=citation.get("ruling_text", ""),
            )
            results.append({**citation, **judgement})
        except Exception as exc:
            raise ValueError(f"Error al evaluar '{citation.get('case_name')}': {exc}") from exc

    return results
