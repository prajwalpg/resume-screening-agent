"""Semantic similarity engine.

Primary backend : Sentence Transformers ("all-MiniLM-L6-v2")
Fallback backend: TF-IDF + cosine similarity (scikit-learn)

The fallback keeps the agent fully runnable on machines where the
pre-trained transformer model cannot be downloaded (offline sandboxes,
CI environments) while keeping behaviour deterministic on a given
machine + backend combination.
"""

from typing import List, Sequence


import os


class SimilarityEngine:
    """Computes cosine similarity between a JD and many resumes."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", prefer_transformers: Optional[bool] = None) -> None:
        self.backend = "tfidf-cosine (fallback)"
        self._model = None

        if prefer_transformers is None:
            if os.getenv("RENDER") or os.getenv("DISABLE_TRANSFORMERS", "").lower() in ("true", "1", "yes"):
                prefer_transformers = False
            else:
                prefer_transformers = True

        if prefer_transformers:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore

                self._model = SentenceTransformer(model_name)
                self.backend = f"sentence-transformers/{model_name}"
            except Exception:
                self._model = None

    # ------------------------------------------------------------------
    def similarities(self, jd_text: str, resume_texts: Sequence[str]) -> List[float]:
        """Return one similarity score (0..1) per resume text."""
        if not resume_texts:
            return []

        if self._model is not None:
            from sklearn.metrics.pairwise import cosine_similarity

            vectors = self._model.encode([jd_text] + list(resume_texts))
            sims = cosine_similarity([vectors[0]], vectors[1:])[0]
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            try:
                matrix = TfidfVectorizer(stop_words="english").fit_transform(
                    [jd_text] + list(resume_texts)
                )
            except ValueError:  # Empty vocabulary (all texts empty).
                return [0.0] * len(resume_texts)
            sims = cosine_similarity(matrix[0], matrix[1:])[0]

        return [max(0.0, min(1.0, float(score))) for score in sims]

    def similarity(self, jd_text: str, resume_text: str) -> float:
        return self.similarities(jd_text, [resume_text])[0]
