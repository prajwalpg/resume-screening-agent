"""End-to-end integration test: batch-screen the bundled sample dataset.

Covers the evaluation-plan items: batch processing of 10+ resumes,
duplicate detection, ranking order, recommendation bands and output
generation (CSV + JSON + Markdown).
"""

import csv
import json

from app.agent.screening_agent import ScreeningAgent
from app.utils.config import DEFAULT_JD_PATH, RESUME_DIR


def test_end_to_end_batch_screening(tmp_path):
    agent = ScreeningAgent(use_llm=False)  # deterministic run: no LLM
    results, job = agent.screen(DEFAULT_JD_PATH, RESUME_DIR)

    # Batch: 10+ resumes processed
    assert len(results) >= 10

    # Ranking is strictly by descending score with correct rank numbers
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)
    assert all(0.0 <= r.score <= 100.0 for r in results)
    assert [r.rank for r in results] == list(range(1, len(results) + 1))

    # All recommendation bands of the evaluation plan are exercised
    bands = {r.recommendation for r in results}
    assert "STRONG SHORTLIST" in bands
    assert "REJECT" in bands
    assert max(scores) >= 85    # perfect-ish candidate exists
    assert min(scores) < 55     # weak candidate exists

    # Duplicate detection: candidate_11 is a copy of candidate_02
    duplicates = [r for r in results if r.flags]
    assert duplicates and any("duplicate" in flag for r in duplicates for flag in r.flags)

    # Every candidate has an explanation
    assert all(r.reason.strip() for r in results)

    # Outputs are written
    paths = agent.save_outputs(results, job, output_dir=tmp_path)
    assert paths["csv"].exists() and paths["json"].exists() and paths["report"].exists()

    with open(paths["csv"], newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == len(results)
    assert rows[0]["rank"] == "1"

    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["job"]["title"] == job.title
    assert len(payload["candidates"]) == len(results)
    assert "scoring_weights" in payload
