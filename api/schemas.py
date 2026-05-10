# api/schemas.py
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message:   str
    thread_id: str = "default"   # identifies the user session

class ChatResponse(BaseModel):
    reply:     str
    thread_id: str