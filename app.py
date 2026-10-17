"""
AI Complaint Triage: Streamlit review app.

Run:  streamlit run app.py

1. Load an inbox (sample emails, a CSV upload, or a single pasted email)
2. Each email gets a category, a confidence score and an urgency flag
3. Low-confidence emails are sent to "Needs review" instead of being trusted blindly
4. Staff open an email, edit the draft reply, and approve it (human in the loop)
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from triage import classifier
from triage.drafts import draft_reply
from triage.urgency import detect_urgency

ROOT = Path(__file__).parent
SAMPLE = ROOT / "data" / "emails.csv"
CONFIDENCE_THRESHOLD = 0.60

st.set_page_config(page_title="AI Complaint Triage", page_icon="📨", layout="wide")


@st.cache_resource
def get_model():
    return classifier.load()


def triage(texts: list[str]) -> pd.DataFrame:
    model = get_model()
    rows = []
    for text, (cat, conf) in zip(texts, classifier.predict(model, texts)):
        urgency, reasons = detect_urgency(text)
        rows.append({
            "Email": text,
            "Category": cat if conf >= CONFIDENCE_THRESHOLD else "Needs review",
            "Best guess": cat,
            "Confidence": round(conf, 2),
            "Urgency": urgency,
            "Why urgent": ", ".join(reasons),
        })
    df = pd.DataFrame(rows)
    # Urgent first, then least confident first
    return df.sort_values(["Urgency", "Confidence"], ascending=[True, True]).reset_index(drop=True)


st.title("📨 AI Complaint Triage")
st.caption("Sorts customer emails by type and urgency, and drafts a reply for staff to approve.")

try:
    get_model()
except FileNotFoundError as e:
    st.error(f"{e}  (first run `python data/generate_data.py`)")
    st.stop()

# ---------- 1. Inbox ----------
source = st.sidebar.radio("Inbox source", ["Sample inbox", "Upload CSV", "Paste one email"])
if source == "Sample inbox":
    n = st.sidebar.slider("Number of emails", 10, 100, 30)
    texts = pd.read_csv(SAMPLE)["text"].head(n).tolist()
elif source == "Upload CSV":
    up = st.sidebar.file_uploader("CSV with a 'text' column", type="csv")
    if not up:
        st.info("Upload a CSV with a column named `text` (one email per row).")
        st.stop()
    texts = pd.read_csv(up)["text"].dropna().astype(str).tolist()
else:
    one = st.sidebar.text_area("Email text", "Hi, I was charged twice for my ride yesterday. "
                                              "Please refund it today. - Maya")
    texts = [one] if one.strip() else []
    if not texts:
        st.stop()

df = triage(texts)

# ---------- 2. KPIs ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Emails", len(df))
c2.metric("Urgent", int((df["Urgency"] == "High").sum()))
c3.metric("Complaints", int(df["Category"].isin(
    ["Late Pickup", "Billing Issue", "Driver Behaviour", "Lost Item"]).sum()))
c4.metric("Needs human review", int((df["Category"] == "Needs review").sum()))

left, right = st.columns([3, 2])
with left:
    st.subheader("Inbox (urgent first)")
    st.dataframe(df[["Urgency", "Category", "Confidence", "Email"]], width="stretch", height=380)
with right:
    st.subheader("By category")
    st.bar_chart(df["Category"].value_counts())

# ---------- 3. Review & approve ----------
st.subheader("Review an email")
idx = st.selectbox("Choose an email", df.index,
                   format_func=lambda i: f"[{df.at[i, 'Urgency']}] {df.at[i, 'Category']}: {df.at[i, 'Email'][:70]}…")
row = df.loc[idx]
st.write(f"**Email:** {row['Email']}")
st.write(f"**Predicted:** {row['Best guess']} ({row['Confidence']:.0%} confident) · "
         f"**Urgency:** {row['Urgency']}" + (f" ({row['Why urgent']})" if row["Why urgent"] else ""))

category = st.selectbox("Confirm or correct the category", list(get_model().classes_),
                        index=list(get_model().classes_).index(row["Best guess"]))
draft, source_used = draft_reply(row["Email"], category, row["Urgency"])
reply = st.text_area(f"Draft reply ({source_used}) — edit before sending", draft, height=200)
if st.button("✅ Approve reply"):
    st.success("Reply approved. In a real system it would now be sent and logged.")
