"""
Company policies used to draft replies.

This is a small "retrieval" step: the reply is grounded in the policy for the
predicted category, instead of being made up. With an LLM (see drafts.py), the
same policy text is passed as context, which is the idea behind RAG.
"""

POLICIES = {
    "Late Pickup": (
        "If a driver arrives more than 15 minutes late, the customer receives a 20% credit on "
        "the trip. Dispatch reviews the GPS log within 1 business day."
    ),
    "Billing Issue": (
        "Billing disputes are reviewed within 2 business days. Duplicate or incorrect charges "
        "are refunded to the original payment method in 5-7 business days."
    ),
    "Driver Behaviour": (
        "All driver behaviour reports are reviewed by the safety team. Safety-related reports "
        "are escalated to a manager the same day. The driver's AI dash-cam footage is checked."
    ),
    "Lost Item": (
        "Lost items are logged and the driver is contacted within 2 hours. Items can be picked "
        "up at the main office or delivered for a fee."
    ),
    "Booking Change": (
        "Bookings can be changed or cancelled free of charge up to 2 hours before pickup "
        "through the app, by phone, or by replying to the confirmation email."
    ),
    "Compliment": (
        "Compliments are shared with the driver and recorded for the monthly recognition program."
    ),
}
