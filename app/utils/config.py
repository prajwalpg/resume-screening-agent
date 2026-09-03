"""Central configuration for the AI Resume Screening Agent.

Paths, scoring weights, recommendation thresholds, LLM settings and the
skill taxonomy used by the heuristic extractor / matcher all live here so
there is a single place to tune the agent.
"""

import os
from pathlib import Path

try:  # Optional dependency: only needed when a .env file is present.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
JD_DIR = DATA_DIR / "jd"
RESUME_DIR = DATA_DIR / "resumes"
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_JD_PATH = JD_DIR / "software_test_engineer.txt"

# ---------------------------------------------------------------------------
# Scoring weights -- must sum to 1.0
# ---------------------------------------------------------------------------
WEIGHTS = {
    "required_skills": 0.40,
    "experience": 0.25,
    "education": 0.15,
    "semantic_similarity": 0.10,
    "preferred_skills": 0.10,
}

# Recommendation thresholds on the final 0-100 score (checked top-down).
RECOMMENDATION_THRESHOLDS = (
    (85.0, "STRONG SHORTLIST"),
    (70.0, "SHORTLIST"),
    (55.0, "REVIEW"),
    (0.0, "REJECT"),
)

# ---------------------------------------------------------------------------
# LLM configuration (fully optional -- the agent works without an LLM)
# Any OpenAI-compatible provider is supported: openai | groq | ollama | custom
# ---------------------------------------------------------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")
LLM_API_KEY = (
    os.getenv("LLM_API_KEY", "")
    or os.getenv("OPENAI_API_KEY", "")
    or os.getenv("GROQ_API_KEY", "")
)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")

PROVIDER_DEFAULTS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.3-70b-versatile",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "llama3.2",
    },
}

# ---------------------------------------------------------------------------
# Skill taxonomy (canonical lowercase names) used by the heuristic extractor.
# Ambiguous single-letter / ultra-short tokens ("c", "r", "go") are
# deliberately excluded to avoid false positives.
# ---------------------------------------------------------------------------
SKILL_TAXONOMY = list(
    dict.fromkeys(
        [
            # Programming languages
            "python", "java", "javascript", "typescript", "c#", "c++",
            "golang", "ruby", "php", "kotlin", "swift", "rust", "scala",
            "matlab", "sql", "pl/sql", "html", "css", "bash",
            "shell scripting", "vba",
            # Testing & QA
            "selenium", "pytest", "unittest", "testng", "junit", "cypress",
            "playwright", "puppeteer", "appium", "robot framework",
            "api testing", "rest assured", "postman", "soapui", "jmeter",
            "load testing", "performance testing", "manual testing",
            "automation testing", "test automation", "regression testing",
            "unit testing", "integration testing", "smoke testing",
            "sanity testing", "uat", "test cases", "test plans",
            "test scenarios", "bug tracking", "defect management",
            "gherkin", "cucumber", "allure", "sdet", "istqb",
            # Web frameworks
            "react", "angular", "vue.js", "next.js", "django", "flask",
            "fastapi", "spring boot", "spring", "node.js", "express.js",
            ".net", "asp.net",
            # Databases
            "mysql", "postgresql", "mongodb", "sqlite", "oracle",
            "sql server", "redis", "dynamodb", "firebase",
            # DevOps & Cloud
            "git", "github", "gitlab", "bitbucket", "jenkins", "docker",
            "kubernetes", "ci/cd", "terraform", "ansible", "linux", "aws",
            "azure", "gcp", "amazon web services", "google cloud platform",
            "ec2", "s3", "lambda", "prometheus", "grafana", "nginx", "helm",
            # Data / ML
            "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
            "keras", "nlp", "computer vision", "machine learning",
            "deep learning", "data analysis", "data visualization",
            "power bi", "tableau", "excel", "spark", "hadoop", "etl",
            "airflow", "matplotlib",
            # Practices & tools
            "agile", "scrum", "kanban", "jira", "confluence", "rest api",
            "graphql", "grpc", "microservices", "oop", "data structures",
            "algorithms", "system design", "tdd", "bdd", "debugging",
        ]
    )
)

# Alias map: normalised token -> canonical skill name.
SKILL_ALIASES = {
    "js": "javascript",
    "node": "node.js",
    "nodejs": "node.js",
    "vue": "vue.js",
    "vuejs": "vue.js",
    "nextjs": "next.js",
    "dotnet": ".net",
    "golang": "go",
    "py.test": "pytest",
    "python3": "python",
    "restful api": "rest api",
    "rest apis": "rest api",
    "api test": "api testing",
    "api automation": "api testing",
    "selenium webdriver": "selenium",
    "webdriver": "selenium",
    "postgres": "postgresql",
    "mssql": "sql server",
    "microsoft sql server": "sql server",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "continuous integration": "ci/cd",
    "continuous delivery": "ci/cd",
    "ci cd": "ci/cd",
    "test driven development": "tdd",
    "behavior driven development": "bdd",
    "behaviour driven development": "bdd",
    "object oriented programming": "oop",
    "oops": "oop",
    "coffee script": "coffeescript",
}

# Groups of skills that are treated as evidence for one another when the
# exact skill is absent (e.g. "Postman" implies API-testing experience).
SYNONYM_GROUPS = [
    {"api testing", "rest api", "rest assured", "postman", "soapui"},
    {"git", "github", "gitlab", "bitbucket"},
    {"sql", "mysql", "postgresql", "sql server", "sqlite", "oracle"},
    {"aws", "amazon web services", "ec2", "s3", "lambda"},
    {"gcp", "google cloud platform"},
    {"ci/cd", "jenkins"},
    {"machine learning", "deep learning"},
]

# Fields of study commonly accepted as equivalent to a "Computer Science"
# style requirement (matched as substrings against education text).
RELATED_FIELD_KEYWORDS = [
    "computer science",
    "information technology",
    "software engineering",
    "computer engineering",
    "computer applications",
    "information systems",
    "artificial intelligence",
    "data science",
]

# Degree keywords used for education line detection.
DEGREE_KEYWORDS = [
    "ph.d", "phd", "m.tech", "mtech", "b.tech", "btech", "b.e.",
    "master of", "bachelor of", "master's", "bachelor's", "m.sc", "msc",
    "b.sc", "bsc", "mca", "bca", "mba", "diploma", "degree",
]
