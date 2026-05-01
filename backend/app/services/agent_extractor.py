import json
import os

import anthropic

_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

_SYSTEM = """Eres un asistente especializado en derecho argentino.
Tu tarea es extraer todas las citas jurisprudenciales de un escrito judicial.
Para cada cita devuelve un objeto JSON con exactamente estos campos:
- claim: lo que el abogado afirma que establece el fallo (cita textual o paráfrasis del escrito)
- case_name: la carátula del expediente (ej. "Rodríguez c/ Estado Nacional s/ daños")
- court: el tribunal que dictó el fallo (ej. "CSJN", "Cámara Nacional de Apelaciones en lo Civil, Sala A")
- year_tomo_folio: referencia de publicación (ej. "2001, T.320 F.2105") o null si no figura

Responde ÚNICAMENTE con un array JSON válido. Sin explicaciones, sin markdown, sin texto adicional.
Si no hay citas jurisprudenciales, responde con [].

Ejemplo de respuesta:
[
  {
    "claim": "el daño moral es resarcible en forma autónoma",
    "case_name": "Pérez c/ García s/ daños y perjuicios",
    "court": "CSJN",
    "year_tomo_folio": "1999, T.322 F.1234"
  }
]"""


def extract_citations(text: str) -> list[dict]:
    if not text or not text.strip():
        raise ValueError("El texto del escrito está vacío.")

    message = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=_SYSTEM,
        messages=[{"role": "user", "content": f"Escrito judicial:\n\n{text}"}],
    )

    raw = message.content[0].text.strip()
    # strip markdown code fences if the model wraps the output
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        citations = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"La respuesta del agente no es JSON válido: {exc}") from exc

    if not isinstance(citations, list):
        raise ValueError("La respuesta del agente no es una lista JSON.")

    return citations
