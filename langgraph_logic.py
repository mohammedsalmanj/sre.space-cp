from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from datetime import datetime
import random
import json

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

# --- Node Implementations ---

def scout_node(state: SREState) -> SREState:
    """Scout: Uses OTel SDK to check for error spans."""
    # Simulate OTel Span Fetching
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: Checking OTel spans for errors in the last 60s...")
    
    # Simulate finding an error (based on 'is_anomaly' flag set by UI)
    if state.get("is_anomaly"):
        error_span = {
            "trace_id": f"trace-{random.randint(1000, 9999)}",
            "span_id": f"span-{random.randint(100, 999)}",
            "exception.message": "HTTP 500 Internal Server Error: Database connection timeout",
            "service.name": "insurance-quote-service"
        }
        state["error_spans"] = [error_span]
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: Detected 1 error span in 'insurance-quote-service'.")
    else:
        state["error_spans"] = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: No error spans detected. System nominal.")

    state["logs"] = logs
    state["status"] = "Analyzing"
    return state

def brain_node(state: SREState) -> SREState:
    """Brain: Analyzes the exception.message from the OTel trace."""
    logs = state.get("logs", [])
    if not state["error_spans"]:
        state["root_cause"] = "None"
        state["status"] = "Healthy"
        return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Analyzing trace '{state['error_spans'][0]['trace_id']}'...")
    msg = state["error_spans"][0]["exception.message"]
    
    if "Database connection timeout" in msg:
        state["root_cause"] = "Database saturation - connection pool exhausted."
    else:
        state["root_cause"] = "Unknown logic failure."
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Root Cause found: {state['root_cause']}")
    state["logs"] = logs
    state["status"] = "Remediating"
    return state

def fixer_node(state: SREState) -> SREState:
    """Fixer: Simulates a fix by updating the System Health state."""
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fixer: Initiating auto-remediation...")
    
    if "Database" in state["root_cause"]:
        state["remediation"] = "Increased connection pool size from 20 to 50."
    else:
        state["remediation"] = "Restarted microservice pod."
        
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fixer: Fix applied - {state['remediation']}")
    state["logs"] = logs
    state["status"] = "Hardening"
    return state

def jules_node(state: SREState) -> SREState:
    """Jules: Applies a Circuit Breaker pattern."""
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: Performing architectural post-mortem...")
    state["circuit_breaker_active"] = True
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: Applied 'Circuit Breaker' pattern to prevent ripple effects.")
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: System recovery complete. State: STABLE.")
    state["logs"] = logs
    state["status"] = "Stable"
    return state

# --- Routing Logic ---

def should_continue(state: SREState) -> Literal["continue", "end"]:
    if not state.get("error_spans") or state["status"] == "Healthy":
        return "end"
    return "continue"

# --- Graph Construction ---

def create_sre_graph():
    workflow = StateGraph(SREState)
    
    workflow.add_node("scout", scout_node)
    workflow.add_node("brain", brain_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("jules", jules_node)
    
    workflow.set_entry_point("scout")
    
    workflow.add_conditional_edges(
        "scout",
        should_continue,
        {
            "continue": "brain",
            "end": END
        }
    )
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
        "is_anomaly": is_anomaly
    }
    
    final_state = await graph.ainvoke(initial_state)
    return final_state
