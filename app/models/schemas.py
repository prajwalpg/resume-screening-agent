"""Pydantic data models shared across the screening pipeline.

These schemas are the single source of truth for the data that flows
between pipeline stages:

    raw document text -> CandidateProfile / JobProfile -> ScreeningResult
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    """Structured information extracted from a single resume."""

    name: str = "Unknown"
    email: Optional[str] = None
    phone: Optional[str] = None

    skills: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    experience: List[str] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)

    # Pipeline metadata (never used for scoring)
    source_file: Optional[str] = None
    extraction_method: str = "heuristic"


class JobProfile(BaseModel):
    """Structured information extracted from a job description."""

    title: str = "Unknown Role"
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    minimum_experience: float = 0.0
    education: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    """Weighted score components (each value is in the 0.0 - 1.0 range)."""

    required_skills: float = 0.0
    experience: float = 0.0
    education: float = 0.0
    semantic_similarity: float = 0.0
    preferred_skills: float = 0.0


class ScreeningResult(BaseModel):
    """Everything the reports need to know about one candidate."""

    candidate: str = "Unknown"
    source_file: str = ""
    score: float = 0.0
    recommendation: str = "REVIEW"
    confidence: str = "LOW"

    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)

    matched_required: List[str] = Field(default_factory=list)
    missing_required: List[str] = Field(default_factory=list)
    matched_preferred: List[str] = Field(default_factory=list)
    missing_preferred: List[str] = Field(default_factory=list)

    experience_years: float = 0.0
    required_experience: float = 0.0
    semantic_similarity: float = 0.0

    skills: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    reason: str = ""
    flags: List[str] = Field(default_factory=list)

    rank: Optional[int] = None
