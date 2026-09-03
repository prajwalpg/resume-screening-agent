"""End-to-end screening agent.

Orchestrates: JD parsing -> batch resume parsing/extraction -> semantic
similarity -> deterministic weighted scoring -> ranking -> explanations
(LLM or template) -> CSV / JSON / Markdown reports.

Design principle: the LLM NEVER decides scores. Deterministic scoring keeps
the ranking reproducible and auditable; the LLM (when configured) only
extracts structured data and writes natural-language explanations.
"""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from ..extraction.jd_extractor import JDExtractor
from ..extraction.resume_extractor import ResumeExtractor
from ..matching.embeddings import SimilarityEngine
from ..matching.scoring import (
    confidence,
    education_score,
    experience_score,
    final_score,
    recommendation,
)
from ..matching.skill_matcher import match_skills
from ..models.schemas import CandidateProfile, JobProfile, ScoreBreakdown, ScreeningResult
from ..parser import extract_text, is_supported
from ..utils.config import OUTPUT_DIR, WEIGHTS
from ..utils.llm_client import LLMClient
from ..utils.text_utils import EMAIL_RE, PHONE_PATTERNS

BIAS_NOTE = (
    "Protected and personal attributes (gender, age, photograph, religion, caste, "
    "marital status, address) are excluded from all scoring and ranking logic. "
    "Contact details are stripped before semantic analysis."
)

_PROTECTED_LINE_KEYWORDS = (
    "marital status",
    "date of birth",
    "gender",
    "religion",
    "caste",
    "nationality",
)


# ---------------------------------------------------------------------------
# Bias protection helpers
# ---------------------------------------------------------------------------
def scrub_for_scoring(text: str) -> str:
    """Remove contact details and protected-attribute lines before scoring."""
    scrubbed = EMAIL_RE.sub(" ", text or "")
    for pattern in PHONE_PATTERNS:
        scrubbed = pattern.sub(" ", scrubbed)
    kept_lines = []
    for line in scrubbed.splitlines():
        lowered = line.lower()
        if any(keyword in lowered for keyword in _PROTECTED_LINE_KEYWORDS):
            continue
        kept_lines.append(line)
    return "\n".join(kept_lines)


class ScreeningAgent:
    """The full resume-screening pipeline."""

    def __init__(
        self,
        use_llm: bool = True,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.llm = LLMClient() if use_llm else None
        self.jd_extractor = JDExtractor(self.llm)
        self.resume_extractor = ResumeExtractor(self.llm)
        self.similarity_engine = SimilarityEngine()
        self._progress: Callable[[str], None] = progress_callback or (lambda message: None)

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------
    def screen(self, jd_path, resume_dir) -> Tuple[List[ScreeningResult], JobProfile]:
        jd_path = Path(jd_path)
        resume_dir = Path(resume_dir)

        self._progress("Parsing job description...")
        jd_text = extract_text(jd_path)
        job = self.jd_extractor.extract(scrub_for_scoring(jd_text))
        self._progress(f"Job profile: {job.title}")
        if job.required_skills:
            self._progress(f"Required skills: {', '.join(job.required_skills)}")
        if job.preferred_skills:
            self._progress(f"Preferred skills: {', '.join(job.preferred_skills)}")
        self._progress(
            f"Minimum experience: {job.minimum_experience:g} yr | Education: {', '.join(job.education) or 'any'}"
        )
        self._progress("")

        resume_files = [
            path
            for path in sorted(resume_dir.iterdir())
            if path.is_file() and is_supported(path)
        ]
        if not resume_files:
            raise RuntimeError(
                f"No supported resume files (PDF / DOCX / TXT) found in: {resume_dir}"
            )

        profiles: List[CandidateProfile] = []
        texts: List[str] = []
        failures: List[str] = []
        for index, path in enumerate(resume_files, start=1):
            try:
                text = extract_text(path)
                profile = self.resume_extractor.extract(text, source_file=path.name)
            except Exception as exc:
                failures.append(path.name)
                self._progress(
                    f"[{index}/{len(resume_files)}] {path.name} FAILED -> {exc.__class__.__name__}: {exc}"
                )
                continue
            profiles.append(profile)
            texts.append(scrub_for_scoring(text))
            self._progress(
                f"[{index}/{len(resume_files)}] {path.name} \u2713 -> {profile.name} "
                f"({profile.extraction_method})"
            )

        self._progress("")
        self._progress("Calculating semantic similarity...")
        similarities = self.similarity_engine.similarities(
            scrub_for_scoring(jd_text), texts
        )
        self._progress(f"Similarity backend: {self.similarity_engine.backend}")

        self._progress("Scoring candidates...")
        results: List[ScreeningResult] = []
        seen_hashes: Dict[str, str] = {}
        for profile, text, similarity in zip(profiles, texts, similarities):
            result = self._score_candidate(profile, job, similarity)

            digest = hashlib.md5(
                re.sub(r"\s+", " ", text.lower()).strip().encode("utf-8")
            ).hexdigest()
            if digest in seen_hashes:
                result.flags.append(f"possible duplicate of {seen_hashes[digest]}")
            else:
                seen_hashes[digest] = profile.source_file or profile.name
            results.append(result)

        if failures:
            self._progress(f"! {len(failures)} file(s) could not be parsed: {', '.join(failures)}")

        # Ranking: score descending, name as a stable tie-breaker.
        results.sort(key=lambda r: (-r.score, r.candidate.lower()))
        for rank, result in enumerate(results, start=1):
            result.rank = rank

        self._progress("Generating explanations...")
        for result in results:
            explained = None
            if self.llm is not None and self.llm.is_available():
                explained = self._llm_explanation(result, job)
            if explained is not None:
                result.strengths, result.gaps, result.reason = explained
            else:
                result.strengths, result.gaps, result.reason = self._template_explanation(
                    result, job
                )

        return results, job

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------
    def _score_candidate(
        self, profile: CandidateProfile, job: JobProfile, semantic_similarity: float
    ) -> ScreeningResult:
        required_match = match_skills(job.required_skills, profile.skills)
        preferred_match = match_skills(job.preferred_skills, profile.skills)

        breakdown = ScoreBreakdown(
            required_skills=required_match.score,
            experience=experience_score(profile.experience_years, job.minimum_experience),
            education=education_score(job.education, profile.education),
            semantic_similarity=max(0.0, min(1.0, float(semantic_similarity))),
            preferred_skills=preferred_match.score,
        )
        score = final_score(breakdown)

        return ScreeningResult(
            candidate=profile.name,
            source_file=profile.source_file or "",
            score=score,
            recommendation=recommendation(score),
            confidence=confidence(
                score,
                breakdown.semantic_similarity,
                len(required_match.matched),
                len(job.required_skills),
            ),
            breakdown=breakdown,
            matched_required=required_match.matched,
            missing_required=required_match.missing,
            matched_preferred=preferred_match.matched,
            missing_preferred=preferred_match.missing,
            experience_years=profile.experience_years,
            required_experience=job.minimum_experience,
            education=profile.education[:10],
            semantic_similarity=breakdown.semantic_similarity,
            skills=profile.skills[:30],
        )

    # ------------------------------------------------------------------
    # Explanations
    # ------------------------------------------------------------------
    def _template_explanation(
        self, result: ScreeningResult, job: JobProfile
    ) -> Tuple[List[str], List[str], str]:
        """Deterministic explanation used when no LLM is configured."""
        strengths: List[str] = []
        gaps: List[str] = []
        total_required = max(len(job.required_skills), 1)
        matched_count = len(result.matched_required)

        if matched_count:
            strengths.append(
                f"Matches {matched_count}/{total_required} required skills "
                f"({', '.join(result.matched_required[:6])})."
            )
        if job.minimum_experience > 0 and result.experience_years >= job.minimum_experience:
            strengths.append(
                f"Meets the experience bar ({result.experience_years:g} yrs vs "
                f"{job.minimum_experience:g}+ required)."
            )
        if result.breakdown.education >= 0.99:
            strengths.append("Educational background aligns with the required field of study.")
        if result.matched_preferred:
            strengths.append(f"Adds preferred skills: {', '.join(result.matched_preferred)}.")
        if result.breakdown.semantic_similarity >= 0.7:
            strengths.append(
                f"High semantic similarity ({result.semantic_similarity:.0%}) between the "
                "resume and the job description."
            )

        if result.missing_required:
            gaps.append(
                f"Missing {len(result.missing_required)}/{total_required} required "
                f"skills: {', '.join(result.missing_required)}."
            )
        if job.minimum_experience > 0 and result.experience_years < job.minimum_experience:
            gaps.append(
                f"Experience below the minimum ({result.experience_years:g} yr vs "
                f"{job.minimum_experience:g}+ yr required)."
            )
        if result.breakdown.semantic_similarity < 0.25:
            gaps.append("Low semantic similarity between the resume content and this job description.")
        if not gaps and result.missing_preferred:
            gaps.append(f"Preferred-skill gaps only: {', '.join(result.missing_preferred)}.")
        if not gaps:
            gaps.append("No significant gaps identified against the scoring criteria.")

        if result.score >= 85:
            reason = (
                f"{result.candidate} demonstrates strong alignment with the {job.title} role: "
                f"{matched_count}/{total_required} required skills matched, "
                f"{result.experience_years:g} years of relevant experience, and "
                f"{result.semantic_similarity:.0%} semantic similarity. "
            )
            reason += (
                f"Primary gap: {', '.join(result.missing_required)}."
                if result.missing_required
                else "No required-skill gaps identified."
            )
        elif result.score >= 70:
            reason = (
                f"Solid overall fit for the {job.title} role with "
                f"{matched_count}/{total_required} required skills matched. "
                f"Gaps to probe in an interview: {', '.join(result.missing_required) or 'none'}."
            )
        elif result.score >= 55:
            reason = (
                f"Partial fit for the {job.title} role "
                f"({matched_count}/{total_required} required skills matched). "
                f"Key gaps: {', '.join(result.missing_required) or 'n/a'}. "
                "Recommend manual review before a decision."
            )
        else:
            bullets = []
            if result.missing_required:
                bullets.append(
                    f"missing {len(result.missing_required)}/{total_required} "
                    f"required technical skills ({', '.join(result.missing_required)})"
                )
            if job.minimum_experience > 0 and result.experience_years < job.minimum_experience:
                bullets.append(
                    f"experience below the minimum requirement "
                    f"({result.experience_years:g} yr vs {job.minimum_experience:g}+ yr)"
                )
            if result.breakdown.semantic_similarity < 0.25:
                bullets.append(f"low semantic similarity ({result.semantic_similarity:.0%})")
            if not bullets:
                bullets.append("overall profile does not align with the role requirements")
            reason = "Why not shortlisted: " + "; ".join(bullets) + "."

        return strengths, gaps, reason.strip()

    def _llm_explanation(
        self, result: ScreeningResult, job: JobProfile
    ) -> Optional[Tuple[List[str], List[str], str]]:
        """LLM explanation layer -- explains the deterministic scores.

        The model is explicitly instructed NOT to change the calculated
        score or recommendation; it only produces reasoning text.
        """
        payload = {
            "job": {
                "title": job.title,
                "required_skills": job.required_skills,
                "preferred_skills": job.preferred_skills,
                "minimum_experience_years": job.minimum_experience,
                "education": job.education,
            },
            "candidate": {
                "name": result.candidate,
                "extracted_skills": result.skills,
                "experience_years": result.experience_years,
                "education": result.education,
            },
            "calculated_scores": {
                "final_score": result.score,
                "recommendation": result.recommendation,
                "required_skills_match": f"{result.breakdown.required_skills:.0%}",
                "experience_match": f"{result.breakdown.experience:.0%}",
                "education_match": f"{result.breakdown.education:.0%}",
                "semantic_similarity": f"{result.breakdown.semantic_similarity:.0%}",
                "preferred_skills_match": f"{result.breakdown.preferred_skills:.0%}",
                "matched_required": result.matched_required,
                "missing_required": result.missing_required,
                "matched_preferred": result.matched_preferred,
            },
        }
        system_prompt = (
            "You are an AI recruitment analyst. You are given: (1) job requirements, "
            "(2) the candidate profile, (3) ALREADY CALCULATED matching scores. "
            "Explain the candidate's suitability. Do NOT change the calculated score or "
            "recommendation. Do not invent information that is not present in the data. "
            'Return ONLY valid JSON: {"strengths": ["..."], "skill_gaps": ["..."], '
            '"experience_assessment": "...", "recommendation_rationale": "..."}'
        )
        data = self.llm.chat_json(system_prompt, json.dumps(payload, indent=2))
        if not data:
            return None

        strengths = [str(s) for s in (data.get("strengths") or []) if str(s).strip()][:6]
        gaps = [str(s) for s in (data.get("skill_gaps") or []) if str(s).strip()][:6]
        experience_assessment = str(data.get("experience_assessment") or "").strip()
        rationale = str(data.get("recommendation_rationale") or "").strip()
        reason = " ".join(part for part in (experience_assessment, rationale) if part)
        if not strengths or not gaps or not reason:
            return None
        return strengths, gaps, reason

    # ------------------------------------------------------------------
    # Outputs
    # ------------------------------------------------------------------
    def save_outputs(self, results: List[ScreeningResult], job: JobProfile, output_dir=None) -> Dict[str, Path]:
        out_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        csv_path = out_dir / "ranked_candidates.csv"
        json_path = out_dir / "ranked_candidates.json"
        report_path = out_dir / "screening_report.md"

        _write_csv(csv_path, results)
        _write_json(json_path, results, job, self.similarity_engine.backend)
        _write_markdown(report_path, results, job, self.similarity_engine.backend)

        return {"csv": csv_path, "json": json_path, "report": report_path}


# ---------------------------------------------------------------------------
# Report writers (module level so tests can call them in isolation)
# ---------------------------------------------------------------------------
def _write_csv(path: Path, results: List[ScreeningResult]) -> None:
    import pandas as pd

    rows = [
        {
            "rank": result.rank,
            "name": result.candidate,
            "score": result.score,
            "recommendation": result.recommendation,
            "confidence": result.confidence,
            "matched_skills": "|".join(result.matched_required),
            "missing_skills": "|".join(result.missing_required),
            "experience_years": result.experience_years,
            "semantic_similarity": round(result.semantic_similarity, 4),
            "flags": "|".join(result.flags),
            "source_file": result.source_file,
        }
        for result in results
    ]
    pd.DataFrame(rows).to_csv(path, index=False)


def _candidate_json(result: ScreeningResult) -> dict:
    return {
        "candidate": result.candidate,
        "rank": result.rank,
        "score": result.score,
        "recommendation": result.recommendation,
        "confidence": result.confidence,
        "skills": {
            "matched": result.matched_required,
            "missing": result.missing_required,
            "preferred_matched": result.matched_preferred,
            "preferred_missing": result.missing_preferred,
            "extracted": result.skills,
        },
        "score_breakdown_percent": {
            "required_skills": round(result.breakdown.required_skills * 100, 1),
            "experience": round(result.breakdown.experience * 100, 1),
            "education": round(result.breakdown.education * 100, 1),
            "semantic_similarity": round(result.breakdown.semantic_similarity * 100, 1),
            "preferred_skills": round(result.breakdown.preferred_skills * 100, 1),
        },
        "experience": {
            "required": result.required_experience,
            "candidate": result.experience_years,
        },
        "semantic_similarity": round(result.semantic_similarity, 4),
        "strengths": result.strengths,
        "skill_gaps": result.gaps,
        "reason": result.reason,
        "flags": result.flags,
        "source_file": result.source_file,
    }


def _write_json(path: Path, results: List[ScreeningResult], job: JobProfile, backend: str) -> None:
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "job": job.model_dump(),
        "similarity_backend": backend,
        "scoring_weights": WEIGHTS,
        "bias_policy": BIAS_NOTE,
        "candidates": [_candidate_json(result) for result in results],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_markdown(path: Path, results: List[ScreeningResult], job: JobProfile, backend: str) -> None:
    lines: List[str] = []
    lines.append("# AI Resume Screening Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    lines.append(f"**Job title:** {job.title}  ")
    lines.append(f"**Resumes screened:** {len(results)}  ")
    lines.append(f"**Similarity backend:** {backend}")
    lines.append("")
    lines.append(f"> {BIAS_NOTE}")
    lines.append("")
    lines.append("## Scoring Method")
    lines.append("")
    lines.append(
        "Final score = Required Skills x 40% + Experience x 25% + Education x 15% "
        "+ Semantic Similarity x 10% + Preferred Skills x 10%"
    )
    lines.append("")
    lines.append("| Component | Weight |")
    lines.append("| --- | --- |")
    for key, weight in WEIGHTS.items():
        lines.append(f"| {key.replace('_', ' ').title()} | {int(weight * 100)}% |")
    lines.append("")
    lines.append(
        "Recommendation thresholds: >= 85 STRONG SHORTLIST | >= 70 SHORTLIST | "
        ">= 55 REVIEW | < 55 REJECT"
    )
    lines.append("")
    lines.append("## Final Ranking")
    lines.append("")
    lines.append("| Rank | Candidate | Score | Recommendation | Confidence |")
    lines.append("| --- | --- | --- | --- | --- |")
    for result in results:
        lines.append(
            f"| {result.rank} | {result.candidate} | {result.score:.1f}% | "
            f"{result.recommendation} | {result.confidence} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Candidate Details")

    for result in results:
        lines.append("")
        lines.append(
            f"### #{result.rank} {result.candidate} \u2014 {result.score:.1f}% "
            f"({result.recommendation}, {result.confidence} confidence)"
        )
        lines.append("")
        file_line = f"- **File:** {result.source_file}"
        if result.flags:
            file_line += f"  **Flags:** {', '.join(result.flags)}"
        lines.append(file_line)
        lines.append("")
        lines.append("| Component | Score |")
        lines.append("| --- | --- |")
        lines.append(f"| Required Skills | {result.breakdown.required_skills * 100:.0f}% |")
        lines.append(f"| Experience | {result.breakdown.experience * 100:.0f}% |")
        lines.append(f"| Education | {result.breakdown.education * 100:.0f}% |")
        lines.append(f"| Semantic Similarity | {result.breakdown.semantic_similarity * 100:.0f}% |")
        lines.append(f"| Preferred Skills | {result.breakdown.preferred_skills * 100:.0f}% |")
        lines.append("")
        matched = ", ".join(f"\u2713 {skill}" for skill in result.matched_required) or "\u2014"
        missing = ", ".join(f"\u2717 {skill}" for skill in result.missing_required) or "\u2014"
        preferred = ", ".join(f"\u2713 {skill}" for skill in result.matched_preferred) or "\u2014"
        lines.append(f"**Matched required skills:** {matched}")
        lines.append("")
        lines.append(f"**Missing required skills:** {missing}")
        lines.append("")
        lines.append(f"**Preferred skills matched:** {preferred}")
        lines.append("")
        lines.append(
            f"**Experience:** {result.experience_years:g} years "
            f"(minimum required: {result.required_experience:g})"
        )
        lines.append("")
        lines.append(f"**Semantic similarity:** {result.semantic_similarity:.1%}")
        lines.append("")
        lines.append("**Strengths:**")
        for strength in result.strengths:
            lines.append(f"- {strength}")
        lines.append("")
        lines.append("**Skill gaps:**")
        for gap in result.gaps:
            lines.append(f"- {gap}")
        lines.append("")
        label = "Why not shortlisted?" if result.recommendation in ("REVIEW", "REJECT") else "Reason"
        lines.append(f"**{label}**")
        lines.append("")
        lines.append(result.reason)
        lines.append("")
        lines.append("---")

    path.write_text("\n".join(lines), encoding="utf-8")
