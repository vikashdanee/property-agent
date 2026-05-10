# graph/state.py
from langgraph.graph import MessagesState
from typing import Optional

class AgentState(MessagesState):
    user_type:        Optional[str] = None   # "applicant" or "resident"
    verified:         bool          = False
    verify_attempts:  int           = 0
    resident_unit_id: Optional[int] = None
    resident_name:    Optional[str] = None