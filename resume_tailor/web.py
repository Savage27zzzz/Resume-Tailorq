import os
import asyncio
import logging
import time
from collections import defaultdict
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory rate limiter
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = int(os.environ.get("RATE_LIMIT_PER_HOUR", "20"))


def _check_rate_limit(client_ip: str) -> bool:
    """Return True if the client is within rate limits."""
    now = time.time()
    window = 3600  # 1 hour
    # Clean old entries
    _rate_limit_store[client_ip] = [
        t for t in _rate_limit_store[client_ip] if now - t < window
    ]
    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT:
        return False
    _rate_limit_store[client_ip].append(now)
    return True


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
    request: Request,
    resume: str = Form(...),
    job_description: str = Form(...),
    include_cover_letter: bool = Form(False),
    include_ats_score: bool = Form(False),
):
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        return JSONResponse(
            {"error": "Rate limit exceeded. Please try again later."},
            status_code=429,
        )

    model = os.environ.get("OPENAI_MODEL", "gpt-4o")

    try:
        result = await asyncio.to_thread(tailor_resume, resume, job_description, model)
    except RuntimeError as exc:
        return JSONResponse({"error": str(exc)}, status_code=502)
    except Exception:
        logger.exception("Unexpected error during tailoring")
        return JSONResponse({"error": "Something went wrong. Please try again."}, status_code=500)

    response = {
        "tailored_resume": result["tailored_resume"],
        "changes": result["changes"],
        "usage": result["usage"],
    }

    if include_cover_letter and HAS_COVER_LETTER:
        try:
            cl_result = await asyncio.to_thread(generate_cover_letter, resume, job_description, model)
            response["cover_letter"] = cl_result["cover_letter"]
        except Exception:
            logger.exception("Cover letter generation failed")
            response["cover_letter_error"] = "Cover letter generation failed."

    if include_ats_score and HAS_ATS_SCORE:
        before = compute_ats_score(resume, job_description)
        after = compute_ats_score(result["tailored_resume"], job_description)
        response["ats_score"] = {
            "before": before,
            "after": after,
            "improvement": round(after["score"] - before["score"], 1),
        }

    return JSONResponse(response)


@app.post("/api/export")
async def api_export(
    content: str = Form(...),
    format: str = Form("pdf"),
):
    from .export import markdown_to_pdf, markdown_to_docx
    from fastapi.responses import Response

    if format == "docx":
        file_bytes = markdown_to_docx(content)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = "tailored_resume.docx"
    else:
        file_bytes = markdown_to_pdf(content)
        media_type = "application/pdf"
        filename = "tailored_resume.pdf"

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...)):
    content = await file.read()

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    if len(content) > MAX_FILE_SIZE:
        return JSONResponse({"error": "File too large. Maximum size is 10 MB."}, status_code=400)

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
