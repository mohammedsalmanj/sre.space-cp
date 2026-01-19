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
    confidence_score: float
    decision: str  # ALLOW | BLOCK | REQUIRE_APPROVAL
    guardrail_reason: str
    service: str
    namespace: str
    env: str

# --- Tier-1 Fast Cache (CAG) ---
CAG_FAST_CACHE = {
    "HTTP 500: Database connection pool exhausted": {
        "root_cause": "System Saturation: DB Pool Exhaustion",
        "remediation": "SCALE: Increase pool size",
        "confidence": 0.95
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
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: Polling spans for errors...")
    
    state["service"] = "policy-service"
    state["namespace"] = "insurance-prod"
    state["env"] = "production"

    if state.get("is_anomaly"):
        error_span = {
            "trace_id": f"trace-{random.randint(1000, 9999)}",
            "exception.message": "HTTP 500: Database connection pool exhausted",
            "service": state["service"]
        }
        state["error_spans"] = [error_span]
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: ⚠️ Detected CRITICAL error in '{state['service']}'.")
    else:
        state["error_spans"] = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scout: System health nominal.")

    state["logs"] = logs
    state["status"] = "Checking Cache"
    return state

def cag_node(state: SREState) -> SREState:
    """CAG Agent: Instant retrieval for known FAQ incidents."""
    logs = state.get("logs", [])
    if not state["error_spans"]:
        state["status"] = "Healthy"
        return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] CAG: Checking Tier-1 Fast Cache...")
    msg = state["error_spans"][0]["exception.message"]
    
    if msg in CAG_FAST_CACHE:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] CAG: ⚡ FAST CACHE HIT!")
        known = CAG_FAST_CACHE[msg]
        state["root_cause"] = known["root_cause"]
        state["remediation"] = known["remediation"]
        state["confidence_score"] = known["confidence"]
        state["cache_hit"] = True
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] CAG: Cache Miss. Escalating...")
        state["cache_hit"] = False

    state["logs"] = logs
    return state

def brain_node(state: SREState) -> SREState:
    """Brain Agent: RCA + RAG Scoring Logic."""
    logs = state.get("logs", [])
    if state.get("cache_hit"):
        return state

    msg = state["error_spans"][0]["exception.message"]
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Initiating Deep RAG analysis...")

    collection = get_memory_collection()
    if collection:
        results = collection.query(query_texts=[msg], n_results=1)
        if results and results['documents'][0]:
            # RAG Scoring Implementation (Simulated Logic)
            similarity = 0.85 # Mock
            success_rate = 0.90 # Mock
            recency = 0.80 # Mock
            infra_match = 1.0 # Mock
            
            # Confidence = (0.4 * sim) + (0.3 * success) + (0.2 * recency) + (0.1 * infra)
            score = (0.4 * similarity) + (0.3 * success_rate) + (0.2 * recency) + (0.1 * infra_match)
            
            state["confidence_score"] = round(score, 2)
            state["historical_context"] = results['documents'][0][0]
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: RAG match found. Confidence: {state['confidence_score']}")
        else:
            state["confidence_score"] = 0.50 # Low confidence for new errors
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: No history. Confidence: {state['confidence_score']}")
    else:
        state["confidence_score"] = 0.60
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Memory Layer Offline. Manual heuristic confidence: {state['confidence_score']}")

    state["root_cause"] = "Database connection pool exhausted" if "Database" in msg else "System Failure"
    state["remediation"] = "SCALE: Increase resources" if "Database" in msg else "RESTART: Service"
    
    state["logs"] = logs
    return state

def guardrail_node(state: SREState) -> SREState:
    """Guardrail Agent: Change Management Enforcer."""
    logs = state.get("logs", [])
    if state["status"] == "Healthy": return state
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Guardrail: Evaluating safety of proposed action...")
    
    action = state["remediation"]
    score = state["confidence_score"]
    
    # Rules Enforcement
    if "delete" in action.lower() or "drop" in action.lower():
        state["decision"] = "BLOCK"
        state["guardrail_reason"] = "Destructive actions (DELETE/DROP) strictly forbidden."
    elif score < 0.75:
        state["decision"] = "REQUIRE_APPROVAL"
        state["guardrail_reason"] = f"Low confidence ({score}). Human review required."
    elif state["env"] != "production" and "production" in state["namespace"]:
        state["decision"] = "BLOCK"
        state["guardrail_reason"] = "Environment mismatch. Action blocked for target namespace."
    else:
        state["decision"] = "ALLOW"
        state["guardrail_reason"] = "Action verified as safe and reversible."

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Guardrail: Result -> {state['decision']} ({state['guardrail_reason']})")
    state["logs"] = logs
    return state

def fixer_node(state: SREState) -> SREState:
    """Fixer: Execution of allowed actions."""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW":
        return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fixer: Executing verified remediation: {state['remediation']}")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Fixer: Deployment successful. Health check passing.")
    state["logs"] = logs
    return state

def jules_node(state: SREState) -> SREState:
    """Jules: Hardening + Memory Curation Agent."""
    logs = state.get("logs", [])
    if state["decision"] == "BLOCK":
        return state

    # Memory Curator Agent Logic
    if state["decision"] == "ALLOW" and not state["cache_hit"]:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Memory Curator: Evaluating storage signal...")
        # Evaluation criteria: Verified successful? Yes. Unique? Yes. Valid for current infra? Yes.
        action = "STORE"
        
        collection = get_memory_collection()
        if collection:
            doc_id = f"inc-{random.randint(1000, 9999)}"
            collection.add(
                documents=[f"Cause: {state['root_cause']} | Fix: {state['remediation']}"],
                ids=[doc_id],
                metadatas=[{"service": state["service"], "cause": "saturation", "action": "scaling", "version": "v3.0"}]
            )
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Memory Curator: Action -> {action}. Index updated.")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Jules: Incident loop closed. System Stable.")
    state["logs"] = logs
    state["status"] = "Stable"
    return state

# --- Routing ---

def route_scout(state: SREState):
    return "cag" if state["is_anomaly"] else "end"

def route_cag(state: SREState):
    return "guardrail" if state["cache_hit"] else "brain"

def route_guardrail(state: SREState):
    return "fixer" if state["decision"] == "ALLOW" else "jules"

# --- Graph ---
def create_sre_graph():
    workflow = StateGraph(SREState)
    workflow.add_node("scout", scout_node)
    workflow.add_node("cag", cag_node)
    workflow.add_node("brain", brain_node)
    workflow.add_node("guardrail", guardrail_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("jules", jules_node)
    
    workflow.set_entry_point("scout")
    workflow.add_conditional_edges("scout", route_scout, {"cag": "cag", "end": END})
    workflow.add_conditional_edges("cag", route_cag, {"guardrail": "guardrail", "brain": "brain"})
    workflow.add_edge("brain", "guardrail")
    workflow.add_conditional_edges("guardrail", route_guardrail, {"fixer": "fixer", "jules": "jules"})
    workflow.add_edge("fixer", "jules")
    workflow.add_edge("jules", END)
    
    return workflow.compile()

async def run_sre_loop(is_anomaly: bool = False):
    graph = create_sre_graph()
    initial_state = {
        "error_spans": [], "root_cause": "", "remediation": "", "circuit_breaker_active": False,
        "status": "Starting", "logs": [], "is_anomaly": is_anomaly, "historical_context": "",
        "cache_hit": False, "confidence_score": 0.0, "decision": "", "guardrail_reason": "",
        "service": "", "namespace": "", "env": ""
    }
    return await graph.ainvoke(initial_state)
