import os
import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .tailor import tailor_resume

try:
    from .cover_letter import generate_cover_letter
    HAS_COVER_LETTER = True
except ImportError:
    HAS_COVER_LETTER = False

try:
    from .ats_score import compute_ats_score
    HAS_ATS_SCORE = True
except ImportError:
    HAS_ATS_SCORE = False

logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Tailor", description="AI-powered resume tailoring")

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "has_cover_letter": HAS_COVER_LETTER,
        "has_ats_score": HAS_ATS_SCORE,
    })


@app.post("/api/tailor")
async def api_tailor(
    resume: str = Form(...),
    job_description: str = Form(...),
    include_cover_letter: bool = Form(False),
    include_ats_score: bool = Form(False),
):
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")

    result = await asyncio.to_thread(tailor_resume, resume, job_description, model)

    response = {
        "tailored_resume": result["tailored_resume"],
        "changes": result["changes"],
        "usage": result["usage"],
    }

    if include_cover_letter and HAS_COVER_LETTER:
        cl_result = await asyncio.to_thread(generate_cover_letter, resume, job_description, model)
        response["cover_letter"] = cl_result["cover_letter"]

    if include_ats_score and HAS_ATS_SCORE:
        before = compute_ats_score(resume, job_description)
        after = compute_ats_score(result["tailored_resume"], job_description)
        response["ats_score"] = {
            "before": before,
            "after": after,
            "improvement": round(after["score"] - before["score"], 1),
        }

    return JSONResponse(response)


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".pdf"):
        try:
            import fitz
            doc = fitz.open(stream=content, filetype="pdf")
            pages = []
            for page in doc:
                text = page.get_text()
                if text.strip():
                    pages.append(text.strip())
            doc.close()
            if not pages:
                return JSONResponse(
                    {"error": "Could not extract text from PDF. It may be a scanned image."},
                    status_code=400,
                )
            return JSONResponse({"text": "\n\n".join(pages)})
        except Exception:
            return JSONResponse({"error": "Failed to read PDF file."}, status_code=400)

    if filename.endswith((".txt", ".md")):
        try:
            return JSONResponse({"text": content.decode("utf-8")})
        except UnicodeDecodeError:
            return JSONResponse({"error": "File is not valid UTF-8 text."}, status_code=400)

    return JSONResponse(
        {"error": "Unsupported file type. Use .txt, .md, or .pdf"},
        status_code=400,
    )
