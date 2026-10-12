"""PaperLens preview API. Not a public production service without access control."""
import os
from pathlib import Path

import fitz
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from analyzer import analyze_pages, export_records
from validation import report

MAX_BYTES = 20 * 1024 * 1024
MAX_PAGES = 100

app = FastAPI(
    title="PaperLens MD API",
    version="0.1.0-preview",
    description="Evidence-first PDF Methods extraction. Findings are unverified candidates.",
)
origins = [
    origin.strip()
    for origin in os.getenv("PAPERLENS_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if origin.strip()
]
if "*" in origins:
    raise RuntimeError("Wildcard CORS origin is prohibited.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "paperlens-api", "schema_version": "1.0"}


@app.post("/api/v1/analyze")
async def analyze(file: UploadFile = File(...)):
    """Read one PDF with a strict byte/page bound; no app-level document saving."""
    if os.getenv("PAPERLENS_UPLOADS_ENABLED", "false").strip().lower() != "true":
        raise HTTPException(status_code=503, detail="PDF analysis is disabled on this deployment pending security review.")
    if Path(file.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(status_code=415, detail="Only .pdf files are supported.")
    chunks = []
    size = 0
    try:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_BYTES:
                raise HTTPException(status_code=413, detail="PDF exceeds the 20 MB preview limit.")
            chunks.append(chunk)
    finally:
        await file.close()
    raw = b"".join(chunks)
    if not raw.startswith(b"%PDF-"):
        raise HTTPException(status_code=422, detail="Invalid PDF file signature.")
    try:
        with fitz.open(stream=raw, filetype="pdf") as doc:
            if doc.needs_pass:
                raise HTTPException(status_code=422, detail="Password-protected PDF not supported.")
            if not 0 < len(doc) <= MAX_PAGES:
                raise HTTPException(status_code=422, detail="PDF page count outside preview limits.")
            pages = [page.get_text(sort=True) for page in doc]
    except HTTPException:
        raise
    except (fitz.FileDataError, ValueError, RuntimeError):
        raise HTTPException(status_code=422, detail="Malformed or unreadable PDF.") from None

    if not any(page.strip() for page in pages):
        raise HTTPException(status_code=422, detail="No selectable text found; OCR not implemented.")

    result = report(analyze_pages(pages), pages)
    candidates = []
    for i, row in enumerate(export_records(result["valid"])):
        candidates.append({
            "id": f"candidate-{i + 1}",
            "field": row["field"],
            "value": row["value"],
            "page": row["page"],
            "excerpt": row["excerpt"],
            "system_hint": None,
            "stage_hint": None,
            "grouping_status": "unassigned",
            "verification": "page_text_match_only",
        })
    held = [
        {"field": item.field, "value": item.value, "page": item.page,
         "reason": "Potentially ambiguous or negated context"}
        for item in result["context_review"]
    ]
    flags = [
        {"code": item.code, "level": item.level,
         "title": item.title, "explanation": item.explanation, "pages": list(item.pages)}
        for item in result["findings"]
    ]
    return {
        "schema_version": "1.0",
        "document": {"filename": Path(file.filename or "document.pdf").name, "pages": len(pages)},
        "method_candidates": candidates,
        "review_items": held,
        "scientific_flags": flags,
        "summary": {
            "candidate_count": len(candidates),
            "held_count": len(held),
            "rejected_count": len(result["rejected"]),
        },
        "disclaimer": (
            "Lexical candidates only. Multiple simulation protocols are NOT auto-grouped; "
            "page text matches do not prove a parameter was used. Verify main text and SI."
        ),
    }
