# AI Resume Screening & Candidate Ranking Agent

An AI-powered recruitment agent that analyzes multiple resumes against a job
description, calculates **explainable candidate relevance scores** using
deterministic weighted criteria + NLP semantic similarity, and produces a
**ranked shortlist** with strengths, skill gaps and hiring recommendations.

```
Job Description (PDF/TXT/DOCX)  +  Resume Folder (PDF/DOCX/TXT)
              │                            │
              ▼                            ▼
       JD Processor                 Document Parser
   (skills, requirements)      (PDF / DOCX / TXT -> text)
              │                            │
              │                   Information Extraction
              │                  (Pydantic CandidateProfile)
              │                            │
              └──────────┬─────────────────┘
                         ▼
                  MATCHING ENGINE
   Required Skills 40% | Experience 25% | Education 15%
        Semantic Similarity 10% | Preferred Skills 10%
                         ▼
                 Candidate Ranking
                         ▼
        ranked_candidates.csv / .json / screening_report.md
```

## Overview

| | |
| --- | --- |
| **Input** | 1 job description (TXT/PDF/DOCX) + a folder of resumes (PDF/DOCX/TXT) |
| **Output** | `output/ranked_candidates.csv`, `output/ranked_candidates.json`, `output/screening_report.md`, SQLite DB |
| **Interface** | Web App (`http://localhost:3000`) & REST API (`http://localhost:8000`) & CLI (`python main.py`) |
| **Stack** | Next.js / Vite React + Tailwind CSS + FastAPI + Python 3.12 + PyMuPDF + Sentence Transformers |
| **LLM** | Optional (OpenAI / Groq / Ollama — any OpenAI-compatible API) |

## Quick Start (Web Application)

```bash
# 1. Start FastAPI Backend (Port 8000)
python -m uvicorn app.server:app --host 127.0.0.1 --port 8000

# 2. Start Web Frontend (Port 3000)
cd frontend
npm install
npx vite --host 0.0.0.0 --port 3000

# 3. Open http://localhost:3000 in your browser!
```

Click **"Run 1-Click Demo (12 Sample Resumes)"** on the website to run an instant automated screening.


## Problem Statement

Manually screening dozens of resumes against a job description is slow,
inconsistent and hard to audit. Generic keyword matching is brittle, while a
pure-LLM score is a black box that can change between runs. This agent sits in
the middle: **deterministic, explainable scoring does the ranking; NLP captures
meaning beyond keywords; the LLM (optional) only extracts and explains.**

## Features

- **Multi-format parsing** — PDF (PyMuPDF), DOCX (python-docx), TXT.
- **Structured extraction** — resumes and JDs become validated Pydantic models
  (name, skills, education, experience, projects, certifications).
- **Hybrid matching engine** — explicit skill matching + TF-IDF/transformer
  semantic similarity, combined by a transparent weighted formula.
- **Explainable results** — every candidate gets matched/missing skills, a
  per-component score breakdown, a confidence level and a written reason.
- **"Why not shortlisted?"** — rejected/review candidates get explicit,
  itemised reasons.
- **Batch processing** — the bundled dataset ships 12 resumes; the agent
  processes any folder size with per-file progress and per-file error capture.
- **Duplicate detection** — identical resumes (candidate_11 in the sample
  data) are flagged, not silently double-counted.
- **Bias protection** — contact details are stripped before scoring and
  protected attributes (gender, age, photo, religion, caste, marital status,
  address) are excluded from all ranking logic.
- **Works without an LLM** — heuristic extractors and template explanations
  make the agent fully runnable offline; add API keys to upgrade extraction
  and explanations, never the scores.

## Tech Stack

| Component | Technology |
| --- | --- |
| Language | Python 3.9+ |
| PDF parsing | PyMuPDF (fitz) |
| DOCX parsing | python-docx |
| Semantic similarity | Sentence Transformers (`all-MiniLM-L6-v2`), TF-IDF fallback |
| Skill matching | Curated taxonomy + alias/synonym maps (deterministic) |
| Data validation | Pydantic |
| Data output | Pandas (CSV), JSON, Markdown |
| LLM (optional) | OpenAI SDK against OpenAI / Groq / Ollama |
| Testing | Pytest (29 tests) |

## How It Works

### 1. Resume Parsing
`app/parser` converts any supported file into plain text. PDF text is
extracted page-by-page with PyMuPDF; DOCX paragraphs *and* tables are read
with python-docx; TXT is read directly. Unsupported extensions fail fast with
a clear error.

### 2. Information Extraction
`app/extraction` converts raw text into structured profiles
(`CandidateProfile`, `JobProfile`). Two interchangeable backends:

- **LLM backend** — a strict JSON-only prompt ("do not invent information")
  parsed and validated into Pydantic models.
- **Heuristic backend** (default, zero-config) — section splitting, a curated
  skill taxonomy with alias resolution, regex for email/phone/degree lines,
  and a two-signal experience estimator: explicit "N years of experience"
  statements plus the union of employment date ranges *inside the work
  experience section only* (education years are never counted as work).

### 3. Skill Matching
Required and candidate skills are normalised (lowercase + aliases, e.g.
"JS" → "javascript"), then matched via exact canonical equality, synonym
groups (e.g. Postman / Rest Assured count as evidence for "API Testing") and
substring containment for multi-word skills. The score is the transparent
fraction `matched / required`, and the matched/missing lists keep the JD's
original wording for the reports.

### 4. Semantic Similarity
`SimilarityEngine` embeds the JD and every resume with
**Sentence Transformers `all-MiniLM-L6-v2`** and computes cosine similarity.
If the model cannot be installed/downloaded (offline machines, CI), the engine
automatically falls back to **TF-IDF + cosine similarity** (scikit-learn) —
weaker on paraphrase, but deterministic and dependency-light. The active
backend is printed during the run and recorded in every report.

### 5. Candidate Scoring
```
FINAL SCORE = Required Skill Match  x 40%
            + Experience Match      x 25%   (candidate_years / required_years, capped at 1.0)
            + Education Match       x 15%   (field match 1.0 / related degree 0.6 / unknown 0.5)
            + Semantic Similarity   x 10%
            + Preferred Skill Match x 10%
```
Experience gives proportional credit below the bar and saturates above it.
A missing education field is neutral (0.5) rather than punitive.

### 6. Ranking
Results are sorted by score (name as a stable tie-breaker) and mapped to
recommendations:

| Score | Recommendation |
| --- | --- |
| >= 85 | STRONG SHORTLIST |
| 70 – 84 | SHORTLIST |
| 55 – 69 | REVIEW |
| < 55 | REJECT |

A **confidence** level (HIGH / MEDIUM / LOW) reflects signal agreement:
final score, semantic similarity and the required-skill match ratio.

### 7. Explanation
For every candidate the agent produces strengths, skill gaps and a reason.
With an LLM configured, the *calculated* scores are sent to the model with the
instruction "do NOT change the calculated score or recommendation" and it
writes the narrative; without an LLM, a deterministic template produces the
same structure. Review and reject candidates additionally get an explicit
**"Why not shortlisted?"** breakdown.

## Scoring Method

Weights live in `app/utils/config.py` and must sum to 1.0:

```python
WEIGHTS = {
    "required_skills": 0.40,
    "experience": 0.25,
    "education": 0.15,
    "semantic_similarity": 0.10,
    "preferred_skills": 0.10,
}
```

## Installation

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) configure an LLM
cp .env.example .env              # then edit .env
```

> **Note:** `sentence-transformers` pulls in PyTorch (~2 GB). If that is a
> problem, comment the line out of `requirements.txt` — the agent
> automatically falls back to TF-IDF similarity and stays fully functional.

## Environment Variables

All optional — the agent runs without any of them:

| Variable | Purpose |
| --- | --- |
| `LLM_PROVIDER` | `openai` \| `groq` \| `ollama` \| custom |
| `LLM_MODEL` | Model name (e.g. `gpt-4o-mini`, `llama-3.3-70b-versatile`, `llama3.2`) |
| `LLM_API_KEY` | API key (not needed for Ollama) |
| `LLM_BASE_URL` | Override the provider's default endpoint |

## Running the Agent

```bash
python main.py                              # bundled sample JD + 12 sample resumes
python main.py data/jd/my_jd.txt            # custom job description
python main.py my_jd.txt my_resume_folder   # custom JD + resume folder
pytest                                      # run the test suite (29 tests)
python scripts/generate_sample_data.py      # regenerate the sample dataset
```

## Sample Input

The bundled dataset (`data/`) contains a **Software Test Automation Engineer**
JD (required: Python, Selenium, API Testing, SQL, Git; preferred: Pytest,
Jenkins, Docker; minimum 1 year experience; CS/IT education) and **12 resumes
in mixed formats** deliberately spanning the full spectrum: strong automation
engineers, a manual tester, adjacent Java testers, a backend developer, a
frontend developer, a fresher, and one exact duplicate (candidate_11 =
candidate_02, used to demonstrate duplicate detection).

## Sample Output

Actual console output from this repository:

```
Job profile: Software Test Automation Engineer
Required skills: Python, SQL, Selenium, API Testing, Git
Preferred skills: Pytest, Jenkins, Docker

[1/12] candidate_01.pdf ✓ -> Priya Sharma (heuristic)
...
[12/12] candidate_12.txt ✓ -> Karthik Menon (heuristic)

================ FINAL RANKING ================
Rank  Candidate            Score    Recommendation    Confidence
----------------------------------------------------------------
1     Priya Sharma         93.7%    STRONG SHORTLIST  HIGH
2     Rahul Kumar          90.2%    STRONG SHORTLIST  HIGH
3     Rahul Kumar          90.2%    STRONG SHORTLIST  HIGH
4     Divya Nair           84.4%    SHORTLIST         MEDIUM
5     Sneha Reddy          81.5%    SHORTLIST         MEDIUM
6     Ananya Rao           78.0%    SHORTLIST         MEDIUM
7     Meera Iyer           65.9%    REVIEW            MEDIUM
8     Kiran Patel          65.7%    REVIEW            MEDIUM
9     Karthik Menon        62.5%    REVIEW            MEDIUM
10    Arjun Singh          60.4%    REVIEW            MEDIUM
11    Vikram Joshi         42.5%    REJECT            LOW
12    Rohit Verma          17.3%    REJECT            LOW
----------------------------------------------------------------
```

Excerpt from `screening_report.md`:

```
### #2 Rahul Kumar — 90.2% (STRONG SHORTLIST, HIGH confidence)

| Component           | Score |
| ------------------- | ----- |
| Required Skills     | 100%  |
| Experience          | 100%  |
| Education           | 100%  |
| Semantic Similarity | 35%   |
| Preferred Skills    | 67%   |

Matched required skills: ✓ Python, ✓ SQL, ✓ Selenium, ✓ API Testing, ✓ Git
Missing required skills: —
Reason: Rahul Kumar demonstrates strong alignment with the role: 5/5 required
skills matched, 4 years of relevant experience. Primary gap: none. Preferred
skills add Pytest and Jenkins; Docker is the only gap.
```

## Evaluation

The repository ships a 12-resume evaluation dataset and a pytest suite
covering the scenarios below:

| Scenario | Where / Result |
| --- | --- |
| Perfect candidate → > 85%, STRONG SHORTLIST | `tests/test_scoring.py` + Priya/Divya in dataset |
| Good candidate → 70–85%, SHORTLIST | `tests/test_scoring.py` + Sneha/Ananya |
| Weak candidate → < 55%, REJECT | `tests/test_scoring.py` + Rohit/Vikram |
| Resume with no experience | candidate_09 (fresher) → experience component 0 |
| Resume with missing skills | every REVIEW/REJECT candidate gets itemised gaps |
| PDF with unusual formatting | generated PDFs via PyMuPDF parse cleanly |
| DOCX | candidates 03, 05, 09 |
| TXT | candidates 07, 12 |
| 10+ resumes | `tests/test_agent.py` batch test |
| Duplicate resumes | candidate_11 flagged "possible duplicate of candidate_02.pdf" |

Run everything with `pytest -q` (29 tests, ~4 s).

## Design Decisions

1. **Hybrid architecture: rules + embeddings + (optional) LLM.**
   *"I intentionally separated scoring from LLM reasoning. Deterministic
   scoring makes the ranking reproducible and explainable, while the LLM is
   used for structured extraction and natural-language reasoning. This
   reduces the risk of letting an LLM arbitrarily decide candidate scores."*
2. **Extraction is modelled explicitly** (Pydantic schemas) instead of
   feeding raw text to the scorer — scoring stays auditable.
3. **Skill matching never relies on embeddings alone.** Embeddings capture
   topical similarity; the explicit matcher produces the audit trail
   ("matched 5/5: Python, Selenium, ...").
4. **Faithful display names** — matched/missing skills are shown exactly as
   the JD words them ("API Testing"), not as internal canonical tokens.
5. **Bias protection by construction** — only skills, experience and
   education enter the scoring function; contact details are stripped before
   semantic analysis and a policy note is embedded in every report.

## Tradeoffs

### Why Sentence Transformers?
Embedding-based semantic similarity captures relationships between job
requirements and resume content better than plain keyword matching
("built UI test scripts" ≈ "Selenium automation"). `all-MiniLM-L6-v2` is
small, fast and strong on short-text similarity.

### Why a TF-IDF fallback?
Torch + model download is heavy and can be impossible in offline/CI
environments. The fallback keeps the system runnable everywhere; the active
backend is always disclosed in reports so readers can weigh similarity
numbers accordingly.

### Why deterministic scoring?
A weighted rule system makes rankings **reproducible** (same input → same
score), **tunable** (recruiters can adjust weights) and **auditable** (every
component is individually visible). Pure-LLM scoring fails all three.

### Why use an LLM at all?
Resume/JD text is messy; LLMs excel at messy extraction and at writing
human-readable justifications. Constrained to JSON extraction and
score-agnostic explanation, the LLM adds value without becoming the judge.

### Why not fine-tune a model?
No large labelled recruitment dataset is available for a short-horizon
project, and a pre-trained embedding model already provides a strong
baseline. Fine-tuning would add training complexity without a measurable
target to beat.

### Limitations
- Extraction quality bounds everything: scanned/image-only PDFs need OCR
  (not implemented), and unusual layouts can hide sections from heuristics.
- The synonym/alias maps are curated, not learned — niche skills may need
  entries added to `SKILL_TAXONOMY` / `SYNONYM_GROUPS`.
- TF-IDF similarity is lexical; with the fallback active, semantic-similarity
  numbers are conservative.
- Experience years are estimated from text signals and can be noisy.
- **This system is a screening aid, not a replacement for human hiring
  decisions.** All recommendations should be reviewed by a human recruiter.

## Future Improvements

- OCR support (Tesseract) for scanned resumes.
- Learning skill synonym groups from a corpus instead of curating them.
- A thin FastAPI service wrapping `ScreeningAgent` for programmatic use.
- Streamlit UI with drag-and-drop upload and per-candidate drill-down.
- Calibration of weights/thresholds against recruiter decisions.

## Project Structure

```
resume-screening-agent/
├── app/
│   ├── agent/            # ScreeningAgent: orchestration + reports
│   ├── extraction/       # Resume/JD -> structured profiles (LLM + heuristics)
│   ├── matching/         # Embeddings, skill matcher, weighted scoring
│   ├── models/           # Pydantic schemas
│   ├── parser/           # PDF / DOCX / TXT -> text
│   └── utils/            # Config, taxonomy, LLM client, text helpers
├── data/
│   ├── jd/               # software_test_engineer.txt
│   └── resumes/          # candidate_01..12 (PDF / DOCX / TXT)
├── output/               # generated CSV / JSON / Markdown reports
├── scripts/
│   └── generate_sample_data.py
├── tests/                # pytest: parser, matching, scoring, e2e
├── main.py               # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Bias & Fairness Policy

Protected/personal attributes — gender, age, photograph, religion, caste,
marital status, address — are **excluded from candidate scoring**. The
pipeline only consumes skills, experience and education; contact details are
removed before semantic analysis. Duplicate resumes are flagged rather than
double-counted, and every verdict carries an explanation so a human can audit
any decision.

## Author

Built as a demonstration of an explainable, reproducible AI screening agent.
Replace this line with your name / GitHub profile.
