# tools/maintenance_ticket.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from tools.send_email import send_maintenance_confirmation
import json

TICKETS = []

PRIORITY_LEVELS = {
    "emergency": ["no water", "no heat", "flood", "fire", "gas leak", "no electricity"],
    "high":      ["broken lock", "broken door", "no hot water", "pest"],
    "medium":    ["broken appliance", "leak", "mold", "broken window", "cooktop"],
    "low":       ["paint", "carpet", "cosmetic", "noise"],
}

def assign_priority(issue: str) -> str:
    issue_lower = issue.lower()
    for priority, keywords in PRIORITY_LEVELS.items():
        if any(kw in issue_lower for kw in keywords):
            return priority
    return "medium"

class MaintenanceTicketInput(BaseModel):
    unit_id:     int           = Field(description="Unit ID where the issue is")
    tenant_name: str           = Field(description="Full name of the tenant")
    issue:       str           = Field(description="Description of the maintenance issue")
    email:       Optional[str] = Field(None, description="Tenant email for confirmation")
    contact:     Optional[str] = Field(None, description="Tenant phone number, optional")

@tool("maintenance_ticket", args_schema=MaintenanceTicketInput)
def maintenance_ticket(unit_id: int, tenant_name: str, issue: str,
                       email: Optional[str] = None,
                       contact: Optional[str] = None) -> str:
    """Create a maintenance ticket for a reported issue in a unit.
    Use when a tenant reports a problem, issue, repair need, or
    anything broken in their unit."""

    priority = assign_priority(issue)
    ticket = {
        "ticket_id":   len(TICKETS) + 1,
        "unit_id":     unit_id,
        "tenant_name": tenant_name,
        "issue":       issue,
        "priority":    priority,
        "contact":     contact,
        "status":      "open",
    }
    TICKETS.append(ticket)

    # Send confirmation email if provided
    email_sent = False
    if email:
        email_sent = send_maintenance_confirmation(
            to_email  = email,
            name      = tenant_name,
            unit_id   = unit_id,
            issue     = issue,
            priority  = priority,
            ticket_id = ticket["ticket_id"]
        )

    result = {**ticket, "email_sent": email_sent}
    return json.dumps(result, indent=2)