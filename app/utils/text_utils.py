"""Shared text-processing helpers used by the heuristic extractors."""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .config import DEGREE_KEYWORDS, RELATED_FIELD_KEYWORDS, SKILL_ALIASES, SKILL_TAXONOMY

SECTION_HEADINGS = [
    # Resume headings
    "professional summary", "summary", "objective", "profile", "about me",
    "technical skills", "skills", "technologies", "tech stack",
    "work experience", "professional experience", "experience",
    "employment history", "career history",
    "projects", "key projects", "education", "academic background",
    "certifications", "certificates", "achievements", "awards",
    "interests", "hobbies", "additional information",
    # Job-description headings
    "responsibilities", "key responsibilities", "what you will do",
    "requirements", "required skills", "must have", "preferred skills",
    "nice to have", "good to have", "bonus skills", "qualifications",
    "minimum experience", "job description", "about the role",
    "about us", "overview", "description",
]

_HEADING_RE = re.compile(
    r"^\s*(?:" + "|".join(re.escape(h) for h in SECTION_HEADINGS) + r")\s*:?\s*$",
    re.IGNORECASE,
)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Ordered: most specific first. Only used for display, never for scoring.
PHONE_PATTERNS = [
    re.compile(r"(?:\+91[\s.-]?)?[6-9]\d{4}[\s.-]?\d{5}"),  # Indian mobile
    re.compile(r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"),  # US style
    re.compile(r"\+\d{1,3}[\s.-]?\d{6,12}"),  # international with '+'
]

YEARS_EXP_RE = re.compile(r"(\d{1,2}(?:\.\d)?)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE)

YEAR_RANGE_RE = re.compile(
    r"\b((?:19|20)\d{2})\s*(?:-|\u2013|\u2014|to)\s*((?:19|20)\d{2}|present|current|now|till\s+date)",
    re.IGNORECASE,
)

_TITLE_RE = re.compile(
    r"^\s*(?:job\s*title|role|position|title)\s*[:\-\u2013\u2014]\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)

_SKIP_NAME_WORDS = ("resume", "curriculum vitae", "curriculum", "vitae", "profile", "biodata")


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------
def split_sections(text: str) -> Dict[str, str]:
    """Split a resume / job description into {section_name: body}.

    Lines that consist solely of a known heading (optionally ending with a
    colon) start a new section; everything before the first heading is kept
    under the key "header".
    """
    sections: Dict[str, List[str]] = {}
    current = "header"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and _HEADING_RE.match(stripped):
            current = re.sub(r"\s*:\s*$", "", stripped).lower()
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {name: "\n".join(body).strip() for name, body in sections.items()}


# ---------------------------------------------------------------------------
# Contact details (display only -- excluded from scoring)
# ---------------------------------------------------------------------------
def find_email(text: str) -> Optional[str]:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def find_phone(text: str) -> Optional[str]:
    for pattern in PHONE_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(0).strip()
    return None


# ---------------------------------------------------------------------------
# Name detection
# ---------------------------------------------------------------------------
def guess_name(text: str) -> str:
    """Best-effort candidate name from the first lines of a resume."""
    for line in text.splitlines()[:10]:
        stripped = line.strip()
        if not stripped or len(stripped) > 60:
            continue
        lowered = stripped.lower()
        if EMAIL_RE.search(stripped) or any(p.search(stripped) for p in PHONE_PATTERNS):
            continue
        if any(word in lowered for word in _SKIP_NAME_WORDS):
            continue
        if _HEADING_RE.match(stripped) or "|" in stripped or "@" in stripped:
            continue
        words = re.findall(r"[A-Za-z][A-Za-z.'\-]*", stripped)
        single_letter_tokens = [w for w in words if len(w) == 1]
        if 2 <= len(words) <= 4 and len(single_letter_tokens) <= 1:
            return " ".join(w.capitalize().rstrip(".") for w in words)
    return "Unknown"


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------
def extract_skills_from_text(text: str) -> List[str]:
    """Find taxonomy skills in free text and return canonical names."""
    lowered = (text or "").lower()
    found: List[str] = []
    for skill in SKILL_TAXONOMY:
        pattern = r"(?<![a-z0-9+#.])" + re.escape(skill) + r"(?![a-z0-9+#])"
        if re.search(pattern, lowered):
            canonical = SKILL_ALIASES.get(skill, skill)
            if canonical not in found:
                found.append(canonical)
    return found


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------
def extract_education_lines(text: str) -> List[str]:
    """Return resume lines that look like education entries."""
    results: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) > 140:
            continue
        lowered = stripped.lower()
        if any(keyword in lowered for keyword in DEGREE_KEYWORDS):
            if stripped not in results:
                results.append(stripped)
    return results[:8]


def extract_education_fields(text: str) -> List[str]:
    """Return required fields of study mentioned in a job description."""
    lowered = (text or "").lower()
    fields: List[str] = []
    for field in RELATED_FIELD_KEYWORDS:
        if field in lowered and field.title() not in fields:
            fields.append(field.title())
    if fields:
        return fields[:4]
    if re.search(r"\b(bachelor|master|degree|b\.?tech|m\.?tech)\b", lowered):
        return ["Bachelor's degree"]
    return []


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------
def _union_years(spans: List[Tuple[int, int]]) -> float:
    """Total length of a set of year intervals, with overlaps merged."""
    if not spans:
        return 0.0
    spans = sorted(spans)
    total = 0.0
    current_start, current_end = spans[0]
    for start, end in spans[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            total += current_end - current_start
            current_start, current_end = start, end
    total += current_end - current_start
    return max(total, 0.0)


def extract_experience_years(text: str, experience_section: str = "") -> float:
    """Estimate total professional experience in years.

    Strategy:
    1. Explicit statements such as "3 years of experience" (whole document).
    2. Union of employment date ranges found in the *experience section*
       (education years are therefore never counted as work experience).
    The larger of the two estimates wins, capped at 45 years.
    """
    explicit = 0.0
    for line in text.splitlines():
        if "experience" not in line.lower():
            continue
        for match in YEARS_EXP_RE.finditer(line):
            try:
                value = float(match.group(1))
            except ValueError:
                continue
            if 0 < value <= 45:
                explicit = max(explicit, value)

    now_year = datetime.now().year
    spans: List[Tuple[int, int]] = []
    for match in YEAR_RANGE_RE.finditer(experience_section or ""):
        start = int(match.group(1))
        end_raw = match.group(2).lower()
        if end_raw in ("present", "current", "now", "till date"):
            end = now_year
        else:
            end = int(end_raw)
        end = min(end, now_year)
        if end >= start:
            spans.append((start, end))
    range_years = _union_years(spans)

    return round(min(max(explicit, range_years), 45.0), 1)


def extract_minimum_experience(text: str) -> float:
    """Extract the minimum experience requirement from a job description."""
    values: List[float] = []
    for line in text.splitlines():
        if "experience" not in line.lower():
            continue
        for match in YEARS_EXP_RE.finditer(line):
            try:
                value = float(match.group(1))
            except ValueError:
                continue
            if 0 <= value <= 30:
                values.append(value)
    return round(min(values), 1) if values else 0.0


# ---------------------------------------------------------------------------
# Section body helpers
# ---------------------------------------------------------------------------
def section_bullet_lines(body: str, limit: int = 8) -> List[str]:
    """Return cleaned bullet/paragraph lines from a section body."""
    lines: List[str] = []
    for line in (body or "").splitlines():
        stripped = line.strip().lstrip("-\u2022*").strip()
        if not stripped or _HEADING_RE.match(stripped):
            continue
        if len(stripped) > 180:
            stripped = stripped[:177] + "..."
        if stripped not in lines:
            lines.append(stripped)
        if len(lines) >= limit:
            break
    return lines


def extract_certifications(text: str) -> List[str]:
    """Return lines that look like certifications."""
    results: List[str] = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("-\u2022*").strip()
        if not stripped or len(stripped) > 140:
            continue
        if "certif" in stripped.lower():
            if stripped not in results:
                results.append(stripped)
    return results[:6]


# ---------------------------------------------------------------------------
# Job title
# ---------------------------------------------------------------------------
def guess_job_title(text: str) -> str:
    """Extract the job title from a job description."""
    match = _TITLE_RE.search(text or "")
    if match:
        return match.group(1).strip()[:100]
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _HEADING_RE.match(stripped):
            continue
        if EMAIL_RE.search(stripped):
            continue
        return stripped[:100]
    return "Unknown Role"
