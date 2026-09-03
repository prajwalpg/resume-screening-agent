"""Matching package: embeddings, skill matching and weighted scoring."""

from .embeddings import SimilarityEngine
from .scoring import confidence, education_score, experience_score, final_score, recommendation
from .skill_matcher import SkillMatch, display_skill, match_skills, normalize_skill

__all__ = [
    "SimilarityEngine",
    "SkillMatch",
    "match_skills",
    "normalize_skill",
    "display_skill",
    "experience_score",
    "education_score",
    "final_score",
    "recommendation",
    "confidence",
]
