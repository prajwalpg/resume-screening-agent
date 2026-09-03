"""Tests for the weighted scoring engine and recommendation thresholds."""

from app.matching.scoring import (
    confidence,
    education_score,
    experience_score,
    final_score,
    recommendation,
)
from app.models.schemas import ScoreBreakdown


def make_breakdown(rs=1.0, exp=1.0, edu=1.0, sem=0.9, pref=1.0) -> ScoreBreakdown:
    return ScoreBreakdown(
        required_skills=rs,
        experience=exp,
        education=edu,
        semantic_similarity=sem,
        preferred_skills=pref,
    )


# ---------------------------------------------------------------------------
# Recommendation bands (guide: 91.4 -> STRONG SHORTLIST, 83.2 -> SHORTLIST,
# 68.5 -> REVIEW, 42.3 -> REJECT)
# ---------------------------------------------------------------------------
def test_recommendation_bands():
    assert recommendation(91.4) == "STRONG SHORTLIST"
    assert recommendation(83.2) == "SHORTLIST"
    assert recommendation(68.5) == "REVIEW"
    assert recommendation(42.3) == "REJECT"


def test_recommendation_boundaries():
    assert recommendation(85.0) == "STRONG SHORTLIST"
    assert recommendation(84.9) == "SHORTLIST"
    assert recommendation(70.0) == "SHORTLIST"
    assert recommendation(69.9) == "REVIEW"
    assert recommendation(55.0) == "REVIEW"
    assert recommendation(54.9) == "REJECT"


# ---------------------------------------------------------------------------
# Experience score
# ---------------------------------------------------------------------------
def test_experience_score_caps_at_one():
    assert experience_score(2.5, 2) == 1.0
    assert experience_score(10, 1) == 1.0


def test_experience_score_proportional():
    assert experience_score(1.0, 2) == 0.5
    assert experience_score(0.5, 1) == 0.5


def test_experience_score_edge_cases():
    assert experience_score(3.0, 0) == 1.0  # no requirement -> full credit
    assert experience_score(0, 2) == 0.0    # no experience -> zero


# ---------------------------------------------------------------------------
# Education score
# ---------------------------------------------------------------------------
def test_education_field_match():
    assert education_score(["Computer Science"], ["B.Tech in Computer Science"]) == 1.0
    # The JD itself accepts IT as a related field
    assert education_score(
        ["Computer Science", "Information Technology"], ["B.E. in Information Technology"]
    ) == 1.0


def test_education_neutral_when_missing():
    assert education_score(["Computer Science"], []) == 0.5


def test_education_unrelated_degree_partial_credit():
    assert education_score(["Computer Science"], ["B.Tech in Electronics"]) == 0.6


# ---------------------------------------------------------------------------
# Final score math (guide example: 89.4)
# ---------------------------------------------------------------------------
def test_weighted_math_matches_guide_example():
    breakdown = make_breakdown(rs=0.9, exp=1.0, edu=1.0, sem=0.84, pref=0.5)
    assert final_score(breakdown) == 89.4


# ---------------------------------------------------------------------------
# Test 1: perfect candidate -> > 85%, STRONG SHORTLIST
# ---------------------------------------------------------------------------
def test_perfect_candidate_is_strong_shortlist():
    score = final_score(make_breakdown())
    assert score > 85
    assert recommendation(score) == "STRONG SHORTLIST"


# ---------------------------------------------------------------------------
# Test 2: good candidate -> 70-85%, SHORTLIST
# ---------------------------------------------------------------------------
def test_good_candidate_is_shortlist():
    score = final_score(make_breakdown(rs=0.8, exp=1.0, edu=1.0, sem=0.6, pref=0.5))
    assert 70 <= score < 85
    assert recommendation(score) == "SHORTLIST"


# ---------------------------------------------------------------------------
# Test 3: weak candidate -> < 55%, REJECT
# ---------------------------------------------------------------------------
def test_weak_candidate_is_rejected():
    score = final_score(make_breakdown(rs=0.2, exp=0.0, edu=0.5, sem=0.2, pref=0.0))
    assert score < 55
    assert recommendation(score) == "REJECT"


# ---------------------------------------------------------------------------
# Test 4: candidate with no experience scores experience = 0
# ---------------------------------------------------------------------------
def test_no_experience_scores_zero_experience_component():
    assert experience_score(0.0, 1.0) == 0.0


# ---------------------------------------------------------------------------
# Confidence levels
# ---------------------------------------------------------------------------
def test_confidence_levels():
    assert confidence(90.0, 0.8, 5, 5) == "HIGH"
    assert confidence(70.0, 0.5, 3, 5) == "MEDIUM"
    assert confidence(40.0, 0.2, 1, 5) == "LOW"
