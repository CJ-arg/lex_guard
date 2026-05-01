from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.services.extractor import extract_docx, extract_pdf

app = FastAPI(title="LexGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before production
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 1 * 1024 * 1024  # 1 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


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
