# agent.py
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from dotenv import load_dotenv
from tools.unit_search import search_units
from tools.book_tour import book_tour

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
tools = [search_units, book_tour]
llm_with_tools = llm.bind_tools(tools)
tool_map = {"search_units": search_units, "book_tour": book_tour}

# ── Conversation loop ──────────────────────────────────────
print("\n🏠 Property Agent ready! Type 'quit' to exit.\n")

message_history = []

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "quit":
        print("Goodbye!")
        break

    message_history.append(HumanMessage(user_input))
    response = llm_with_tools.invoke(message_history)
    message_history.append(response)

    # ── Tool call handling ─────────────────────────────────
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            print(f"\n[calling {tool_name} with {tool_args}]")

            result = tool_map[tool_name].invoke(tool_args)

            message_history.append(
                ToolMessage(content=result, tool_call_id=tool_call["id"])
            )

        # Get final response after tool execution
        final_response = llm_with_tools.invoke(message_history)
        message_history.append(final_response)
        print(f"\nAgent: {final_response.content}\n")

    else:
        print(f"\nAgent: {response.content}\n")