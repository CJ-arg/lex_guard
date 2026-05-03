from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from app.services.agent_extractor import extract_citations
from app.services.investigator import investigate_citations
from app.services.agent_judge import judge_citations
from app.services.extractor import extract_docx, extract_pdf
from app.services.sessions import get_session, save_session

app = FastAPI(title="LexGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before production
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 1 * 1024 * 1024  # 1 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


class ExtractRequest(BaseModel):
    text: str


class InvestigateRequest(BaseModel):
    citations: list[dict]


class SaveSessionRequest(BaseModel):
    document_name: str
    user_note: str | None = None
    citations: list[dict]


@app.get("/health")
def health():
    return {"status": "LexGuard is live"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Only PDF and DOCX files are accepted.")

    data = await file.read()

    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 1 MB size limit.")

    try:
        text = extract_pdf(data) if ext == ".pdf" else extract_docx(data)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Text extraction failed: {exc}")

    return {"filename": filename, "text": text}


@app.post("/extract")
async def extract(req: ExtractRequest):
    try:
        citations = extract_citations(req.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {exc}")

    return {"citations": citations}


@app.post("/investigate")
async def investigate(req: InvestigateRequest):
    try:
        results = investigate_citations(req.citations)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Investigation failed: {exc}")

    return {"citations": results}


@app.post("/sessions")
async def create_session(req: SaveSessionRequest):
    try:
        session_id = save_session(req.document_name, req.user_note, req.citations)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not save session: {exc}")
    return {"session_id": session_id}


@app.get("/sessions/{session_id}")
async def read_session(session_id: str):
    try:
        session = get_session(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not retrieve session: {exc}")
    return session


@app.post("/judge")
async def judge(req: InvestigateRequest):
    try:
        results = judge_citations(req.citations)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Judge failed: {exc}")

    return {"citations": results}
