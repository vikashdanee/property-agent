# tools/book_tour.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from tools.send_email import send_booking_confirmation
import json

BOOKINGS = []

AVAILABLE_SLOTS = [
    {"day": "Saturday", "time": "10:00 AM"},
    {"day": "Saturday", "time": "2:00 PM"},
    {"day": "Sunday",   "time": "11:00 AM"},
    {"day": "Sunday",   "time": "3:00 PM"},
    {"day": "Monday",   "time": "9:00 AM"},
]

class BookTourInput(BaseModel):
    unit_id: int           = Field(description="The ID of the unit to book a tour for")
    name:    str           = Field(description="Full name of the person booking")
    day:     str           = Field(description="Preferred day e.g. Saturday, Sunday, Monday")
    time:    str           = Field(description="Preferred time e.g. 10:00 AM, 2:00 PM")
    email:   Optional[str] = Field(None, description="Email address for confirmation")

@tool("book_tour", args_schema=BookTourInput)
def book_tour(unit_id: int, name: str, day: str,
              time: str, email: Optional[str] = None) -> str:
    """Book a property tour for a specific unit. Use when the user wants
    to schedule, arrange or book a tour or appointment for a unit."""

    slot_exists = any(
        s["day"].lower() == day.lower() and s["time"].lower() == time.lower()
        for s in AVAILABLE_SLOTS
    )
    if not slot_exists:
        available = ", ".join([f"{s['day']} {s['time']}" for s in AVAILABLE_SLOTS])
        return f"That slot is unavailable. Available slots: {available}"

    booking = {
        "booking_id": len(BOOKINGS) + 1,
        "unit_id":    unit_id,
        "name":       name,
        "day":        day,
        "time":       time,
        "status":     "confirmed"
    }
    BOOKINGS.append(booking)

    # Send confirmation email if provided
    email_sent = False
    if email:
        email_sent = send_booking_confirmation(
            to_email   = email,
            name       = name,
            unit_id    = unit_id,
            day        = day,
            time       = time,
            booking_id = booking["booking_id"]
        )

    result = {**booking, "email_sent": email_sent}
    return json.dumps(result, indent=2)