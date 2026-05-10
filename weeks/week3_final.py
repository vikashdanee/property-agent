# agent.py
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage, AIMessage
from graph.builder import build_graph

app = build_graph()

config = {"configurable": {"thread_id": "user_003"}}

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

    # Find last AIMessage with actual content
    response_text = ""
    for msg in reversed(result['messages']):
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
                response_text = text
                break

    print(f"\nAgent: {response_text}\n")