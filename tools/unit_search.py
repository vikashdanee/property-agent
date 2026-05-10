# tools/unit_search.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
import json

MOCK_UNITS = [
    {"id": 1, "beds": 2, "rent": 1400, "location": "downtown", "available": True},
    {"id": 2, "beds": 1, "rent": 950,  "location": "midtown",  "available": True},
    {"id": 3, "beds": 3, "rent": 2100, "location": "downtown", "available": False},
    {"id": 4, "beds": 2, "rent": 1350, "location": "uptown",   "available": True},
    {"id": 5, "beds": 1, "rent": 870,  "location": "downtown", "available": True},
]

class UnitSearchInput(BaseModel):
    bedrooms: int           = Field(description="Number of bedrooms required")
    max_rent: float         = Field(description="Maximum monthly rent in USD")
    location: Optional[str] = Field(None, description="Area name, optional")

@tool("search_units", args_schema=UnitSearchInput)
def search_units(bedrooms: int, max_rent: float, location: Optional[str] = None) -> str:
    """Search available rental units. Use when the user asks about units,
    apartments, or properties to rent. Returns matching available units."""
    results = [
        u for u in MOCK_UNITS
        if u["beds"] == bedrooms
        and u["rent"] <= max_rent
        and u["available"]
        and (not location or location.lower() in u["location"])
    ]
    if not results:
        return "No units found matching those criteria. Try relaxing the filters."
    return json.dumps(results, indent=2)