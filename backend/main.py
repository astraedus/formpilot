import os
import uuid
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database import init_db, save_analysis, get_analysis, list_analyses
from form_analyzer import analyze_form
from models import AnalysisResult, AnalysisListItem, FieldAnalysis

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_FILE_SIZE_MB = 10


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialised")
    yield


app = FastAPI(
    title="FormPilot API",
    description="Smart form navigator powered by Gemini Vision",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images statically
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


def _validate_image(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )


@app.post("/api/analyze", response_model=AnalysisResult, status_code=201)
async def analyze(
    file: UploadFile = File(..., description="Screenshot of the form to analyze"),
    user_context: str = Form(
        default="",
        description="Describe yourself and what you are filling this form for",
    ),
):
    """Upload a form screenshot and receive field-by-field fill instructions."""
    _validate_image(file)

    # Read file bytes and enforce size limit
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size is {MAX_FILE_SIZE_MB}MB",
        )

    # Save upload with unique filename
    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    image_path = UPLOAD_DIR / filename
    image_path.write_bytes(content)

    logger.info(f"Saved upload: {image_path} ({len(content)} bytes)")

    # Run Gemini Vision analysis
    fields_data, summary, is_mock = await analyze_form(str(image_path), user_context)

    # Persist to DB
    analysis_id = await save_analysis(
        image_path=str(image_path),
        user_context=user_context,
        fields=fields_data,
        summary=summary,
        is_mock=is_mock,
    )

    # Fetch and return
    record = await get_analysis(analysis_id)
    return AnalysisResult(
        id=record["id"],
        image_path=f"/uploads/{filename}",
        user_context=record["user_context"],
        fields=[FieldAnalysis(**f) for f in record["fields"]],
        summary=record["summary"],
        created_at=record["created_at"],
        is_mock=record["is_mock"],
    )


@app.get("/api/analyses", response_model=list[AnalysisListItem])
async def list_all_analyses(limit: int = 50, offset: int = 0):
    """List past form analyses, newest first."""
    if limit > 200:
        limit = 200
    rows = await list_analyses(limit=limit, offset=offset)
    return [
        AnalysisListItem(
            id=r["id"],
            user_context=r["user_context"],
            field_count=r["field_count"],
            created_at=r["created_at"],
            thumbnail_path=f"/uploads/{Path(r['thumbnail_path']).name}" if r.get("thumbnail_path") else None,
        )
        for r in rows
    ]


@app.get("/api/analyses/{analysis_id}", response_model=AnalysisResult)
async def get_single_analysis(analysis_id: int):
    """Retrieve a specific form analysis by ID."""
    record = await get_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
    filename = Path(record["image_path"]).name
    return AnalysisResult(
        id=record["id"],
        image_path=f"/uploads/{filename}",
        user_context=record["user_context"],
        fields=[FieldAnalysis(**f) for f in record["fields"]],
        summary=record["summary"],
        created_at=record["created_at"],
        is_mock=record["is_mock"],
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "formpilot-api"}
