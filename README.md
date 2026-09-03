# 🤖 AI Resume Screening & Candidate Ranking Agent

An AI-powered recruitment platform that automatically analyzes resumes against a job description, extracts candidate information, calculates **explainable candidate-fit scores**, ranks candidates, identifies skill gaps, detects duplicate resumes, and generates hiring recommendations.

The system combines **deterministic rule-based scoring, NLP semantic similarity, structured information extraction, and optional LLM capabilities** to provide a transparent and reproducible resume screening workflow.

---

## 🌐 Live Demo

🚀 **Live Application:**
https://resume-screening-agent-roan.vercel.app/

📦 **GitHub Repository:**
https://github.com/prajwalpg/resume-screening-agent

---

## 📌 Overview

Recruiters often need to manually review dozens or hundreds of resumes for a single job opening.

Traditional keyword-based screening can miss relevant candidates because different resumes may describe the same skill using different terminology. On the other hand, allowing an LLM to make the final hiring decision can make the process difficult to reproduce and audit.

This project solves the problem using a **hybrid AI screening architecture**:

```text
                ┌──────────────────────────┐
                │       Job Description    │
                │      PDF / DOCX / TXT    │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │     JD Document Parser   │
                │  Skills / Requirements   │
                └────────────┬─────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────┐
│                  RESUME PROCESSING                   │
│                                                     │
│  PDF ──┐                                            │
│  DOCX ─┼──► Document Parser ──► Text Extraction     │
│  TXT ──┘                                            │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
                ┌──────────────────────────┐
                │ Information Extraction   │
                │ CandidateProfile /       │
                │ JobProfile (Pydantic)    │
                └────────────┬─────────────┘
                             │
             ┌───────────────┴────────────────┐
             │                                │
             ▼                                ▼
   ┌───────────────────┐          ┌────────────────────┐
   │ Skill Matching     │          │ Semantic Similarity│
   │ Exact + Aliases    │          │ SentenceTransform. │
   │ + Synonyms         │          │ / TF-IDF fallback │
   └──────────┬────────┘          └─────────┬──────────┘
              │                             │
              └──────────────┬──────────────┘
                             ▼
                ┌──────────────────────────┐
                │   Weighted Scoring      │
                │                          │
                │ Required Skills   40%   │
                │ Experience        25%   │
                │ Education         15%   │
                │ Semantic Match    10%   │
                │ Preferred Skills  10%   │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │ Candidate Ranking        │
                │ + Confidence             │
                │ + Skill Gaps             │
                │ + Strengths              │
                │ + Recommendation         │
                └────────────┬─────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │ CSV / JSON / Markdown / SQLite / UI   │
        └────────────────────────────────────────┘
```

---

# ✨ Key Features

## 📄 Multi-Format Resume Parsing

Supports multiple resume formats:

* PDF
* DOCX
* TXT

The parser extracts resume content and converts it into normalized text for downstream processing.

### PDF

Powered by **PyMuPDF (`fitz`)**.

### DOCX

Uses **python-docx** and supports both paragraphs and tables.

### TXT

Plain-text resumes are processed directly.

---

## 📋 Job Description Processing

The system accepts a job description in:

* PDF
* DOCX
* TXT

The JD processor extracts:

* Required skills
* Preferred skills
* Experience requirements
* Education requirements
* Job title
* Relevant requirements

---

# 🧠 Intelligent Candidate Extraction

Resume information is converted into structured Pydantic models.

Candidate information can include:

* Candidate name
* Skills
* Education
* Experience
* Projects
* Certifications
* Contact information

The system provides two extraction approaches.

### 1. Heuristic Extraction

The default extraction method requires no API key.

It uses:

* Section detection
* Skill taxonomy
* Skill aliases
* Regular expressions
* Experience estimation
* Degree detection

### 2. LLM Extraction

An optional LLM backend can be configured for more flexible extraction from unstructured resumes.

The LLM is instructed to return structured JSON and avoid inventing candidate information.

---

# 🎯 Explainable Candidate Scoring

A major design goal of this project is **explainability**.

Instead of allowing an LLM to randomly assign a candidate score, the final score is calculated using deterministic weighted components.

## Scoring Formula

```text
Final Score =
    Required Skill Match × 40%
  + Experience Match × 25%
  + Education Match × 15%
  + Semantic Similarity × 10%
  + Preferred Skill Match × 10%
```

### Weight Configuration

```python
WEIGHTS = {
    "required_skills": 0.40,
    "experience": 0.25,
    "education": 0.15,
    "semantic_similarity": 0.10,
    "preferred_skills": 0.10,
}
```

The weights are configurable in:

```text
app/utils/config.py
```

---

# 📊 Candidate Recommendations

Candidates are automatically categorized based on their final score.

| Score | Recommendation      |
| ----: | ------------------- |
|  ≥ 85 | 🟢 STRONG SHORTLIST |
| 70–84 | 🟢 SHORTLIST        |
| 55–69 | 🟡 REVIEW           |
|  < 55 | 🔴 REJECT           |

The system also calculates a confidence level:

* HIGH
* MEDIUM
* LOW

Confidence is based on agreement between multiple screening signals.

---

# 🔍 Skill Matching

Candidate skills are normalized before comparison.

For example:

```text
JS → JavaScript
Postman → API Testing evidence
Rest Assured → API Testing evidence
```

The matching engine supports:

* Exact skill matching
* Alias resolution
* Synonym groups
* Multi-word skill matching
* Required skill matching
* Preferred skill matching

The report preserves the original terminology used in the job description.

Example:

```text
Required Skills

✓ Python
✓ Selenium
✓ API Testing
✓ SQL
✗ Git
```

---

# 🧬 Semantic Similarity

The project uses NLP embeddings to identify semantic relationships between resumes and job descriptions.

Primary model:

```text
Sentence Transformers
all-MiniLM-L6-v2
```

The system calculates cosine similarity between the job description and candidate resume.

This helps identify cases where the candidate uses different wording for related experience.

For example:

```text
JD:
"Selenium automation testing"

Resume:
"Built automated UI test scripts using Selenium WebDriver"
```

Keyword matching alone may be limited, while semantic similarity can recognize the relationship.

---

# 🔄 TF-IDF Fallback

If Sentence Transformers cannot be installed or the model cannot be downloaded, the system automatically falls back to:

```text
TF-IDF + Cosine Similarity
```

This makes the project more resilient in:

* Offline environments
* CI/CD environments
* Lightweight deployments

The active similarity backend is reported during execution.

---

# 🤖 Optional LLM Integration

The system can work completely without an LLM.

However, an LLM can be enabled for:

* Structured resume extraction
* Job description extraction
* Natural-language candidate explanations
* Strength generation
* Skill-gap explanations

Supported providers include OpenAI-compatible APIs such as:

* OpenAI
* Groq
* Ollama
* Custom OpenAI-compatible endpoints

### Important Design Principle

The LLM **does not determine the final candidate score**.

Instead:

```text
Deterministic Engine
        │
        ├── Calculates Score
        ├── Calculates Ranking
        └── Determines Recommendation
                    │
                    ▼
                  LLM
                    │
                    └── Generates Explanation
```

This keeps candidate ranking reproducible and auditable.

---

# 🛡️ Bias Protection

The system is designed to avoid using protected personal attributes during ranking.

The following attributes are excluded from candidate scoring:

* Gender
* Age
* Photograph
* Religion
* Caste
* Marital status
* Address

Contact information is removed before semantic analysis.

The ranking logic focuses on job-relevant signals such as:

* Skills
* Experience
* Education
* Semantic relevance

> ⚠️ This system is a recruitment screening aid and should not replace human hiring decisions.

---

# ♻️ Duplicate Resume Detection

The system detects duplicate resumes during batch processing.

Identical resumes are flagged rather than silently counted multiple times.

Example:

```text
candidate_11.pdf
Possible duplicate of candidate_02.pdf
```

This prevents duplicate candidates from artificially affecting ranking results.

---

# 📦 Batch Resume Screening

The agent can process multiple resumes from a directory.

Example:

```text
data/resumes/

├── candidate_01.pdf
├── candidate_02.pdf
├── candidate_03.docx
├── candidate_04.pdf
├── candidate_05.docx
└── candidate_06.txt
```

Each candidate is processed independently.

The system provides:

* Per-file processing status
* Extraction result
* Candidate score
* Recommendation
* Error capture
* Final ranking

---

# 🖥️ Web Application

The project includes a browser-based frontend built with:

* React
* Vite
* Tailwind CSS

The frontend provides an interface for running the resume screening workflow.

The backend exposes the screening functionality through a FastAPI application.

### Application Architecture

```text
React + Vite Frontend
        │
        │ HTTP / REST
        ▼
FastAPI Backend
        │
        ▼
Screening Agent
        │
        ├── Parser
        ├── Extraction
        ├── Matching
        ├── Similarity
        ├── Scoring
        └── Reporting
```

---

# 🔌 REST API

The backend is implemented using **FastAPI**.

Default development server:

```text
http://localhost:8000
```

API documentation is available through FastAPI's automatic documentation interface when the server is running:

```text
http://localhost:8000/docs
```

---

# 🖥️ CLI

The project also provides a command-line interface.

Run the bundled sample:

```bash
python main.py
```

Run with a custom job description:

```bash
python main.py data/jd/my_jd.txt
```

Run with a custom job description and resume directory:

```bash
python main.py my_jd.txt my_resume_folder
```

---

# 📁 Project Structure

```text
resume-screening-agent/
│
├── app/
│   ├── agent/
│   │   └── # Screening orchestration and reporting
│   │
│   ├── extraction/
│   │   └── # Resume/JD information extraction
│   │
│   ├── matching/
│   │   └── # Skill matching, embeddings and scoring
│   │
│   ├── models/
│   │   └── # Pydantic data models
│   │
│   ├── parser/
│   │   └── # PDF / DOCX / TXT parsing
│   │
│   └── utils/
│       └── # Configuration, taxonomy and LLM utilities
│
├── data/
│   ├── jd/
│   │   └── software_test_engineer.txt
│   │
│   └── resumes/
│       └── # Sample candidate resumes
│
├── frontend/
│   └── # React + Vite web application
│
├── output/
│   └── # Generated screening reports
│
├── scripts/
│   └── generate_sample_data.py
│
├── tests/
│   └── # Automated test suite
│
├── main.py
├── conftest.py
├── requirements.txt
├── .env.example
├── Procfile
├── render.yaml
├── vercel.json
└── README.md
```

---

# ⚙️ Technology Stack

| Component           | Technology             |
| ------------------- | ---------------------- |
| Backend             | Python                 |
| API                 | FastAPI                |
| Frontend            | React + Vite           |
| Styling             | Tailwind CSS           |
| Data Validation     | Pydantic               |
| PDF Processing      | PyMuPDF                |
| DOCX Processing     | python-docx            |
| NLP                 | Sentence Transformers  |
| NLP Fallback        | TF-IDF / scikit-learn  |
| Data Processing     | Pandas                 |
| Output              | CSV / JSON / Markdown  |
| Database            | SQLite                 |
| LLM                 | OpenAI / Groq / Ollama |
| Testing             | Pytest                 |
| Frontend Deployment | Vercel                 |
| Backend Deployment  | Render                 |

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/prajwalpg/resume-screening-agent.git
```

Navigate into the project:

```bash
cd resume-screening-agent
```

---

# 🐍 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 📦 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 4. Configure Environment Variables

Create a `.env` file from the example:

### Windows

```bash
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Edit `.env` if you want to enable an LLM provider.

Example:

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=your_api_key
```

All LLM variables are optional.

The application can run without an API key using the heuristic extraction and deterministic explanation pipeline.

---

# ▶️ Running the Backend

Start FastAPI:

```bash
python -m uvicorn app.server:app --host 127.0.0.1 --port 8000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

# ▶️ Running the Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start Vite:

```bash
npx vite --host 0.0.0.0 --port 3000
```

Open:

```text
http://localhost:3000
```

---

# ⚡ Quick Demo

The project includes sample data so that the screening workflow can be tested immediately.

Run:

```bash
python main.py
```

The sample dataset contains:

* A Software Test Automation Engineer job description
* 12 candidate resumes
* Multiple resume formats
* Strong candidates
* Moderate candidates
* Weak candidates
* A fresher
* Different technical backgrounds
* A duplicate resume

---

# 📊 Example Screening Result

Example ranking:

```text
============================================================
FINAL RANKING
============================================================

Rank  Candidate        Score     Recommendation
------------------------------------------------------------
1     Priya Sharma     93.7%     STRONG SHORTLIST
2     Rahul Kumar      90.2%     STRONG SHORTLIST
3     Rahul Kumar      90.2%     STRONG SHORTLIST
4     Divya Nair       84.4%     SHORTLIST
5     Sneha Reddy      81.5%     SHORTLIST
6     Ananya Rao       78.0%     SHORTLIST
7     Meera Iyer       65.9%     REVIEW
8     Kiran Patel      65.7%     REVIEW
9     Karthik Menon    62.5%     REVIEW
10    Arjun Singh      60.4%     REVIEW
11    Vikram Joshi     42.5%     REJECT
12    Rohit Verma      17.3%     REJECT
```

---

# 📄 Generated Outputs

The system generates multiple output formats.

### CSV

```text
output/ranked_candidates.csv
```

Useful for:

* Recruiter review
* Excel analysis
* Candidate ranking
* Reporting

### JSON

```text
output/ranked_candidates.json
```

Useful for:

* APIs
* Integrations
* Applications
* Data pipelines

### Markdown Report

```text
output/screening_report.md
```

Contains:

* Candidate ranking
* Score breakdown
* Matched skills
* Missing skills
* Strengths
* Skill gaps
* Recommendation
* Confidence
* Explanation

---

# 🧪 Testing

The repository includes an automated pytest suite.

Run all tests:

```bash
pytest
```

Or:

```bash
pytest -q
```

The test suite covers:

* Resume parsing
* PDF processing
* DOCX processing
* TXT processing
* Skill matching
* Semantic similarity
* Candidate scoring
* Ranking
* Missing skills
* Duplicate detection
* Batch processing
* End-to-end screening

---

# 📈 Evaluation Scenarios

The sample dataset is intentionally designed to test different candidate profiles.

| Scenario                | Expected Result           |
| ----------------------- | ------------------------- |
| Excellent candidate     | STRONG SHORTLIST          |
| Good candidate          | SHORTLIST                 |
| Borderline candidate    | REVIEW                    |
| Weak candidate          | REJECT                    |
| Fresher                 | Low/zero experience score |
| Missing required skills | Skill-gap explanation     |
| Duplicate resume        | Duplicate warning         |
| DOCX resume             | Successfully parsed       |
| TXT resume              | Successfully parsed       |
| PDF resume              | Successfully parsed       |
| 10+ resumes             | Batch processing          |

---

# 🧠 Design Philosophy

## Why Hybrid AI?

The project deliberately combines three approaches:

```text
Rules
  +
NLP Embeddings
  +
Optional LLM
```

Each component has a specific responsibility.

### Rules

Provide:

* Reproducibility
* Transparency
* Deterministic scoring
* Auditable results

### NLP

Provides:

* Semantic understanding
* Better matching beyond exact keywords
* Resume/JD similarity

### LLM

Provides:

* Flexible information extraction
* Natural-language explanations
* Human-readable summaries

---

# 🔐 Why the LLM Does Not Control the Score

A pure LLM-based recruitment system could produce different scores for the same candidate depending on:

* Prompt changes
* Model changes
* Temperature
* Context
* Model updates

This project separates **decision calculation** from **language generation**.

```text
                    ┌─────────────────┐
                    │ Candidate Data  │
                    └────────┬────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │ Deterministic Scoring  │
                └───────────┬────────────┘
                            │
                    ┌───────┴────────┐
                    │                │
                    ▼                ▼
                 Score          Recommendation
                    │                │
                    └───────┬────────┘
                            ▼
                     Optional LLM
                            │
                            ▼
                     Explanation
```

This approach makes the screening pipeline easier to understand, test and audit.

---

# ⚖️ Limitations

The current system has several limitations.

### OCR

Scanned/image-only PDFs are not currently supported by the standard text extraction pipeline.

Future versions can integrate:

```text
Tesseract OCR
```

or another OCR engine.

### Skill Taxonomy

The skill taxonomy and synonym mappings are curated.

Niche technologies may need to be added manually.

### Experience Estimation

Experience is estimated from resume text and employment date ranges, so unusual resume formats can affect accuracy.

### Semantic Similarity

TF-IDF fallback is less capable of understanding paraphrasing than transformer embeddings.

### Human Review

The system is designed as a **decision-support tool**, not an autonomous hiring replacement.

---

# 🔮 Future Improvements

Planned improvements include:

* [ ] OCR support for scanned resumes
* [ ] More advanced resume layout detection
* [ ] Automatic skill taxonomy expansion
* [ ] Better experience extraction
* [ ] Recruiter authentication
* [ ] Candidate database dashboard
* [ ] Interview question generation
* [ ] Candidate comparison view
* [ ] Recruiter feedback loop
* [ ] Score calibration using historical hiring decisions
* [ ] Advanced analytics dashboard
* [ ] Email integration
* [ ] Job portal integrations
* [ ] Multi-language resume support
* [ ] Improved explainability dashboard

---

# 👨‍💻 Use Cases

This system can be used for:

### Recruiters

Quickly shortlist candidates from large resume collections.

### HR Teams

Standardize initial resume screening.

### Startups

Automate repetitive recruitment workflows.

### Technical Hiring

Compare resumes against technical job descriptions.

### Academic Projects

Demonstrate:

* NLP
* Generative AI
* Embeddings
* Information extraction
* Explainable AI
* Agentic workflows
* Full-stack development

---

# 💡 Example Workflow

```text
1. Recruiter uploads Job Description
                ↓
2. Recruiter uploads multiple resumes
                ↓
3. System extracts resume text
                ↓
4. Candidate information is structured
                ↓
5. Required/preferred skills are identified
                ↓
6. Skills are normalized
                ↓
7. Semantic similarity is calculated
                ↓
8. Candidate score is calculated
                ↓
9. Candidates are ranked
                ↓
10. Skill gaps are identified
                ↓
11. Strengths are generated
                ↓
12. Hiring recommendation is produced
                ↓
13. Results are exported
```

---

# 📊 Sample Score Breakdown

Example candidate:

```text
Candidate: Rahul Kumar

Required Skills       100%
Experience            100%
Education             100%
Semantic Similarity    35%
Preferred Skills       67%

Final Score: 90.2%

Recommendation:
STRONG SHORTLIST

Confidence:
HIGH
```

The recruiter can also see:

```text
Matched Required Skills:
✓ Python
✓ SQL
✓ Selenium
✓ API Testing
✓ Git

Missing Required Skills:
None

Preferred Skills:
✓ Pytest
✓ Jenkins
✗ Docker
```

---

# 🧪 Regenerate Sample Data

The repository includes a sample-data generation script.

Run:

```bash
python scripts/generate_sample_data.py
```

This can regenerate the demonstration dataset used for testing the screening workflow.

---

# 📁 Custom Usage

You can replace the bundled data with your own.

Example:

```text
my-project/
│
├── job_description.pdf
│
└── resumes/
    ├── resume1.pdf
    ├── resume2.pdf
    ├── resume3.docx
    ├── resume4.pdf
    └── resume5.txt
```

Then run:

```bash
python main.py job_description.pdf resumes/
```

---

# 🔧 Configuration

The scoring configuration can be customized in:

```text
app/utils/config.py
```

Example:

```python
WEIGHTS = {
    "required_skills": 0.40,
    "experience": 0.25,
    "education": 0.15,
    "semantic_similarity": 0.10,
    "preferred_skills": 0.10,
}
```

The total weights should equal:

```text
1.0
```

This makes it possible to customize the screening system for different recruitment requirements.

---

# 🌐 Deployment

The repository includes deployment configuration for:

### Frontend

Vercel configuration:

```text
vercel.json
```

### Backend

Render configuration:

```text
render.yaml
Procfile
```

The frontend and backend can therefore be deployed independently.

---

# 🔑 Environment Variables

All LLM-related environment variables are optional.

| Variable       | Description                       |
| -------------- | --------------------------------- |
| `LLM_PROVIDER` | LLM provider                      |
| `LLM_MODEL`    | Model name                        |
| `LLM_API_KEY`  | API key                           |
| `LLM_BASE_URL` | Custom OpenAI-compatible endpoint |

Example:

```env
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=your_api_key
```

For Ollama:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
```

---

# 🏗️ Architecture

The project follows a modular architecture.

```text
                 USER
                  │
                  ▼
        ┌───────────────────┐
        │ React Web Frontend│
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │    FastAPI API    │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │  Screening Agent  │
        └─────────┬─────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
        ▼         ▼         ▼
     Parser  Extraction  Matching
        │         │         │
        └─────────┼─────────┘
                  ▼
        ┌───────────────────┐
        │ Similarity Engine │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ Scoring Engine    │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │ Ranking & Reports │
        └───────────────────┘
```

---

# 🛠️ Engineering Highlights

This project demonstrates practical implementation of:

* Python
* FastAPI
* React
* Vite
* Tailwind CSS
* NLP
* Sentence Transformers
* TF-IDF
* Cosine Similarity
* Pydantic
* PDF parsing
* DOCX parsing
* REST APIs
* SQLite
* LLM integration
* Deterministic scoring
* Explainable AI
* Batch processing
* Automated testing
* Frontend/backend deployment

---

# 📜 License

This project is intended as an educational and demonstration project.

Add your preferred open-source license to the repository if you plan to distribute or modify the project publicly.

---

# 👨‍💻 Author

**Prajwal PG**

AI/ML & Generative AI Developer

GitHub:
https://github.com/prajwalpg

Project:
https://github.com/prajwalpg/resume-screening-agent

---

# ⭐ Support

If you find this project useful:

⭐ Star the repository
🍴 Fork the repository
🐛 Report issues
💡 Suggest improvements
🤝 Contribute to the project

---

## 📌 Disclaimer

This application provides automated resume analysis and candidate ranking for screening assistance.

It should **not be used as the sole basis for employment decisions**. Recruiters and hiring teams should review candidate information and make final decisions using appropriate human judgment and organizational hiring policies.
