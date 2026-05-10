# tools/verify_resident.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from data.residents import verify_resident as check_resident

class VerifyResidentInput(BaseModel):
    unit_id: int = Field(description="The resident's unit number")
    email:   str = Field(description="The resident's email address")

@tool("verify_resident", args_schema=VerifyResidentInput)
def verify_resident(unit_id: int, email: str) -> str:
    """Verify a resident by their unit number and email address.
    Use this when a resident provides their unit and email to authenticate."""
    resident = check_resident(unit_id, email)
    if resident:
        return f"VERIFIED:{resident['name']}:{unit_id}"
    return "FAILED"