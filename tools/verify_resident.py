# tools/verify_resident.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from database.connection import get_db_session
from database.models import Resident

class VerifyResidentInput(BaseModel):
    unit_id: int = Field(description="The resident's unit number")
    email:   str = Field(description="The resident's email address")

@tool("verify_resident", args_schema=VerifyResidentInput)
def verify_resident(unit_id: int, email: str) -> str:
    """Verify a resident by their unit number and email address.
    Use this when a resident provides their unit and email to authenticate."""
    db = get_db_session()
    try:
        resident = db.query(Resident).filter(
            Resident.unit_id == unit_id,
            Resident.email   == email.lower()
        ).first()

        if resident:
            return f"VERIFIED:{resident.name}:{unit_id}"
        return "FAILED"
    finally:
        db.close()