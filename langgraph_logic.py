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
    decision: str
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

# --- Shared Utilities ---
def get_memory_collection():
    if not CHROMA_ENABLED: return None
    try:
        client = chromadb.HttpClient(host='localhost', port=8000)
        return client.get_or_create_collection(name="sre_incident_memory")
    except: return None

# --- Individual Agents (Nodes) ---

def scout_agent(state: SREState) -> SREState:
    """Agent: Scout (Detection)"""
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🕵️ Scout: Polling OTel traces...")
    
    state["service"] = "policy-service"
    state["namespace"] = "insurance-prod"
    state["env"] = "production"

    if state.get("is_anomaly"):
        state["error_spans"] = [{"exception.message": "HTTP 500: Database connection pool exhausted"}]
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🕵️ Scout: ⚠️ Detected 1 error span.")
    else:
        state["error_spans"] = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🕵️ Scout: System health nominal.")

    state["logs"] = logs
    return state

def cag_agent(state: SREState) -> SREState:
    """Agent: CAG (Fast Cache)"""
    logs = state.get("logs", [])
    if not state["error_spans"]: return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ CAG: Checking Tier-1 Fast Cache for incident FAQ...")
    msg = state["error_spans"][0]["exception.message"]
    
    if msg in CAG_FAST_CACHE:
        known = CAG_FAST_CACHE[msg]
        state["root_cause"] = known["root_cause"]
        state["remediation"] = known["remediation"]
        state["confidence_score"] = known["confidence"]
        state["cache_hit"] = True
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ CAG: INSTANT-HIT. Known incident signature.")
    else:
        state["cache_hit"] = False
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ CAG: Cache Miss. Escalating to Brain...")

    state["logs"] = logs
    return state

def brain_agent(state: SREState) -> SREState:
    """Agent: Brain (RAG-Augmented Reasoning)"""
    logs = state.get("logs", [])
    if state.get("cache_hit") or not state["error_spans"]: return state

    msg = state["error_spans"][0]["exception.message"]
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: Initiating deep RAG retrieval & scoring...")

    collection = get_memory_collection()
    if collection:
        results = collection.query(query_texts=[msg], n_results=1)
        if results and results['documents'][0]:
            # RAG Scoring Implementation
            state["confidence_score"] = 0.88 # Simulated score
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: Historical fix found. RAG Confidence: {state['confidence_score']}")
        else:
            state["confidence_score"] = 0.40
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: No historical match found.")
    
    state["root_cause"] = "Database saturation detected via trace attributes."
    state["remediation"] = "SCALE: Increase HikariCP pool size."
    state["logs"] = logs
    return state

def guardrail_agent(state: SREState) -> SREState:
    """Agent: Guardrail (Safety Enforcer)"""
    logs = state.get("logs", [])
    if not state["error_spans"]: return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ Guardrail: ⚖️ Evaluating safety of remediation action...")
    
    if state["confidence_score"] < 0.75:
        state["decision"] = "REQUIRE_APPROVAL"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ Guardrail: 🛑 Confidence too low ({state['confidence_score']}). Blocking auto-fix.")
    else:
        state["decision"] = "ALLOW"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ Guardrail: ✅ Action ALLOWED. Action is reversible and safe.")

    state["logs"] = logs
    return state

def fixer_agent(state: SREState) -> SREState:
    """Agent: Fixer (Execution)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW": return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛠️ Fixer: Executing '{state['remediation']}' on Cluster...")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛠️ Fixer: Patch deployed successfully.")
    state["logs"] = logs
    return state

def jules_agent(state: SREState) -> SREState:
    """Agent: Jules (Hardening)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW": return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Jules: Hardening architecture (Applied Circuit Breaker).")
    state["logs"] = logs
    return state

def curator_agent(state: SREState) -> SREState:
    """Agent: Memory Curator (Memory Lifecycle)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW" or state["cache_hit"]: return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧹 Curator: Incident unique. 📚 Archiving Knowledge into ChromaDB.")
    collection = get_memory_collection()
    if collection:
        doc_id = f"inc-{random.randint(1000, 9999)}"
        collection.add(
            documents=[f"Issue: {state['root_cause']} | Fix: {state['remediation']}"],
            ids=[doc_id]
        )
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧹 Curator: Indexing complete ID: {doc_id}")

    state["status"] = "Stable"
    state["logs"] = logs
    return state

# --- Graph Logic ---
def create_sre_graph():
    workflow = StateGraph(SREState)
    
    # 1. Add all 7 specialized agents
    workflow.add_node("scout", scout_agent)
    workflow.add_node("cag", cag_agent)
    workflow.add_node("brain", brain_agent)
    workflow.add_node("guardrail", guardrail_agent)
    workflow.add_node("fixer", fixer_agent)
    workflow.add_node("jules", jules_agent)
    workflow.add_node("curator", curator_agent)
    
    # 2. Define Transitions
    workflow.set_entry_point("scout")
    
    workflow.add_conditional_edges("scout", lambda s: "cag" if s["is_anomaly"] else END)
    workflow.add_conditional_edges("cag", lambda s: "guardrail" if s["cache_hit"] else "brain")
    workflow.add_edge("brain", "guardrail")
    workflow.add_conditional_edges("guardrail", lambda s: "fixer" if s["decision"] == "ALLOW" else "jules")
    
    workflow.add_edge("fixer", "jules")
    workflow.add_edge("jules", "curator")
    workflow.add_edge("curator", END)
    
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
