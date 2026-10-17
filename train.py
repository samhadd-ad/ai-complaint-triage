"""
Train and evaluate the complaint classifier.

Run:  python train.py
Outputs:
  models/classifier.joblib      trained model used by the app
  reports/metrics.md            accuracy, per-category scores, urgency rule accuracy
  reports/confusion_matrix.png  where the model gets confused
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report
from sklearn.model_selection import train_test_split

from triage import classifier
from triage.urgency import detect_urgency

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "emails.csv"
REPORTS = ROOT / "reports"


def main() -> None:
    if not DATA.exists():
        raise SystemExit("No data found. Run:  python data/generate_data.py")
    df = pd.read_csv(DATA)

    # 1) Naive random split: test emails share sentence templates with training emails,
    #    so the score is too optimistic (the model can memorise templates).
    Xa, Xb, ya, yb = train_test_split(df["text"], df["category"], test_size=0.25,
                                      random_state=42, stratify=df["category"])
    naive_acc = accuracy_score(yb, classifier.build_pipeline().fit(Xa, ya).predict(Xb))

    # 2) Honest split: whole templates are held out, so the test set only contains
    #    wordings the model has never seen. This is the number we report.
    #    2 templates per category are held out, so every category is tested fairly.
    rng = np.random.default_rng(3)
    held_out = set()
    for cat, ids in df.groupby("category")["template_id"].unique().items():
        held_out.update(rng.choice(sorted(ids), size=2, replace=False))
    is_test = df["template_id"].isin(held_out)
    X_train, X_test = df.loc[~is_test, "text"], df.loc[is_test, "text"]
    y_train, y_test = df.loc[~is_test, "category"], df.loc[is_test, "category"]

    model = classifier.build_pipeline().fit(X_train, y_train)
    pred = model.predict(X_test)
    acc = accuracy_score(y_test, pred)
    report = classification_report(y_test, pred, digits=3, zero_division=0)

    # Final model for the app is trained on all emails
    final_model = classifier.build_pipeline().fit(df["text"], df["category"])

    urgency_pred = df["text"].apply(lambda t: detect_urgency(t)[0])
    urgency_acc = (urgency_pred == df["urgency"]).mean()

    print(f"Emails: {len(df)}  (train {len(X_train)}, test {len(X_test)})")
    print(f"Random-split accuracy (optimistic): {naive_acc:.1%}")
    print(f"Unseen-wording accuracy (honest):   {acc:.1%}")
    print(report)
    print(f"Urgency rule accuracy: {urgency_acc:.1%}")

    classifier.save(final_model)
    REPORTS.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=ax, xticks_rotation=35, cmap="Blues", colorbar=False)
    ax.set_title("Confusion matrix on unseen wording (held-out templates)")
    fig.tight_layout()
    fig.savefig(REPORTS / "confusion_matrix.png", dpi=150)

    words = "\n".join(f"- **{c}:** {', '.join(classifier.top_words(final_model, c, 6))}" for c in final_model.classes_)
    (REPORTS / "metrics.md").write_text(
        f"# Model results\n\n- Emails: {len(df)} (train {len(X_train)}, test {len(X_test)})\n"
        f"- Random-split accuracy: {naive_acc:.1%} (optimistic: shares sentence templates with training)\n"
        f"- **Accuracy on unseen wording: {acc:.1%}** (whole templates held out)\n- **Urgency rule accuracy: {urgency_acc:.1%}**\n\n"
        f"## Per-category scores\n```\n{report}```\n\n## Words that drive each category\n{words}\n",
        encoding="utf-8")
    print(f"\nSaved model to {classifier.MODEL_PATH.relative_to(ROOT)} and reports to reports/")


if __name__ == "__main__":
    main()
