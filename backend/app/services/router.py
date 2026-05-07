"""Deterministic Router — maps a citation to its natural source(s).

Pure regex + lookup tables; no LLM, no I/O. Microseconds per call.

Returns a RouteDecision with:
  primary    – source to try first
  secondary  – source to try if primary returns nothing (None = no cross-check)
  fallback   – True means skip primary/secondary and fan-out to all sources
"""

import re
from typing import Literal, TypedDict

SourceKey = Literal["CSJN", "SAIJ", "JUBA"]

# Set to True while JUBA's ASP.NET WebForms POST is not implemented.
# Routing rules that would normally target JUBA as primary substitute SAIJ
# until this flag is cleared.
JUBA_DISABLED = True


class RouteDecision(TypedDict):
    primary: SourceKey
    secondary: SourceKey | None
    fallback: bool


# ---------------------------------------------------------------------------
# Routing rule table
# Each entry: (pattern_on_field, field, primary, secondary)
#   field = "tomo_folio" | "court"
#   pattern is matched case-insensitively anywhere in the field value
# First match wins.
# ---------------------------------------------------------------------------

_RULES: list[tuple[re.Pattern, str, SourceKey, SourceKey | None]] = [
    # Fallos: T:P  →  CSJN primary, SAIJ secondary
    (re.compile(r"fallos\s*:\s*\d+\s*:\s*\d+", re.I), "tomo_folio", "CSJN", "SAIJ"),

    # CSJN court patterns  →  CSJN primary, SAIJ secondary
    (re.compile(r"\bC\.?S\.?J\.?N\.?\b", re.I), "court", "CSJN", "SAIJ"),
    (re.compile(r"corte\s+suprema", re.I), "court", "CSJN", "SAIJ"),

    # SCBA  →  JUBA primary (SAIJ while JUBA disabled), SAIJ secondary
    (re.compile(r"\bS\.?C\.?B\.?A\.?\b", re.I), "court", "JUBA", "SAIJ"),
    (re.compile(r"suprema\s+corte\s+de\s+(la\s+)?buenos\s+aires", re.I), "court", "JUBA", "SAIJ"),

    # Federal / national chambers  →  SAIJ only
    (re.compile(r"\bCN(Civ|Com|Fed|Trab|CAF|Crim)\b", re.I), "court", "SAIJ", None),
    (re.compile(r"c[aá]mara\s+nacional", re.I), "court", "SAIJ", None),

    # Buenos Aires provincial chambers  →  JUBA primary (SAIJ while disabled)
    (re.compile(
        r"c[aá]m(ara)?\.?\s+(apel|civ|com|pen|lab|cont)",
        re.I,
    ), "court", "JUBA", "SAIJ"),

    # Other provincial supreme courts  →  SAIJ only
    (re.compile(r"tribunal\s+superior|corte\s+de\s+justicia", re.I), "court", "SAIJ", None),
]

_FANOUT: RouteDecision = {"primary": "CSJN", "secondary": None, "fallback": True}


def route(citation: dict) -> RouteDecision:
    """Return the routing decision for *citation*.

    Checks year_tomo_folio first, then court. If nothing matches, returns
    fallback=True (fan-out to all sources).
    """
    tomo_folio = (citation.get("year_tomo_folio") or "").strip()
    court = (citation.get("court") or "").strip()

    for pattern, field, primary, secondary in _RULES:
        value = tomo_folio if field == "tomo_folio" else court
        if value and pattern.search(value):
            effective_primary = _resolve(primary)
            effective_secondary = _resolve(secondary) if secondary else None
            # If primary and secondary collapse to the same source, drop secondary
            if effective_secondary == effective_primary:
                effective_secondary = None
            return RouteDecision(
                primary=effective_primary,
                secondary=effective_secondary,
                fallback=False,
            )

    return _FANOUT


def _resolve(source: SourceKey) -> SourceKey:
    """Substitute SAIJ for JUBA while JUBA is disabled."""
    if source == "JUBA" and JUBA_DISABLED:
        return "SAIJ"
    return source
