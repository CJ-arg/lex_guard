import logging
import re
import time

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
_log = logging.getLogger("lexguard")

from app.services.agent_extractor import extract_citations
from app.services.investigator import investigate_citations
from app.services.agent_judge import judge_citations
from app.services.extractor import extract_docx, extract_pdf
from app.services.sessions import get_session, save_session

app = FastAPI(title="LexGuard API")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    _log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor. Intente nuevamente."},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    _log.info("%s %s → %d (%.0fms)", request.method, request.url.path, response.status_code, ms)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before production
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 1 * 1024 * 1024  # 1 MB
MAX_TEXT_CHARS = 50_000              # ~12k tokens, enough for a 15-page brief
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

_PATH_RE = re.compile(r"[/\\]")


def _sanitize_filename(name: str) -> str:
    name = name.replace("\x00", "").strip()
    name = _PATH_RE.sub("_", name)
    return name[:255] or "documento"


class ExtractRequest(BaseModel):
    text: str


class InvestigateRequest(BaseModel):
    citations: list[dict]


class SaveSessionRequest(BaseModel):
    document_name: str = Field(max_length=255)
    user_note: str | None = Field(default=None, max_length=500)
    citations: list[dict]


@app.get("/health")
def health():
    return {"status": "LexGuard is live"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    raw_name = file.filename or ""
    ext = "." + raw_name.rsplit(".", 1)[-1].lower() if "." in raw_name else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Solo se aceptan archivos PDF y DOCX.")

    data = await file.read()

    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="El archivo supera el límite de 1 MB.")

    try:
        text = extract_pdf(data) if ext == ".pdf" else extract_docx(data)
    except Exception:
        raise HTTPException(status_code=422, detail="No se pudo extraer el texto del archivo. Verifique que no esté dañado.")

    return {"filename": _sanitize_filename(raw_name), "text": text}


@app.post("/extract")
async def extract(req: ExtractRequest):
    try:
        citations = extract_citations(req.text[:MAX_TEXT_CHARS])
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno al extraer las citas.")

    return {"citations": citations}


@app.post("/investigate")
async def investigate(req: InvestigateRequest):
    try:
        results = await investigate_citations(req.citations)
    except Exception:
        raise HTTPException(status_code=500, detail="La verificación falló. Intente nuevamente.")

    return {"citations": results}


@app.post("/sessions")
async def create_session(req: SaveSessionRequest):
    try:
        session_id = save_session(req.document_name, req.user_note, req.citations)
    except Exception:
        raise HTTPException(status_code=500, detail="No se pudo guardar el informe. Intente nuevamente.")
    return {"session_id": session_id}


@app.get("/sessions/{session_id}")
async def read_session(session_id: str):
    try:
        session = get_session(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Error al cargar el informe. Intente nuevamente.")
    return session


@app.post("/judge")
async def judge(req: InvestigateRequest):
    try:
        results = judge_citations(req.citations)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno al evaluar las citas.")

    return {"citations": results}
