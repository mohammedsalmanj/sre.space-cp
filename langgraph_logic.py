from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from datetime import datetime
import random
import json
import os

# Optional: ChromaDB Integration
try:
    import chromadb
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
    cache_hit: bool

# --- CAG (Cache-Augmented Generation) Tier-1 Store ---
# This acts as our high-speed FAQ/Known-Issue cache
CAG_FAST_CACHE = {
    "HTTP 500: Database connection pool exhausted": {
        "root_cause": "Tier-1 Known Issue: DB Saturation.",
        "remediation": "INSTANT-PATCH: Auto-scaled pool to 100 via CAG Cache."
    },
    "ConnectionTimeout: policy-service unavailable": {
        "root_cause": "Tier-1 Known Issue: Mock API Latency.",
        "remediation": "INSTANT-RESTART: Recycled policy-service pod via CAG Cache."
    }
}

# --- ChromaDB Initialization ---
def get_memory_collection():
    if not CHROMA_ENABLED:
        return None
    try:
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
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: System health nominal.")

    state["logs"] = logs
    state["status"] = "Checking Cache"
    return state

def cag_node(state: SREState) -> SREState:
    """
    CAG (Cache-Augmented Generation) Agent:
    Bypasses heavy Reasoning/RAG for known 'FAQ' style incidents.
    """
    logs = state.get("logs", [])
    if not state["error_spans"]:
        state["status"] = "Healthy"
        return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] CAG: Checking Tier-1 Fast Cache for incident signature...")
    msg = state["error_spans"][0]["exception.message"]
    
    # Check if this is a "Known FAQ" incident
    if msg in CAG_FAST_CACHE:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] CAG: ⚡ FAST CACHE HIT! Identification immediate.")
        known_fix = CAG_FAST_CACHE[msg]
        state["root_cause"] = known_fix["root_cause"]
        state["remediation"] = known_fix["remediation"]
        state["cache_hit"] = True
        state["status"] = "Instant Remediation"
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] CAG: Cache Miss. Escalating to Brain Agent for RAG/Reasoning.")
        state["cache_hit"] = False
        state["status"] = "Reasoning"

    state["logs"] = logs
    return state

def brain_node(state: SREState) -> SREState:
    """Brain: Analyzes root cause and retrieves historical context from ChromaDB (RAG)."""
    logs = state.get("logs", [])
    # If CAG already fixed it, we skip deep reasoning
    if state.get("cache_hit"):
        return state

    msg = state["error_spans"][0]["exception.message"]
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Initiating Deep RAG analysis for exception: '{msg}'")

    collection = get_memory_collection()
    if collection:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Querying ChromaDB for historical remediation...")
        results = collection.query(query_texts=[msg], n_results=1)
        if results and results['documents'][0]:
            state["historical_context"] = results['documents'][0][0]
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Found historical match: '{state['historical_context'][:50]}...'")
        else:
            state["historical_context"] = "No history found."
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Memory Layer offline. Proceeding with heuristic analysis.")

    if "Database" in msg:
        state["root_cause"] = "Connection pool saturation (Analyzed via Brain)."
    else:
        state["root_cause"] = "Unknown microservice failure."

    state["logs"] = logs
    state["status"] = "Remediating"
    return state

def fixer_node(state: SREState) -> SREState:
    """Fixer: Applies the most confident remediation."""
    logs = state.get("logs", [])
    
    # If remediation isn't set (by Brain), set it here
    if not state.get("remediation"):
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fixer: Applying remediation plan from Brain Agent...")
        if "Connection pool" in state["root_cause"]:
            state["remediation"] = "HOT-PATCH: Increased pool size via Brain recommendation."
        else:
            state["remediation"] = "RESTART: Performed service recycle."
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fixer: Executing CAG-Provided Instant Fix...")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fixer: Fix deployed - {state['remediation']}")
    state["logs"] = logs
    state["status"] = "Hardening"
    return state

def jules_node(state: SREState) -> SREState:
    """Jules: Hardens the system and archives the lesson in ChromaDB."""
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: Performing architectural hardening...")
    state["circuit_breaker_active"] = True

    # Archive if it was a deep reasoning fix (new knowledge)
    if not state.get("cache_hit") and state["root_cause"] != "None":
        collection = get_memory_collection()
        if collection:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: Archiving new lesson in ChromaDB memory...")
            doc_id = f"inc-{random.randint(10000, 99999)}"
            collection.add(
                documents=[f"Incident: {state['root_cause']} | Fix: {state['remediation']}"],
                ids=[doc_id]
            )

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: System recovery complete. State: STABLE.")
    state["logs"] = logs
    state["status"] = "Stable"
    return state

# --- Graph Routing Logic ---

def should_check_cache(state: SREState) -> Literal["cag", "end"]:
    if state["status"] == "Healthy":
        return "end"
    return "cag"

def route_after_cag(state: SREState) -> Literal["fixer", "brain"]:
    """If CAG was a hit, go straight to Fixer. Else, go to Brain."""
    return "fixer" if state.get("cache_hit") else "brain"

# --- Graph Construction ---

def create_sre_graph():
    workflow = StateGraph(SREState)
    
    workflow.add_node("scout", scout_node)
    workflow.add_node("cag", cag_node)
    workflow.add_node("brain", brain_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("jules", jules_node)
    
    workflow.set_entry_point("scout")
    
    workflow.add_conditional_edges("scout", should_check_cache, {"cag": "cag", "end": END})
    workflow.add_conditional_edges("cag", route_after_cag, {"fixer": "fixer", "brain": "brain"})
    
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
        "historical_context": "",
        "cache_hit": False
    }
    return await graph.ainvoke(initial_state)
