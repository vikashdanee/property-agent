# graph/builder.py
import os

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from graph.state import AgentState
from graph.nodes import (
    identify_node, applicant_node,
    resident_node, resident_tool_node, support_node
)
from graph.edges import route_by_user_type, route_applicant, route_resident
from tools.unit_search import search_units
from tools.book_tour import book_tour
import sqlite3

def build_graph():
    graph = StateGraph(AgentState)

    # ── Nodes ──────────────────────────────────────────────
    graph.add_node("identify",        identify_node)
    graph.add_node("applicant",       applicant_node)
    graph.add_node("applicant_tools", ToolNode([search_units, book_tour]))
    graph.add_node("resident",        resident_node)
    graph.add_node("resident_tools",  resident_tool_node)
    graph.add_node("support",         support_node)

    # ── Edges ──────────────────────────────────────────────
    graph.add_edge(START, "identify")

    graph.add_conditional_edges("identify", route_by_user_type, {
        "identify":  "identify",
        "applicant": "applicant",
        "resident":  "resident",
        END:          END,
    })

    graph.add_conditional_edges("applicant", route_applicant, {
        "applicant_tools": "applicant_tools",
        END:                END,
    })
    graph.add_edge("applicant_tools", "applicant")

    graph.add_conditional_edges("resident", route_resident, {
        "resident_tools": "resident_tools",
        "support":        "support",
        END:               END,
    })
    graph.add_edge("resident_tools", "resident")
    graph.add_edge("support",        END)

    # ── Sync SQLite memory ─────────────────────────────────
    db_path = os.getenv("DB_PATH", "memory.db")
    conn    = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)
    return graph.compile(checkpointer=memory)