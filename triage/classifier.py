"""
Complaint category classifier: TF-IDF features + Logistic Regression.

A simple, fast and explainable baseline: you can inspect which words push an
email towards each category. Swap in an LLM later if needed.
"""

from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "classifier.joblib"


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", FeatureUnion([
            # whole words and word pairs ("refund", "late pickup")
            ("words", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words="english")),
            # word pieces, so new wordings still match ("charged" ~ "charge", "rude" ~ "rudely")
            ("chars", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)),
        ])),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ])


def save(model: Pipeline, path: Path = MODEL_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load(path: Path = MODEL_PATH) -> Pipeline:
    if not path.exists():
        raise FileNotFoundError("No trained model found. Run:  python train.py")
    return joblib.load(path)


def predict(model: Pipeline, texts: list[str]) -> list[tuple[str, float]]:
    """Return (category, confidence) for each text."""
    proba = model.predict_proba(texts)
    classes = model.classes_
    return [(classes[i], float(p[i])) for p, i in zip(proba, np.argmax(proba, axis=1))]


def top_words(model: Pipeline, category: str, n: int = 8) -> list[str]:
    """Words that most strongly point to a category (explainability)."""
    union, clf = model.named_steps["tfidf"], model.named_steps["clf"]
    words = union.transformer_list[0][1]
    n_words = len(words.get_feature_names_out())
    idx = list(clf.classes_).index(category)
    coefs = clf.coef_[idx][:n_words]  # word features come first in the union
    terms = words.get_feature_names_out()
    return [terms[i] for i in np.argsort(coefs)[::-1][:n]]
