"""The weighted scoring engine -- the deterministic heart of the agent.

FINAL SCORE
    = Required Skill Match x 40%
    + Experience Match     x 25%
    + Education Match      x 15%
    + Semantic Similarity  x 10%
    + Preferred Skills     x 10%

The LLM never changes these numbers; it only explains them.
"""

from typing import List

from ..models.schemas import ScoreBreakdown
from ..utils.config import DEGREE_KEYWORDS, RELATED_FIELD_KEYWORDS, RECOMMENDATION_THRESHOLDS, WEIGHTS


# ---------------------------------------------------------------------------
# Component scores (all return values in the 0.0 - 1.0 range)
# ---------------------------------------------------------------------------
def experience_score(candidate_years: float, required_years: float) -> float:
    """Proportional credit, capped at 1.0 (exceeding the bar adds no more)."""
    if required_years <= 0:
        return 1.0
    if candidate_years <= 0:
        return 0.0
    return min(candidate_years / required_years, 1.0)


def education_score(required_education: List[str], candidate_education: List[str]) -> float:
    """Field-of-study match with a neutral default when data is missing."""
    if not required_education:
        return 1.0

    required_text = " ".join(required_education).lower()
    candidate_text = " ".join(candidate_education).lower()

    if not candidate_text.strip():
        return 0.5  # Neutral: resume contains no education information.

    for keyword in RELATED_FIELD_KEYWORDS:
        if keyword in required_text and keyword in candidate_text:
            return 1.0

    # No field match: partial credit for holding any relevant degree.
    if any(degree in candidate_text for degree in DEGREE_KEYWORDS):
        return 0.6
    return 0.5


# ---------------------------------------------------------------------------
# Final score, recommendation, confidence
# ---------------------------------------------------------------------------
def final_score(breakdown: ScoreBreakdown) -> float:
    """Weighted sum on a 0-100 scale, rounded to one decimal."""
    total = (
        breakdown.required_skills * WEIGHTS["required_skills"]
        + breakdown.experience * WEIGHTS["experience"]
        + breakdown.education * WEIGHTS["education"]
        + breakdown.semantic_similarity * WEIGHTS["semantic_similarity"]
        + breakdown.preferred_skills * WEIGHTS["preferred_skills"]
    )
    return round(total * 100.0, 1)


def recommendation(score: float) -> str:
    for threshold, label in RECOMMENDATION_THRESHOLDS:
        if score >= threshold:
            return label
    return "REJECT"


def confidence(
    score: float,
    semantic_similarity: float,
    matched_required: int,
    total_required: int,
) -> str:
    """How much we trust this verdict (extraction quality + signal agreement)."""
    match_ratio = (matched_required / total_required) if total_required else 0.0
    if score >= 85 and (semantic_similarity >= 0.75 or match_ratio >= 0.8):
        return "HIGH"
    if score >= 60:
        return "MEDIUM"
    return "LOW"
