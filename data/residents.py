# data/residents.py

RESIDENTS = [
    {"unit_id": 1, "name": "Vikash",  "email": "vikash@email.com",  "phone": "971-555-0101"},
    {"unit_id": 2, "name": "Sarah",   "email": "sarah@email.com",   "phone": "971-555-0102"},
    {"unit_id": 4, "name": "James",   "email": "james@email.com",   "phone": "971-555-0104"},
    {"unit_id": 5, "name": "Priya",   "email": "priya@email.com",   "phone": "971-555-0105"},
]

SUPPORT = {
    "phone":   "1-800-PROPERTY",
    "email":   "support@propertymanager.com",
    "hours":   "Mon–Fri, 9AM–6PM",
}

def verify_resident(unit_id: int, email: str) -> dict | None:
    """Returns resident if unit_id + email match, else None."""
    for r in RESIDENTS:
        if r["unit_id"] == unit_id and r["email"].lower() == email.lower():
            return r
    return None