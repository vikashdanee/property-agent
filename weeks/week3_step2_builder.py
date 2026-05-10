# graph/builder.py
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from graph.state import AgentState
from graph.nodes import agent_node
from graph.edges import should_continue
from tools.unit_search import search_units
from tools.book_tour import book_tour
import sqlite3

def build_graph():
    """Assembles and compiles the full agent graph with persistent memory."""

    tool_node = ToolNode([search_units, book_tour])

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    # SQLite checkpointer — persists memory to disk
    conn = sqlite3.connect("memory.db", check_same_thread=False)
    memory = SqliteSaver(conn)

    return graph.compile(checkpointer=memory)