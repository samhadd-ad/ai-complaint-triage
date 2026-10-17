"""
Draft a reply for staff to review.

- Default: a template reply built from the company policy (works offline, no API key).
- Optional: if ANTHROPIC_API_KEY is set and the `anthropic` package is installed,
  an LLM writes the reply using ONLY the policy text as context.

Either way, a human approves the draft before anything is sent.
"""

import os

from .policies import POLICIES

OPENINGS = {
    "Late Pickup": "I'm sorry your driver was late. That is not the service we aim for.",
    "Billing Issue": "Thank you for flagging this charge. I understand how frustrating billing errors are.",
    "Driver Behaviour": "Thank you for reporting this. Your safety and comfort are our top priority.",
    "Lost Item": "I'm sorry you left something behind. We'll do our best to get it back to you.",
    "Booking Change": "Thanks for reaching out about your booking.",
    "Compliment": "Thank you so much for your kind words!",
}


def template_reply(category: str, urgency: str) -> str:
    policy = POLICIES.get(category, "")
    urgent_line = "\n\nBecause this is urgent, a team member will call you today." if urgency == "High" else ""
    return (
        f"Hello,\n\n{OPENINGS.get(category, 'Thank you for contacting us.')}\n\n"
        f"{policy}{urgent_line}\n\nBest regards,\nCustomer Care Team"
    )


def llm_reply(email: str, category: str, urgency: str, model: str = "claude-sonnet-5") -> str | None:
    """Return an LLM-written draft, or None if no API key / package is available."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
    except ImportError:
        return None
    prompt = (
        "You are a customer care agent for a taxi and limousine company. Write a short, polite "
        "reply (under 120 words) to the customer email below. Only promise what the policy says. "
        "Do not invent refunds, amounts or dates.\n\n"
        f"Category: {category}\nUrgency: {urgency}\nPolicy: {POLICIES.get(category, '')}\n\n"
        f"Customer email:\n{email}"
    )
    client = anthropic.Anthropic()
    msg = client.messages.create(model=model, max_tokens=400,
                                 messages=[{"role": "user", "content": prompt}])
    return msg.content[0].text


def draft_reply(email: str, category: str, urgency: str) -> tuple[str, str]:
    """Return (draft, source) where source is 'LLM' or 'Template'."""
    try:
        text = llm_reply(email, category, urgency)
        if text:
            return text, "LLM"
    except Exception:  # network/API errors fall back to the safe template
        pass
    return template_reply(category, urgency), "Template"
