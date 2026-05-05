import pytest
from app.services.router import route, JUBA_DISABLED


# ------------------------------------------------------------------
# Helper
# ------------------------------------------------------------------

def _c(court="", tomo_folio=""):
    return {"court": court, "year_tomo_folio": tomo_folio}


# ------------------------------------------------------------------
# Fallos: T:P  →  CSJN primary
# ------------------------------------------------------------------

def test_fallos_format_routes_csjn():
    d = route(_c(tomo_folio="Fallos: 330:4921"))
    assert d["primary"] == "CSJN"
    assert d["secondary"] == "SAIJ"
    assert d["fallback"] is False


def test_fallos_format_case_insensitive():
    assert route(_c(tomo_folio="fallos: 239:459"))["primary"] == "CSJN"


def test_fallos_format_with_spaces():
    assert route(_c(tomo_folio="Fallos:  239 : 459"))["primary"] == "CSJN"


# ------------------------------------------------------------------
# CSJN court patterns
# ------------------------------------------------------------------

def test_court_csjn_abbreviation():
    d = route(_c(court="CSJN"))
    assert d["primary"] == "CSJN"
    assert d["secondary"] == "SAIJ"


def test_court_csjn_dots():
    assert route(_c(court="C.S.J.N."))["primary"] == "CSJN"


def test_court_corte_suprema():
    assert route(_c(court="Corte Suprema de Justicia de la Nación"))["primary"] == "CSJN"


# ------------------------------------------------------------------
# SCBA  →  SAIJ while JUBA disabled
# ------------------------------------------------------------------

def test_court_scba_routes_saij_while_juba_disabled():
    assert JUBA_DISABLED, "test assumes JUBA_DISABLED=True"
    d = route(_c(court="SCBA"))
    assert d["primary"] == "SAIJ"
    assert d["fallback"] is False


def test_court_suprema_corte_ba():
    d = route(_c(court="Suprema Corte de Buenos Aires"))
    assert d["primary"] == "SAIJ"


# ------------------------------------------------------------------
# Federal / national chambers  →  SAIJ only
# ------------------------------------------------------------------

@pytest.mark.parametrize("court", ["CNCiv", "CNCom", "CNFed", "CNTrab", "CNCAF", "CNCrim"])
def test_federal_chambers_route_saij(court):
    d = route(_c(court=court))
    assert d["primary"] == "SAIJ"
    assert d["secondary"] is None
    assert d["fallback"] is False


def test_camara_nacional_pattern():
    assert route(_c(court="Cámara Nacional de Apelaciones en lo Civil"))["primary"] == "SAIJ"


# ------------------------------------------------------------------
# BA provincial chambers  →  SAIJ while JUBA disabled
# ------------------------------------------------------------------

def test_ba_chamber_routes_saij_while_juba_disabled():
    d = route(_c(court="Cám. Apel. Civ. y Com. Mar del Plata"))
    assert d["primary"] == "SAIJ"


def test_ba_chamber_abbreviated():
    assert route(_c(court="Cámara Civil y Comercial La Plata"))["primary"] == "SAIJ"


# ------------------------------------------------------------------
# Fan-out fallback
# ------------------------------------------------------------------

def test_empty_court_returns_fallback():
    d = route(_c(court=""))
    assert d["fallback"] is True


def test_unknown_court_returns_fallback():
    d = route(_c(court="Tribunal Arbitral Internacional XYZ"))
    assert d["fallback"] is True


def test_no_fields_returns_fallback():
    assert route({})["fallback"] is True


# ------------------------------------------------------------------
# tomo_folio takes priority over court
# ------------------------------------------------------------------

def test_fallos_tomo_folio_beats_ambiguous_court():
    d = route(_c(court="", tomo_folio="Fallos: 239:459"))
    assert d["primary"] == "CSJN"
    assert d["fallback"] is False
