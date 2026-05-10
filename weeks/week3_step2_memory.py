# agent.py
from dotenv import load_dotenv
load_dotenv()  # ← must be first before any other imports

from langchain_core.messages import HumanMessage
from graph.builder import build_graph

app = build_graph()

config = {"configurable": {"thread_id": "user_001"}}

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

    print(f"\nAgent: {result['messages'][-1].content}\n")