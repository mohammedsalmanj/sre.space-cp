from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
import os

import sys
import os
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Import Agents from the packages/agents
from packages.agents.scout import scout_agent
from packages.agents.cag import cag_agent
from packages.agents.brain import brain_agent
from packages.agents.guardrail import guardrail_agent
from packages.agents.fixer import fixer_agent
from packages.agents.jules import jules_agent
from packages.agents.curator import curator_agent
from packages.agents.human import human_agent

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
    anomaly_frequency: int

# --- Graph Logic ---
def create_sre_graph():
    from apps.control_plane.config import ACTIVE_AGENTS
    workflow = StateGraph(SREState)
    
    # Add Nodes
    workflow.add_node("scout", scout_agent)
    workflow.add_node("cag", cag_agent)
    workflow.add_node("brain", brain_agent)
    workflow.add_node("guardrail", guardrail_agent)
    workflow.add_node("fixer", fixer_agent)
    workflow.add_node("jules", jules_agent)
    workflow.add_node("curator", curator_agent)
    workflow.add_node("human", human_agent)
    
    # Define Transitions
    workflow.set_entry_point("scout")
    
    def scout_next(s):
        if s["anomaly_frequency"] >= 3: return "human"
        if not s["is_anomaly"]: return END
        return "cag" if "cag" in ACTIVE_AGENTS else "brain"

    def cag_next(s):
        if s["cache_hit"]:
            return "guardrail" if "guardrail" in ACTIVE_AGENTS else "fixer"
        return "brain"

    def brain_next(s):
        return "guardrail" if "guardrail" in ACTIVE_AGENTS else "fixer"

    def guardrail_next(s):
        if s["decision"] == "ALLOW":
            return "fixer"
        return "jules" if "jules" in ACTIVE_AGENTS else "curator"

    def fixer_next(s):
        return "jules" if "jules" in ACTIVE_AGENTS else "curator"

    workflow.add_conditional_edges("scout", scout_next)
    workflow.add_conditional_edges("cag", cag_next)
    workflow.add_conditional_edges("brain", brain_next)
    workflow.add_conditional_edges("guardrail", guardrail_next)
    workflow.add_conditional_edges("fixer", fixer_next)
    
    workflow.add_edge("human", "curator")
    workflow.add_edge("jules", "curator")
    workflow.add_edge("curator", END)
    
    return workflow.compile()

async def run_sre_loop(is_anomaly: bool = False):
    graph = create_sre_graph()
    initial_state = {
        "error_spans": [], "root_cause": "", "remediation": "", "circuit_breaker_active": False,
        "status": "Starting", "logs": [], "is_anomaly": is_anomaly, "historical_context": "",
        "cache_hit": False, "confidence_score": 0.0, "decision": "", "guardrail_reason": "",
        "service": "", "namespace": "", "env": "", "anomaly_frequency": 0
    }
    
    # Simulate a frequency surge for testing if anomaly is true
    if is_anomaly:
        initial_state["anomaly_frequency"] = 1 # Lowered for full loop testing

    return await graph.ainvoke(initial_state)
