"""Resume information extraction.

Strategy: LLM-first (strict JSON prompt), deterministic heuristic fallback.
The heuristic path uses regex + a curated skill taxonomy so the agent is
fully runnable with no API keys, and so results stay reproducible.
"""

import re
from typing import List, Optional

from ..models.schemas import CandidateProfile
from ..matching.skill_matcher import display_skill
from ..utils.llm_client import LLMClient
from ..utils.text_utils import (
    EMAIL_RE,
    extract_certifications,
    extract_education_lines,
    extract_experience_years,
    extract_skills_from_text,
    find_email,
    find_phone,
    guess_name,
    section_bullet_lines,
    split_sections,
)

LLM_SYSTEM_PROMPT = """You are a resume information extraction system.
Extract structured information from the resume text.
Return ONLY valid JSON with exactly these fields:
{"name": "", "email": "", "phone": "", "skills": [], "education": [], "experience_years": 0, "experience": [], "projects": [], "certifications": []}

Rules:
1. Do not invent information.
2. Only extract information explicitly present in the resume.
3. If information is missing, use "", [] or 0.
4. Normalize skill names (e.g. "js" -> "JavaScript", "py.test" -> "Pytest").
5. experience_years must be a number (use 0 for freshers).
6. Return valid JSON only. No markdown fences, no commentary."""


def _to_float(value) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _string_list(values, limit: int) -> List[str]:
    result: List[str] = []
    for value in values or []:
        text = str(value).strip()
        if text and text not in result:
            result.append(text)
        if len(result) >= limit:
            break
    return result


class ResumeExtractor:
    """Converts raw resume text into a CandidateProfile."""

    def __init__(self, llm: Optional[LLMClient] = None) -> None:
        self.llm = llm

    # ------------------------------------------------------------------
    def extract(self, text: str, source_file: str = "") -> CandidateProfile:
        profile = None
        if self.llm is not None:
            profile = self._extract_with_llm(text)
        if profile is None:
            profile = self._extract_with_heuristics(text)
        profile.source_file = source_file or None
        return profile

    # ------------------------------------------------------------------
    def _extract_with_llm(self, text: str) -> Optional[CandidateProfile]:
        data = self.llm.chat_json(LLM_SYSTEM_PROMPT, text[:12000])
        if not data:
            return None
        try:
            experience_years = _to_float(data.get("experience_years")) or 0.0
            profile = CandidateProfile(
                name=str(data.get("name") or "").strip() or "Unknown",
                email=(str(data.get("email")).strip() if data.get("email") else None),
                phone=(str(data.get("phone")).strip() if data.get("phone") else None),
                skills=_string_list(data.get("skills"), 60),
                education=_string_list(data.get("education"), 10),
                experience_years=max(0.0, min(experience_years, 45.0)),
                experience=_string_list(data.get("experience"), 15),
                projects=_string_list(data.get("projects"), 15),
                certifications=_string_list(data.get("certifications"), 15),
                extraction_method="llm",
            )
            if profile.name == "Unknown":
                profile.name = guess_name(text)
            if not profile.skills:
                return None  # LLM clearly failed; use heuristics instead.
            return profile
        except Exception:
            return None

    # ------------------------------------------------------------------
    def _extract_with_heuristics(self, text: str) -> CandidateProfile:
        sections = split_sections(text)
        email = find_email(text)
        phone = find_phone(text)

        experience_section = ""
        for key in (
            "work experience",
            "professional experience",
            "experience",
            "employment history",
            "career history",
        ):
            if sections.get(key):
                experience_section = sections[key]
                break

        return CandidateProfile(
            name=guess_name(text),
            email=email,
            phone=phone,
            skills=[display_skill(skill) for skill in extract_skills_from_text(text)],
            education=extract_education_lines(text),
            experience_years=extract_experience_years(text, experience_section),
            experience=section_bullet_lines(experience_section, limit=8),
            projects=section_bullet_lines(sections.get("projects", ""), limit=8),
            certifications=extract_certifications(text),
            extraction_method="heuristic",
        )
