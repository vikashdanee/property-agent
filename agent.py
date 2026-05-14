# agent.py
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage
from graph.builder import build_graph
import uuid

app    = build_graph()

# Fresh session every run for testing
# Change to a fixed ID like "user_001" for persistent memory
config = {"configurable": {"thread_id": str(uuid.uuid4())}}

def extract_reply(messages) -> str:
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, list):
                text = " ".join(
                    b.get("text", "") for b in content
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            else:
                text = content
            if text.strip():
                return text
    return ""

print("\n🏠 Property Agent ready! Type 'quit' to exit.\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "quit":
        print("Goodbye!")
        break

    result = app.invoke(
        {"messages": [HumanMessage(user_input)]},
        config=config
    )
    print(f"\nAgent: {extract_reply(result['messages'])}\n")