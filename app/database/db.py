"""Database helper for persisting resume screening runs and candidates into SQLite."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.schemas import CandidateProfile, JobProfile, ScoreBreakdown, ScreeningResult
from ..utils.config import BASE_DIR

DB_PATH = BASE_DIR / "output" / "screenings.db"


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize SQLite tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS screenings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            jd_path TEXT,
            created_at TEXT NOT NULL,
            total_candidates INTEGER DEFAULT 0,
            shortlisted_count INTEGER DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            rejected_count INTEGER DEFAULT 0,
            avg_score REAL DEFAULT 0.0,
            top_score REAL DEFAULT 0.0,
            job_data TEXT,
            similarity_backend TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            screening_id TEXT NOT NULL,
            rank INTEGER NOT NULL,
            name TEXT NOT NULL,
            score REAL NOT NULL,
            recommendation TEXT NOT NULL,
            confidence TEXT NOT NULL,
            source_file TEXT,
            result_json TEXT NOT NULL,
            FOREIGN KEY (screening_id) REFERENCES screenings (id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()
    conn.close()


def save_screening(
    screening_id: str,
    job: JobProfile,
    results: List[ScreeningResult],
    backend: str = "tfidf-cosine",
    jd_path: Optional[str] = None,
) -> None:
    """Save a completed screening run and candidates to SQLite."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    total = len(results)
    shortlisted = sum(1 for r in results if r.recommendation in ("STRONG SHORTLIST", "SHORTLIST"))
    review = sum(1 for r in results if r.recommendation == "REVIEW")
    rejected = sum(1 for r in results if r.recommendation == "REJECT")
    avg_s = sum(r.score for r in results) / total if total > 0 else 0.0
    top_s = max((r.score for r in results), default=0.0)

    cursor.execute(
        """
        INSERT OR REPLACE INTO screenings (
            id, title, jd_path, created_at, total_candidates,
            shortlisted_count, review_count, rejected_count,
            avg_score, top_score, job_data, similarity_backend
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            screening_id,
            job.title,
            jd_path or "",
            datetime.now().isoformat(timespec="seconds"),
            total,
            shortlisted,
            review,
            rejected,
            round(avg_s, 1),
            round(top_s, 1),
            json.dumps(job.model_dump(), ensure_ascii=False),
            backend,
        ),
    )

    # Clear existing candidates for this screening if replacing
    cursor.execute("DELETE FROM candidates WHERE screening_id = ?", (screening_id,))

    for result in results:
        cand_id = f"{screening_id}_{result.rank}_{hash(result.candidate)}"
        result_dict = {
            "candidate": result.candidate,
            "rank": result.rank,
            "score": result.score,
            "recommendation": result.recommendation,
            "confidence": result.confidence,
            "source_file": result.source_file,
            "breakdown": result.breakdown.model_dump(),
            "matched_required": result.matched_required,
            "missing_required": result.missing_required,
            "matched_preferred": result.matched_preferred,
            "missing_preferred": result.missing_preferred,
            "experience_years": result.experience_years,
            "required_experience": result.required_experience,
            "semantic_similarity": result.semantic_similarity,
            "skills": result.skills,
            "education": result.education,
            "strengths": result.strengths,
            "gaps": result.gaps,
            "reason": result.reason,
            "flags": result.flags,
        }

        cursor.execute(
            """
            INSERT INTO candidates (
                id, screening_id, rank, name, score, recommendation, confidence, source_file, result_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cand_id,
                screening_id,
                result.rank or 0,
                result.candidate,
                result.score,
                result.recommendation,
                result.confidence,
                result.source_file,
                json.dumps(result_dict, ensure_ascii=False),
            ),
        )

    conn.commit()
    conn.close()


def list_screenings() -> List[Dict[str, Any]]:
    """List all stored screenings ordered by created_at desc."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM screenings ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_screening(screening_id: str) -> Optional[Dict[str, Any]]:
    """Get screening details and candidate list."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM screenings WHERE id = ?", (screening_id,))
    s_row = cursor.fetchone()
    if not s_row:
        conn.close()
        return None

    screening = dict(s_row)
    if screening.get("job_data"):
        screening["job_data"] = json.loads(screening["job_data"])

    cursor.execute("SELECT * FROM candidates WHERE screening_id = ? ORDER BY rank ASC", (screening_id,))
    c_rows = cursor.fetchall()
    conn.close()

    candidates = []
    for crow in c_rows:
        cdict = dict(crow)
        cdict["result"] = json.loads(cdict["result_json"])
        del cdict["result_json"]
        candidates.append(cdict)

    screening["candidates"] = candidates
    return screening
