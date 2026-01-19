from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from datetime import datetime
import random
import json
import os

# Optional: ChromaDB Integration
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_ENABLED = True
except ImportError:
    CHROMA_ENABLED = False

# --- State Definition ---
class SREState(TypedDict):
    """The state of our autonomous SRE engine."""
    error_spans: List[Dict[str, Any]]
    root_cause: str
    remediation: str
    circuit_breaker_active: bool
    status: str
    logs: List[str]
    is_anomaly: bool
    historical_context: str

# --- ChromaDB Initialization ---
def get_memory_collection():
    if not CHROMA_ENABLED:
        return None
    try:
        # Connect to the ChromaDB hosted in Docker (body)
        client = chromadb.HttpClient(host='localhost', port=8000)
        return client.get_or_create_collection(name="sre_incident_memory")
    except Exception:
        return None

# --- Node Implementations ---

def scout_node(state: SREState) -> SREState:
    """Scout: Monitors OTel spans for internal errors."""
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: Polling OTel traces for error spans...")
    
    if state.get("is_anomaly"):
        error_span = {
            "trace_id": f"trace-{random.randint(1000, 9999)}",
            "exception.message": "HTTP 500: Database connection pool exhausted",
            "service": "policy-service"
        }
        state["error_spans"] = [error_span]
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: ⚠️ Detected CRITICAL error in 'policy-service'.")
    else:
        state["error_spans"] = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: System health nominal. No errors found.")

    state["logs"] = logs
    state["status"] = "Analyzing"
    return state

def brain_node(state: SREState) -> SREState:
    """Brain: Analyzes root cause and retrieves historical context from ChromaDB (RAG)."""
    logs = state.get("logs", [])
    if not state["error_spans"]:
        state["status"] = "Healthy"
        return state

    msg = state["error_spans"][0]["exception.message"]
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Analyzing exception: '{msg}'")

    # RAG: Query ChromaDB for similar past incidents
    collection = get_memory_collection()
    if collection:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Querying ChromaDB for historical remediation...")
        results = collection.query(query_texts=[msg], n_results=1)
        if results and results['documents'][0]:
            state["historical_context"] = results['documents'][0][0]
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Found historical match: '{state['historical_context'][:50]}...'")
        else:
            state["historical_context"] = "No history found."
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: No previous matching incidents found in memory.")
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Memory Layer (ChromaDB) offline. Proceeding with heuristic analysis.")

    # RCA Inference
    if "Database" in msg:
        state["root_cause"] = "Connection pool saturation."
    else:
        state["root_cause"] = "Unknown microservice failure."

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Diagnosis complete - {state['root_cause']}")
    state["logs"] = logs
    state["status"] = "Remediating"
    return state

def fixer_node(state: SREState) -> SREState:
    """Fixer: Applies the most confident remediation."""
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fixer: Applying remediation plan...")

    if "Connection pool" in state["root_cause"]:
        state["remediation"] = "HOT-PATCH: Increased HikariCP pool size to 100."
    else:
        state["remediation"] = "RESTART: Rolling restart of affected pod."

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fixer: Fix deployed - {state['remediation']}")
    state["logs"] = logs
    state["status"] = "Hardening"
    return state

def jules_node(state: SREState) -> SREState:
    """Jules: Hardens the system and archives the lesson in ChromaDB."""
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: Performing architectural hardening...")
    
    # Simulate adding robustness
    state["circuit_breaker_active"] = True
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: Applied Circuit Breaker pattern to 'policy-service'.")

    # Archive to ChromaDB
    collection = get_memory_collection()
    if collection and state["root_cause"] != "None":
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: Archiving fix in ChromaDB vector memory...")
        doc_id = f"inc-{random.randint(10000, 99999)}"
        collection.add(
            documents=[f"Incident: {state['root_cause']} | Fix: {state['remediation']}"],
            ids=[doc_id]
        )
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: Incident archived under ID: {doc_id}")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: System recovery complete. State: STABLE.")
    state["logs"] = logs
    state["status"] = "Stable"
    return state

# --- Graph ---
def should_continue(state: SREState) -> Literal["continue", "end"]:
    if state["status"] == "Healthy":
        return "end"
    return "continue"

def create_sre_graph():
    workflow = StateGraph(SREState)
    workflow.add_node("scout", scout_node)
    workflow.add_node("brain", brain_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("jules", jules_node)
    workflow.set_entry_point("scout")
    workflow.add_conditional_edges("scout", should_continue, {"continue": "brain", "end": END})
    workflow.add_edge("brain", "fixer")
    workflow.add_edge("fixer", "jules")
    workflow.add_edge("jules", END)
    return workflow.compile()

async def run_sre_loop(is_anomaly: bool = False):
    graph = create_sre_graph()
    initial_state = {
        "error_spans": [],
        "root_cause": "",
        "remediation": "",
        "circuit_breaker_active": False,
        "status": "Starting",
        "logs": [],
        "is_anomaly": is_anomaly,
        "historical_context": ""
    }
    return await graph.ainvoke(initial_state)
