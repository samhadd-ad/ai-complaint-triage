"""
Generate a synthetic inbox of customer emails for a taxi & limousine company.

Real customer emails contain personal information, so this project uses
realistic, generated examples instead. Each email has a category and an
urgency label so a model can be trained and evaluated.

Run:  python data/generate_data.py
"""

import csv
import random
from pathlib import Path

random.seed(7)
OUT = Path(__file__).parent / "emails.csv"

NAMES = ["Sarah", "Ahmed", "Lina", "Mark", "Priya", "Daniel", "Maya", "Omar", "Chen", "Julia",
         "Carlos", "Emma", "Rami", "Noah", "Fatima", "Liam", "Grace", "Hassan", "Olivia", "Yusuf"]
PLACES = ["Pearson Airport", "Union Station", "downtown Toronto", "Mississauga", "the hotel",
          "Terminal 1", "Terminal 3", "my office", "Square One", "North York"]
TIMES = ["5 am", "6:30 this morning", "last night", "yesterday afternoon", "Friday evening",
         "this morning", "Sunday", "around 11 pm"]

TEMPLATES = {
    "Late Pickup": [
        "My driver was {n} minutes late picking me up at {place}. I almost missed my flight.",
        "I booked a car for {time} but nobody showed up until {n} minutes later.",
        "Waited at {place} for over {n} minutes, the driver never called. Very disappointing.",
        "The pickup at {place} was late again. This is the second time this month.",
        "Our limo arrived {n} minutes after the scheduled time and we were late to the wedding.",
        "Nobody was there when I came out of arrivals at {place}. I had to take another cab.",
        "You promised the car at {time}, it came way after. I lost an important meeting.",
        "Driver showed up so late that I had to rush through security. Not ok.",
    ],
    "Billing Issue": [
        "I was charged twice for my trip from {place} {time}. Please refund the extra charge.",
        "The fare on my receipt is ${amt} but I was quoted ${amt2}. Why the difference?",
        "My credit card shows a charge of ${amt} for a ride I never took.",
        "Can you explain the extra fee on my invoice? I paid ${amt} instead of ${amt2}.",
        "I need a corrected receipt for my business trip, the amount is wrong.",
        "Something is off with my statement, there are two payments for one ride.",
        "I paid cash but you still billed my card ${amt}.",
        "The price on the app and the final price do not match at all.",
    ],
    "Driver Behaviour": [
        "The driver was rude to me and refused to help with my luggage at {place}.",
        "My driver was on the phone the whole ride and was speeding on the highway.",
        "I felt unsafe, the driver was driving aggressively {time}.",
        "The driver smelled of smoke and was very unprofessional.",
        "The driver took a much longer route from {place} and argued when I asked about it.",
        "Your chauffeur yelled at my elderly mother when she was slow getting in.",
        "He kept texting while driving through {place}, I was scared the whole time.",
        "Very impolite driver, he did not even say hello and slammed the trunk.",
    ],
    "Lost Item": [
        "I left my laptop bag in the car {time} after a ride from {place}. Please help.",
        "I think I forgot my phone in the back seat of the taxi from {place}.",
        "My daughter left her backpack in the limo {time}. How can we get it back?",
        "Lost my wallet during my trip to {place}, can you check with the driver?",
        "I left a black suitcase in the trunk {time}. It has important documents.",
        "My keys must have fallen out in the car, I can't find them anywhere since {time}.",
        "There is a blue umbrella and a gift bag that I forgot in the vehicle.",
        "Did any driver find a pair of glasses? I had them before the ride to {place}.",
    ],
    "Booking Change": [
        "Can I change my pickup time tomorrow from {time} to a later time?",
        "I need to cancel my booking for Friday to {place}.",
        "Please update my reservation, my flight now lands at Terminal 3 instead of Terminal 1.",
        "Is it possible to add a stop at {place} on my booking?",
        "I would like to book a car for 6 people next Saturday from {place}.",
        "Our plans changed, we now need the car on Thursday instead of Wednesday.",
        "Please move my airport ride one hour earlier.",
        "Can I switch my reservation to a bigger vehicle for {place}?",
    ],
    "Compliment": [
        "Just wanted to say {name}, my driver, was excellent and very friendly. Thank you!",
        "Great service {time}, the car was clean and on time. I will book again.",
        "Thank you for getting me to {place} so quickly. Amazing driver.",
        "Your team was very helpful when I changed my booking. Much appreciated.",
        "The limo for our event was perfect. Everyone loved it.",
        "Five stars! Smooth ride, friendly chauffeur and a spotless car.",
        "I really appreciated how patient the driver was with my kids.",
        "Best airport transfer I've had in years, thank you {name}.",
    ],
}

URGENT_ADDONS = [
    " This is unacceptable and I want a refund immediately.",
    " I need this resolved today.",
    " I will file a formal complaint if this is not fixed.",
    " It is urgent, please call me back as soon as possible.",
    " I felt unsafe and I want someone to contact me right away.",
]
CONTEXT = [
    "I'm a regular customer and usually book through the app.",
    "My booking reference is in the confirmation email.",
    "I travel for work every week with your company.",
    "This was for a trip with my family.",
]
CLOSINGS = ["", " Thanks.", " Regards.", " Please get back to me.", " Thank you for your help."]

# Categories where urgent wording is realistic
URGENT_PROB = {"Late Pickup": 0.35, "Billing Issue": 0.35, "Driver Behaviour": 0.45,
               "Lost Item": 0.45, "Booking Change": 0.10, "Compliment": 0.0}
SIZES = {"Late Pickup": 260, "Billing Issue": 220, "Driver Behaviour": 170,
         "Lost Item": 140, "Booking Change": 230, "Compliment": 130}


def make_email(category: str) -> dict:
    t_idx = random.randrange(len(TEMPLATES[category]))
    text = TEMPLATES[category][t_idx].format(
        n=random.choice([15, 20, 25, 30, 40, 45, 60]),
        place=random.choice(PLACES), time=random.choice(TIMES),
        amt=random.choice([48, 65, 72, 89, 120, 150]),
        amt2=random.choice([40, 55, 60, 75, 95, 110]),
        name=random.choice(NAMES),
    )
    urgent = random.random() < URGENT_PROB[category]
    if urgent:
        text += random.choice(URGENT_ADDONS)
    # Safety issues are always urgent, even without urgent wording
    if any(w in text.lower() for w in ("unsafe", "speeding", "aggressively")):
        urgent = True
    text = f"Hi, {text}{random.choice(CLOSINGS)} - {random.choice(NAMES)}"
    if random.random() < 0.15:  # real emails often add unrelated context
        text = random.choice(CONTEXT) + " " + text
    return {"text": text, "category": category, "urgency": "High" if urgent else "Normal",
            "template_id": f"{category}-{t_idx}"}


def main() -> None:
    rows = [make_email(c) for c, n in SIZES.items() for _ in range(n)]
    random.shuffle(rows)
    for i, r in enumerate(rows, 1):
        r["email_id"] = f"E{i:04d}"
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["email_id", "text", "category", "urgency", "template_id"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} emails to {OUT}")


if __name__ == "__main__":
    main()
