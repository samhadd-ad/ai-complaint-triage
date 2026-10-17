import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from triage.drafts import draft_reply, template_reply
from triage.urgency import detect_urgency


def test_safety_words_are_always_urgent():
    level, reasons = detect_urgency("The driver was speeding and I felt unsafe.")
    assert level == "High"
    assert "unsafe" in reasons and "speeding" in reasons


def test_normal_email_is_not_urgent():
    assert detect_urgency("Can I move my pickup to 7 pm on Friday?")[0] == "Normal"


def test_whole_words_only():
    # "dangerous" contains "danger" but "endangered" should not trigger on a partial match of other words
    assert detect_urgency("We saw an endangered bird.")[0] == "Normal"


def test_template_reply_uses_policy_and_urgency():
    reply = template_reply("Billing Issue", "High")
    assert "refunded" in reply
    assert "call you today" in reply


def test_draft_falls_back_to_template_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    text, source = draft_reply("I left my phone in the car.", "Lost Item", "Normal")
    assert source == "Template"
    assert "Lost items" in text
