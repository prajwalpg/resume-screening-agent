"""FastAPI web server exposing REST endpoints for the AI Resume Screening Agent."""

import json
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .agent.screening_agent import ScreeningAgent
from .database import db
from .models.schemas import JobProfile, ScreeningResult
from .utils.config import DEFAULT_JD_PATH, OUTPUT_DIR, RESUME_DIR, WEIGHTS

app = FastAPI(
    title="AI Resume Screening & Candidate Intelligence API",
    description="Backend API for AI candidate screening, semantic ranking, and explainable scoring.",
    version="1.0.0",
)

# Enable CORS for Next.js / Vite frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init database tables on startup
db.init_db()


class CompareRequest(BaseModel):
    candidates: List[Dict]


@app.get("/")
def root():
    return {
        "app": "AI Resume Screening & Candidate Intelligence API",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    agent = ScreeningAgent(use_llm=False)
    return {
        "status": "healthy",
        "similarity_backend": agent.similarity_engine.backend,
        "llm_available": agent.llm.is_available() if agent.llm else False,
        "weights": WEIGHTS,
    }


@app.get("/api/screenings")
def list_screenings():
    """List all previous screening runs."""
    return db.list_screenings()


@app.get("/api/screenings/{screening_id}")
def get_screening(screening_id: str):
    """Retrieve details and candidate rankings for a given screening ID."""
    data = db.get_screening(screening_id)
    if not data:
        raise HTTPException(status_code=404, detail="Screening run not found.")
    return data


@app.post("/api/screenings/demo")
def run_demo_screening():
    """Run an instant screening using bundled sample Job Description and 12 sample resumes."""
    screening_id = f"demo_{uuid.uuid4().hex[:8]}"

    if not DEFAULT_JD_PATH.exists():
        raise HTTPException(status_code=404, detail="Default sample Job Description not found.")
    if not RESUME_DIR.exists():
        raise HTTPException(status_code=404, detail="Sample resume directory not found.")

    agent = ScreeningAgent()
    results, job = agent.screen(DEFAULT_JD_PATH, RESUME_DIR)

    # Save to SQLite database
    db.save_screening(
        screening_id=screening_id,
        job=job,
        results=results,
        backend=agent.similarity_engine.backend,
        jd_path=str(DEFAULT_JD_PATH.name),
    )

    # Save file outputs
    agent.save_outputs(results, job)

    screening_data = db.get_screening(screening_id)
    return screening_data


@app.post("/api/screenings/upload")
async def run_custom_screening(
    jd_file: Optional[UploadFile] = File(None),
    resume_files: List[UploadFile] = File(...),
):
    """Upload custom Job Description and 1+ resumes to run screening."""
    if not resume_files:
        raise HTTPException(status_code=400, detail="At least one resume file must be uploaded.")

    screening_id = f"run_{uuid.uuid4().hex[:8]}"
    temp_dir = Path(tempfile.mkdtemp(prefix="resume_screener_"))

    try:
        # 1. Save JD file or use default
        if jd_file and jd_file.filename:
            jd_path = temp_dir / jd_file.filename
            content = await jd_file.read()
            jd_path.write_bytes(content)
        else:
            jd_path = DEFAULT_JD_PATH

        # 2. Save Resumes
        resumes_dir = temp_dir / "resumes"
        resumes_dir.mkdir(parents=True, exist_ok=True)

        for file in resume_files:
            if file.filename:
                res_path = resumes_dir / file.filename
                res_content = await file.read()
                res_path.write_bytes(res_content)

        # 3. Run Agent
        agent = ScreeningAgent()
        results, job = agent.screen(jd_path, resumes_dir)

        # 4. Save to DB
        db.save_screening(
            screening_id=screening_id,
            job=job,
            results=results,
            backend=agent.similarity_engine.backend,
            jd_path=jd_path.name,
        )

        screening_data = db.get_screening(screening_id)
        return screening_data

    finally:
        # Cleanup temporary files
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/api/screenings/{screening_id}/export/{format_type}")
def export_report(screening_id: str, format_type: str):
    """Download screening outputs (csv, json, or markdown report)."""
    format_type = format_type.lower()
    screening = db.get_screening(screening_id)
    if not screening:
        raise HTTPException(status_code=404, detail="Screening not found.")

    if format_type == "csv":
        file_path = OUTPUT_DIR / "ranked_candidates.csv"
        media_type = "text/csv"
        filename = f"{screening_id}_ranked_candidates.csv"
    elif format_type == "json":
        file_path = OUTPUT_DIR / "ranked_candidates.json"
        media_type = "application/json"
        filename = f"{screening_id}_ranked_candidates.json"
    elif format_type in ("md", "report", "markdown"):
        file_path = OUTPUT_DIR / "screening_report.md"
        media_type = "text/markdown"
        filename = f"{screening_id}_screening_report.md"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'csv', 'json', or 'report'.")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found. Re-run screening first.")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )


@app.post("/api/compare")
def compare_candidates(body: CompareRequest):
    """Compare 2 to 4 candidates side-by-side."""
    candidates = body.candidates
    if not candidates:
        return {"metrics": [], "candidates": []}

    metrics = [
        {"key": "score", "label": "Overall Score (%)"},
        {"key": "required_skills", "label": "Required Skills (%)"},
        {"key": "experience", "label": "Experience (%)"},
        {"key": "education", "label": "Education (%)"},
        {"key": "semantic_similarity", "label": "Semantic Similarity (%)"},
        {"key": "preferred_skills", "label": "Preferred Skills (%)"},
    ]

    processed = []
    for cand in candidates:
        res = cand.get("result", cand)
        bd = res.get("breakdown", {})
        processed.append(
            {
                "name": res.get("candidate", "Unknown"),
                "recommendation": res.get("recommendation", "N/A"),
                "score": res.get("score", 0.0),
                "required_skills": round(bd.get("required_skills", 0.0) * 100, 1),
                "experience": round(bd.get("experience", 0.0) * 100, 1),
                "education": round(bd.get("education", 0.0) * 100, 1),
                "semantic_similarity": round(bd.get("semantic_similarity", 0.0) * 100, 1),
                "preferred_skills": round(bd.get("preferred_skills", 0.0) * 100, 1),
                "missing_skills": res.get("missing_required", []),
                "matched_skills": res.get("matched_required", []),
                "experience_years": res.get("experience_years", 0.0),
            }
        )

    return {"metrics": metrics, "candidates": processed}
