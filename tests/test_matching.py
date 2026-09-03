"""Tests for the matching engine: skill matching + semantic similarity."""

from app.matching.embeddings import SimilarityEngine
from app.matching.skill_matcher import dedupe_related_skills, display_skill, match_skills, normalize_skill


# ---------------------------------------------------------------------------
# Skill normalisation
# ---------------------------------------------------------------------------
def test_normalize_skill_aliases():
    assert normalize_skill("JS") == "javascript"
    assert normalize_skill("Py.test") == "pytest"
    assert normalize_skill("  Selenium   WebDriver ") == "selenium"


def test_display_skill():
    assert display_skill("api testing") == "API Testing"
    assert display_skill("sql") == "SQL"
    assert display_skill("javascript") == "JavaScript"


# ---------------------------------------------------------------------------
# Explicit skill matching (explainable, deterministic)
# ---------------------------------------------------------------------------
def test_skill_match_full_via_synonyms():
    # mysql/postman must give credit for SQL / API Testing requirements.
    result = match_skills(
        ["Python", "Selenium", "SQL", "Git", "API Testing"],
        ["python", "selenium", "mysql", "git", "postman"],
    )
    assert result.missing == []
    assert result.score == 1.0


def test_skill_match_partial():
    result = match_skills(["Python", "Jenkins"], ["Python", "Docker"])
    assert result.matched == ["Python"]
    assert result.missing == ["Jenkins"]
    assert result.score == 0.5


def test_skill_match_empty_required_is_neutral():
    result = match_skills([], ["Python"])
    assert result.score == 0.0
    assert result.matched == [] and result.missing == []


def test_dedupe_related_skills_keeps_first():
    assert dedupe_related_skills(["api testing", "postman", "sql"]) == ["api testing", "sql"]


# ---------------------------------------------------------------------------
# Semantic similarity (TF-IDF backend for offline determinism)
# ---------------------------------------------------------------------------
def test_semantic_similarity_range_and_ordering():
    engine = SimilarityEngine(prefer_transformers=False)  # force TF-IDF fallback
    jd = "Test automation engineer with Python, Selenium, API testing and SQL experience."
    related = "QA automation engineer skilled in Python, Selenium, pytest and API testing."
    unrelated = "Graphic designer specialised in logo design and brand identity."

    related_sim = engine.similarity(jd, related)
    unrelated_sim = engine.similarity(jd, unrelated)

    assert 0.0 <= related_sim <= 1.0
    assert 0.0 <= unrelated_sim <= 1.0
    assert related_sim > unrelated_sim


def test_batch_similarities_returns_one_score_per_resume():
    engine = SimilarityEngine(prefer_transformers=False)
    sims = engine.similarities(
        "Python automation engineer job description.",
        ["python selenium pytest resume", "graphic designer resume", ""],
    )
    assert len(sims) == 3
    assert all(0.0 <= s <= 1.0 for s in sims)
