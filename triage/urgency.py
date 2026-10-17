"""
Rule-based urgency detection.

Urgency uses transparent keyword rules (not a black-box model) so staff can
see exactly why an email was flagged. Safety words always mean High urgency.
"""

import re

SAFETY_WORDS = ["unsafe", "accident", "speeding", "aggressive", "aggressively", "danger", "injured"]
URGENT_PHRASES = [
    "immediately", "urgent", "today", "as soon as possible", "right away",
    "formal complaint", "unacceptable", "refund", "call me back",
]


def detect_urgency(text: str) -> tuple[str, list[str]]:
    """Return ("High" | "Normal", reasons)."""
    lowered = text.lower()
    reasons = [w for w in SAFETY_WORDS if re.search(rf"\b{re.escape(w)}\b", lowered)]
    reasons += [p for p in URGENT_PHRASES if p in lowered]
    return ("High" if reasons else "Normal"), reasons
