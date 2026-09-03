"""Deterministic, explainable skill matching.

Matching is done in three passes so that equivalent skills get credit
without inventing matches:

1. Canonical normalisation (lowercase + alias map, e.g. "JS" -> "javascript").
2. Synonym groups (e.g. "Postman" / "Rest Assured" count as API-testing evidence).
3. Substring containment for multi-word skills (e.g. required "API Testing"
   matches candidate skill "API Testing and Automation").
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

from ..utils.config import SKILL_ALIASES, SYNONYM_GROUPS


def normalize_skill(skill: str) -> str:
    """Lowercase, collapse whitespace and resolve known aliases."""
    normalized = re.sub(r"\s+", " ", str(skill).strip().lower())
    return SKILL_ALIASES.get(normalized, normalized)


# canonical skill -> set of canonical skills it is interchangeable with
_SYNONYM_LOOKUP: Dict[str, Set[str]] = {}
for _group in SYNONYM_GROUPS:
    _canonical_group = {normalize_skill(skill) for skill in _group}
    for _skill in _canonical_group:
        _SYNONYM_LOOKUP.setdefault(_skill, set()).update(_canonical_group)


@dataclass
class SkillMatch:
    """Result of matching one skill list against another."""

    score: float = 0.0
    matched: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)


def _skill_hits(canonical: str, candidate_set: Set[str], candidate_strings: List[str]) -> bool:
    if canonical in candidate_set:
        return True

    group = _SYNONYM_LOOKUP.get(canonical)
    if group and group & candidate_set:
        return True

    if len(canonical) >= 4:  # Avoid accidental substring hits on tiny tokens.
        for candidate in candidate_strings:
            if canonical in candidate or candidate in canonical:
                return True
    return False


# canonical skill -> skill -> human-friendly display name
_DISPLAY_OVERRIDES = {
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "github": "GitHub",
    "gitlab": "GitLab",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "fastapi": "FastAPI",
    "graphql": "GraphQL",
    ".net": ".NET",
    "node.js": "Node.js",
    "vue.js": "Vue.js",
    "next.js": "Next.js",
    "express.js": "Express.js",
}

_ACRONYM_WORDS = {
    "api", "sql", "html", "css", "ci", "cd", "aws", "gcp", "nlp", "oop",
    "tdd", "bdd", "uat", "etl", "ec2", "s3", "php", "ui", "ux", "qa",
    "sdet", "istqb",
}


def display_skill(skill: str) -> str:
    """Human-friendly casing for report output ("api testing" -> "API Testing")."""
    canonical = normalize_skill(skill)
    if canonical in _DISPLAY_OVERRIDES:
        return _DISPLAY_OVERRIDES[canonical]
    parts = re.split(r"(\s+|/|-)", canonical)
    rendered = []
    for part in parts:
        if part.lower() in _ACRONYM_WORDS:
            rendered.append(part.upper())
        else:
            rendered.append(part.capitalize())
    return "".join(rendered)


def dedupe_related_skills(skills: List[str]) -> List[str]:
    """Drop later skills that are synonyms/relations of an earlier one.

    Used by the JD extractor: if a requirements section lists both
    "API Testing" and "Postman", the postman mention is just evidence for
    the API-testing requirement, not a separate requirement.
    """
    kept: List[str] = []
    kept_canonical: Set[str] = set()
    for skill in skills:
        canonical = normalize_skill(skill)
        group = _SYNONYM_LOOKUP.get(canonical, {canonical})
        if group & kept_canonical:
            continue
        kept.append(skill)
        kept_canonical.add(canonical)
    return kept


def match_skills(required_skills: List[str], candidate_skills: List[str]) -> SkillMatch:
    """Return (score, matched, missing) for the required-skill list.

    `matched` / `missing` keep the *original* casing of the required skill
    so reports can show "API Testing" exactly as the JD worded it.
    """
    if not required_skills:
        return SkillMatch()

    candidate_canonical_set = {normalize_skill(skill) for skill in candidate_skills}
    candidate_canonical_list = [normalize_skill(skill) for skill in candidate_skills]

    matched: List[str] = []
    missing: List[str] = []
    for required in required_skills:
        canonical = normalize_skill(required)
        if _skill_hits(canonical, candidate_canonical_set, candidate_canonical_list):
            matched.append(str(required).strip())
        else:
            missing.append(str(required).strip())

    score = round(len(matched) / len(required_skills), 4)
    return SkillMatch(score=score, matched=matched, missing=missing)
