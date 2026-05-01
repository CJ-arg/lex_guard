KNOWN_CASES: dict[str, str] = {
    "kot s.r.l. c/ estado nacional": (
        "El derecho a la intimidad y a la inviolabilidad del domicilio protege tanto el espacio físico "
        "como los documentos y papeles privados. La garantía constitucional del artículo 18 se extiende "
        "al domicilio comercial y a los registros empresariales frente a intervenciones estatales arbitrarias."
    ),
    "siri angel": (
        "Las garantías constitucionales son operativas y de aplicación directa, sin necesidad de ley "
        "reglamentaria que las instrumente. El amparo procede contra actos de autoridad pública que "
        "restringen derechos fundamentales de manera manifiestamente ilegítima."
    ),
    "halabi ernesto c/ p.e.n.": (
        "La acción de clase procede cuando existe un hecho único que lesiona a una pluralidad de sujetos "
        "y la pretensión está enfocada en el aspecto colectivo de los efectos. El art. 43 de la CN "
        "reconoce legitimación activa al afectado para interponer acción de amparo colectivo."
    ),
    "fayt carlos s. c/ estado nacional": (
        "La inamovilidad de los jueces federales mientras dure su buena conducta es una garantía "
        "de la independencia del poder judicial. La reforma constitucional no puede válidamente "
        "alterar atribuciones esenciales del Poder Judicial establecidas en la Constitución."
    ),
    "arriola sebastián y otros s/ causa n° 9080": (
        "La penalización de la tenencia de estupefacientes para consumo personal es inconstitucional "
        "en tanto afecta la autonomía personal garantizada por el art. 19 de la CN, siempre que "
        "dicha conducta no cause un perjuicio concreto a terceros o a la sociedad."
    ),
    "rodriguez maria marta c/ gcba": (
        "El derecho a la salud tiene jerarquía constitucional y operatividad directa. El Estado "
        "tiene obligación de garantizar prestaciones mínimas esenciales, y su omisión es "
        "susceptible de control judicial mediante acción de amparo."
    ),
    "lino onel c/ ferrocarril del estado": (
        "La responsabilidad del Estado por los daños causados por sus dependientes en el ejercicio "
        "de sus funciones es directa y objetiva. No se requiere acreditar culpa individual del agente "
        "para comprometer la responsabilidad de la administración pública."
    ),
    "peralta luis archidio y otro c/ estado nacional": (
        "En situaciones de grave perturbación económica el Estado puede adoptar medidas de emergencia "
        "que restrinjan temporariamente derechos patrimoniales, siempre que sean razonables, "
        "proporcionales y no afecten el núcleo esencial de los derechos afectados."
    ),
    "verbitsky horacio s/ habeas corpus": (
        "El habeas corpus colectivo es procedente cuando la situación de detención de un conjunto "
        "de personas afecta derechos fundamentales. Los jueces tienen el deber de hacer cesar "
        "condiciones de detención que resultan contrarias a la dignidad humana y a los estándares "
        "constitucionales e internacionales."
    ),
    "mendoza beatriz silvia y otros c/ estado nacional": (
        "La tutela del ambiente como bien colectivo exige la recomposición del daño y la prevención "
        "de futuros perjuicios. El Estado y los particulares son solidariamente responsables por el "
        "daño ambiental colectivo, con legitimación activa amplia para su reclamación judicial."
    ),
}


def investigate_citations(citations: list[dict]) -> list[dict]:
    results = []
    for citation in citations:
        key = citation.get("case_name", "").strip().lower()
        if key in KNOWN_CASES:
            results.append({**citation, "found": True, "ruling_text": KNOWN_CASES[key]})
        else:
            results.append({**citation, "found": False, "ruling_text": None})
    return results
