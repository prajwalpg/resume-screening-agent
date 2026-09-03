"""Job description extraction.

Strategy: LLM-first (strict JSON prompt), deterministic heuristic fallback
using section splitting + the shared skill taxonomy.
"""

import re
from typing import Dict, List, Optional

from ..models.schemas import JobProfile
from ..matching.skill_matcher import dedupe_related_skills, display_skill
from ..utils.llm_client import LLMClient
from ..utils.text_utils import (
    extract_education_fields,
    extract_minimum_experience,
    extract_skills_from_text,
    guess_job_title,
    section_bullet_lines,
    split_sections,
)

LLM_SYSTEM_PROMPT = """You are a job description parsing system.
Extract structured information from the job description text.
Return ONLY valid JSON with exactly these fields:
{"title": "", "required_skills": [], "preferred_skills": [], "minimum_experience": 0, "education": [], "responsibilities": []}

Rules:
1. Do not invent information.
2. required_skills = must-have skills. preferred_skills = nice-to-have skills.
3. minimum_experience must be a number of years (0 if not stated).
4. education should list required fields of study (e.g. "Computer Science").
5. Return valid JSON only. No markdown fences, no commentary."""

_REQUIRED_SECTION_KEYS = (
    "required skills",
    "must have",
    "requirements",
    "key skills",
    "skills",
    "technical skills",
    "qualifications",
)

_PREFERRED_SECTION_KEYS = (
    "preferred skills",
    "nice to have",
    "good to have",
    "bonus skills",
)

_EXPERIENCE_SECTION_KEYS = (
    "work experience",
    "professional experience",
    "experience",
    "employment history",
    "career history",
)


def _unique_extend(target: List[str], values: List[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


class JDExtractor:
    """Converts raw job description text into a JobProfile."""

    def __init__(self, llm: Optional[LLMClient] = None) -> None:
        self.llm = llm

    # ------------------------------------------------------------------
    def extract(self, text: str) -> JobProfile:
        profile = None
        if self.llm is not None:
            profile = self._extract_with_llm(text)
        if profile is None:
            profile = self._extract_with_heuristics(text)
        return profile

    # ------------------------------------------------------------------
    def _extract_with_llm(self, text: str) -> Optional[JobProfile]:
        data = self.llm.chat_json(LLM_SYSTEM_PROMPT, text[:12000])
        if not data:
            return None
        try:
            minimum_experience = float(data.get("minimum_experience") or 0)
            profile = JobProfile(
                title=str(data.get("title") or "").strip() or "Unknown Role",
                required_skills=[s.strip() for s in data.get("required_skills") or [] if str(s).strip()],
                preferred_skills=[s.strip() for s in data.get("preferred_skills") or [] if str(s).strip()],
                minimum_experience=max(0.0, min(minimum_experience, 30.0)),
                education=[str(e) for e in (data.get("education") or [])][:6],
                responsibilities=[str(r) for r in (data.get("responsibilities") or [])][:12],
            )
            if not profile.required_skills:
                return None
            return profile
        except Exception:
            return None

    # ------------------------------------------------------------------
    def _extract_with_heuristics(self, text: str) -> JobProfile:
        sections: Dict[str, str] = split_sections(text)
        title = guess_job_title(text)
        all_skills = extract_skills_from_text(text)

        preferred: List[str] = []
        for key in _PREFERRED_SECTION_KEYS:
            _unique_extend(preferred, extract_skills_from_text(sections.get(key, "")))

        required: List[str] = []
        for key in _REQUIRED_SECTION_KEYS:
            for skill in extract_skills_from_text(sections.get(key, "")):
                if skill not in required and skill not in preferred:
                    required.append(skill)
        # "Postman" mentioned inside an "API Testing" bullet is evidence of
        # the same requirement, not a separate one.
        required = dedupe_related_skills(required)
        if not required:
            required = dedupe_related_skills(
                [skill for skill in all_skills if skill not in preferred]
            )

        preferred = dedupe_related_skills(preferred)

        responsibilities: List[str] = []
        for key in ("responsibilities", "key responsibilities", "what you will do"):
            _unique_extend(responsibilities, section_bullet_lines(sections.get(key, ""), limit=12))

        return JobProfile(
            title=title,
            required_skills=[display_skill(skill) for skill in required],
            preferred_skills=[display_skill(skill) for skill in preferred],
            minimum_experience=extract_minimum_experience(text),
            education=extract_education_fields(text),
            responsibilities=responsibilities,
        )
