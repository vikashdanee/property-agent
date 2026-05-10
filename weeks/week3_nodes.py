# graph/nodes.py
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from graph.state import AgentState
from tools.unit_search import search_units
from tools.book_tour import book_tour
from tools.maintenance_ticket import maintenance_ticket
from tools.verify_resident import verify_resident
from data.residents import SUPPORT

llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)

applicant_tools = [search_units, book_tour]
resident_tools  = [verify_resident, maintenance_ticket]

applicant_llm = ChatAnthropic(
    model="claude-sonnet-4-5", temperature=0
).bind_tools(applicant_tools)

resident_llm = ChatAnthropic(
    model="claude-sonnet-4-5", temperature=0
).bind_tools(resident_tools)

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
- When user wants to book → call book_tour IMMEDIATELY.
- NEVER say you don't have access to inventory. You DO have access via search_units tool.
- NEVER ask for move-in date, pets, amenities — not in the system.
- Only collect: bedrooms (required), max_rent (required), location (optional).
- If you have bedrooms and budget → call the tool RIGHT NOW. Stop asking questions.""")

RESIDENT_PROMPT = SystemMessage(content="""You are a property management assistant for current residents.

STRICT RULES:
- Ask for unit number and email to verify identity.
- Call verify_resident tool as soon as you have BOTH unit number AND email.
- After VERIFIED state is True, you MUST use maintenance_ticket tool for any issues.
- When submitting maintenance: use the verified resident's unit_id and name from state.
- NEVER say you cannot submit — you have the maintenance_ticket tool, use it.
- Do not ask for confirmation before submitting — just call the tool immediately.
- Priority is auto-assigned — do not ask the user about priority.""")

# ── Classification using LLM ───────────────────────────────
def classify_user_type(messages) -> str | None:
    """Use LLM to classify user as applicant, resident or unknown."""
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

    result = llm.invoke(classification_prompt)
    answer = result.content.strip().lower()

    if "applicant" in answer:
        return "applicant"
    elif "resident" in answer:
        return "resident"
    return None

# ── Nodes ──────────────────────────────────────────────────
def identify_node(state: AgentState):
    """Classify user type — ask if not clear yet."""
    user_type = classify_user_type(state["messages"])

    if user_type:
        # Already classified — return silently, let routing handle it
        return {"user_type": user_type}

    # Not clear yet — ask the question
    messages = [IDENTIFY_PROMPT] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response], "user_type": None}

def applicant_node(state: AgentState):
    """Handles new applicant — search units and book tours."""
    messages = [APPLICANT_PROMPT] + state["messages"]
    response = applicant_llm.invoke(messages)
    return {"messages": [response]}

def resident_node(state: AgentState):
    """Handles resident — verify then allow maintenance tickets."""
    verified   = state.get("verified", False)
    name       = state.get("resident_name", "")
    unit_id    = state.get("resident_unit_id", "")

    # Tell LLM current verification status explicitly
    status_msg = ""
    if verified:
        status_msg = f"\n\nCURRENT STATE: Resident is VERIFIED. Name={name}, Unit={unit_id}. You MUST use maintenance_ticket tool for any issues reported."
    else:
        attempts = state.get("verify_attempts", 0)
        status_msg = f"\n\nCURRENT STATE: NOT verified yet. Attempts={attempts}. Ask for unit number and email."

    prompt = SystemMessage(content=RESIDENT_PROMPT.content + status_msg)
    messages  = [prompt] + state["messages"]
    response  = resident_llm.invoke(messages)
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
    """Executes resident tools and updates verified status."""
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
    """Shown after 3 failed verification attempts."""
    msg = AIMessage(content=(
        f"I'm really sorry, I wasn't able to verify your identity. 😔\n\n"
        f"Please contact our support team directly:\n\n"
        f"📞 Phone : {SUPPORT['phone']}\n"
        f"📧 Email : {SUPPORT['email']}\n"
        f"🕐 Hours : {SUPPORT['hours']}\n\n"
        f"We apologise for the inconvenience!"
    ))
    return {"messages": [msg]}