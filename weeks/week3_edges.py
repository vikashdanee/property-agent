# graph/edges.py
from langgraph.graph import END
from graph.state import AgentState

MAX_ATTEMPTS = 3

def route_by_user_type(state: AgentState):
    user_type = state.get("user_type")
    if user_type == "applicant":
        return "applicant"
    elif user_type == "resident":
        return "resident"
    return END

def route_applicant(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "applicant_tools"
    return END

def route_resident(state: AgentState):
    last     = state["messages"][-1]
    attempts = state.get("verify_attempts", 0)
    verified = state.get("verified", False)
    if attempts >= MAX_ATTEMPTS and not verified:
        return "support"
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "resident_tools"
    return END