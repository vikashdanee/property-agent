# graph/nodes.py
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from graph.state import AgentState
from tools.unit_search import search_units
from tools.book_tour import book_tour
from tools.maintenance_ticket import maintenance_ticket
from tools.verify_resident import verify_resident
from data.residents import SUPPORT
import os

# ── Tool sets ──────────────────────────────────────────────
applicant_tools = [search_units, book_tour]
resident_tools  = [verify_resident, maintenance_ticket]

# ── System prompts ─────────────────────────────────────────
IDENTIFY_PROMPT = SystemMessage(content="""You are a friendly property management assistant.
Your ONLY job is to ask whether the user is a new applicant or current resident.
Ask warmly and wait for their answer. Do nothing else.""")

APPLICANT_PROMPT = SystemMessage(content="""You are a property management assistant for new applicants.

You have EXACTLY two tools:
1. search_units — call this when user wants to see available units
2. book_tour — call this when user wants to book a viewing

STRICT RULES:
- When user mentions bedrooms AND budget → call search_units IMMEDIATELY. No questions.
- When user wants to book → collect name, day, time, and optionally email → call book_tour.
- Ask for email address when booking — say it's for the confirmation email.
- NEVER say you don't have access to inventory. You DO have access via search_units tool.
- Only collect: bedrooms (required), max_rent (required), location (optional).""")

RESIDENT_PROMPT = SystemMessage(content="""You are a property management assistant for residents.

STRICT RULES:
- Ask for unit number and email address to verify identity.
- As soon as you have BOTH unit number and email → call verify_resident tool immediately.
- After verified → use the resident's email for maintenance_ticket confirmation emails.
- After VERIFIED state is True → use maintenance_ticket tool for any issues reported.
- Do NOT ask for anything else before verifying.
- After 3 failed verifications → stop and tell user to contact support.""")

# ── LLM factory — created fresh each time to pick up env vars ──
def get_llm():
    return ChatAnthropic(
        model="claude-sonnet-4-5",
        temperature=0,
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

def get_applicant_llm():
    return get_llm().bind_tools(applicant_tools)

def get_resident_llm():
    return get_llm().bind_tools(resident_tools)

# ── Classification ─────────────────────────────────────────
def classify_user_type(messages) -> str | None:
    all_text = " ".join(
        m.content for m in messages
        if hasattr(m, "content") and isinstance(m.content, str)
    )
    if not all_text.strip():
        return None

    classification_prompt = [
        SystemMessage(content="""Classify the user as exactly one of:
- applicant: looking to rent, find a unit, new, searching
- resident: current tenant, lives there, maintenance, repair, my unit
- unknown: not clear yet

Reply with ONLY one word: applicant, resident, or unknown."""),
        HumanMessage(content=all_text)
    ]

    result = get_llm().invoke(classification_prompt)
    answer = result.content.strip().lower()

    if "applicant" in answer:
        return "applicant"
    elif "resident" in answer:
        return "resident"
    return None

# ── Nodes ──────────────────────────────────────────────────
def identify_node(state: AgentState):
    messages  = [IDENTIFY_PROMPT] + state["messages"]
    response  = get_llm().invoke(messages)
    user_type = classify_user_type(state["messages"])
    return {"messages": [response], "user_type": user_type}

def applicant_node(state: AgentState):
    messages = [APPLICANT_PROMPT] + state["messages"]
    response = get_applicant_llm().invoke(messages)
    return {"messages": [response]}

def resident_node(state: AgentState):
    verified   = state.get("verified", False)
    name       = state.get("resident_name", "")
    unit_id    = state.get("resident_unit_id", "")

    status_msg = ""
    if verified:
        status_msg = f"\n\nCURRENT STATE: Resident is VERIFIED. Name={name}, Unit={unit_id}. You MUST use maintenance_ticket tool for any issues reported."
    else:
        attempts   = state.get("verify_attempts", 0)
        status_msg = f"\n\nCURRENT STATE: NOT verified yet. Attempts={attempts}. Ask for unit number and email."

    prompt    = SystemMessage(content=RESIDENT_PROMPT.content + status_msg)
    messages  = [prompt] + state["messages"]
    response  = get_resident_llm().invoke(messages)
    new_attempts = state.get("verify_attempts", 0)

    if response.tool_calls:
        for tc in response.tool_calls:
            if tc["name"] == "verify_resident":
                new_attempts += 1

    return {
        "messages":         [response],
        "verified":         verified,
        "verify_attempts":  new_attempts,
        "resident_name":    name,
        "resident_unit_id": unit_id,
    }

def resident_tool_node(state: AgentState):
    from langgraph.prebuilt import ToolNode
    tool_node = ToolNode(resident_tools)
    result    = tool_node.invoke(state)

    new_verified = state.get("verified", False)
    new_name     = state.get("resident_name")
    new_unit_id  = state.get("resident_unit_id")

    for msg in result.get("messages", []):
        content = str(msg.content) if hasattr(msg, "content") else ""
        if "VERIFIED:" in content:
            parts        = content.split(":")
            new_verified = True
            new_name     = parts[1]
            new_unit_id  = int(parts[2])

    return {
        "messages":         result["messages"],
        "verified":         new_verified,
        "resident_name":    new_name,
        "resident_unit_id": new_unit_id,
    }

def support_node(state: AgentState):
    msg = AIMessage(content=(
        f"I'm really sorry, I wasn't able to verify your identity. 😔\n\n"
        f"Please contact our support team directly:\n\n"
        f"📞 Phone : {SUPPORT['phone']}\n"
        f"📧 Email : {SUPPORT['email']}\n"
        f"🕐 Hours : {SUPPORT['hours']}\n\n"
        f"We apologise for the inconvenience!"
    ))
    return {"messages": [msg]}