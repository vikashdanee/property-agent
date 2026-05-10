# tools/unit_search.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
from database.connection import get_db_session
from database.models import Unit
import json

class UnitSearchInput(BaseModel):
    bedrooms: int           = Field(description="Number of bedrooms required")
    max_rent: float         = Field(description="Maximum monthly rent in USD")
    location: Optional[str] = Field(None, description="Area name, optional")

@tool("search_units", args_schema=UnitSearchInput)
def search_units(bedrooms: int, max_rent: float,
                 location: Optional[str] = None) -> str:
    """Search available rental units. Use when the user asks about units,
    apartments, or properties to rent. Returns matching available units."""
    db = get_db_session()
    try:
        query = db.query(Unit).filter(
            Unit.beds      == bedrooms,
            Unit.rent      <= max_rent,
            Unit.available == True
        )
        if location:
            query = query.filter(Unit.location.ilike(f"%{location}%"))

        units = query.all()

        if not units:
            return "No units found matching those criteria. Try relaxing the filters."

        results = [
            {
                "id":        u.id,
                "beds":      u.beds,
                "rent":      u.rent,
                "location":  u.location,
                "address":   u.address,
                "amenities": u.amenities,
                "available": u.available,
            }
            for u in units
        ]
        return json.dumps(results, indent=2)
    finally:
        db.close()