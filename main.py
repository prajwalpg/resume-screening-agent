#!/usr/bin/env python3
"""AI Resume Screening & Candidate Ranking Agent -- CLI entry point.

Usage:
    python main.py                      # interactive, uses the bundled sample JD
    python main.py path/to/jd.txt       # custom job description (PDF/TXT/DOCX)
    python main.py jd.txt data/resumes  # custom JD + custom resume folder
"""

import sys
from pathlib import Path

from app.agent.screening_agent import ScreeningAgent
from app.parser import is_supported
from app.utils.config import DEFAULT_JD_PATH, RESUME_DIR

BANNER = r"""
============================================================
           AI RESUME SCREENING AGENT
============================================================
"""

RANKING_HEADER = "================ FINAL RANKING ================"


def _resolve_jd_path() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    try:
        raw = input(f"Enter Job Description path [{DEFAULT_JD_PATH}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        raw = ""
        print()
    return Path(raw) if raw else Path(DEFAULT_JD_PATH)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print(BANNER)

    jd_path = _resolve_jd_path()
    if not jd_path.exists():
        print(f"ERROR: Job description file not found: {jd_path}")
        return 1

    resume_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(RESUME_DIR)
    if not resume_dir.is_dir():
        print(f"ERROR: Resume folder not found: {resume_dir}")
        return 1

    resume_files = [p for p in sorted(resume_dir.iterdir()) if p.is_file() and is_supported(p)]
    if not resume_files:
        print(f"ERROR: No supported resumes (PDF / DOCX / TXT) found in: {resume_dir}")
        return 1

    print(f"Job Description: {jd_path}")
    print(f"Resumes found: {len(resume_files)}")
    print()

    agent = ScreeningAgent(progress_callback=print)
    results, job = agent.screen(jd_path, resume_dir)

    print()
    print(RANKING_HEADER)
    print(f"{'Rank':<6}{'Candidate':<21}{'Score':<9}{'Recommendation':<18}{'Confidence':<10}")
    print("-" * 64)
    for result in results:
        score_text = f"{result.score:.1f}%"
        print(
            f"{result.rank:<6}"
            f"{result.candidate[:19]:<21}"
            f"{score_text:<9}"
            f"{result.recommendation:<18}"
            f"{result.confidence:<10}"
        )
    print("-" * 64)

    print()
    print("Results saved:")
    saved = agent.save_outputs(results, job)
    for label, path in saved.items():
        print(f"  \u2713 output/{path.name} ({label})")

    print()
    print("Protected/personal attributes are excluded from candidate scoring.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
