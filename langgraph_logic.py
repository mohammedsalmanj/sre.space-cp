from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
import os

# Import Agents from the Agents package
from agents.scout import scout_agent
from agents.cag import cag_agent
from agents.brain import brain_agent
from agents.guardrail import guardrail_agent
from agents.fixer import fixer_agent
from agents.jules import jules_agent
from agents.curator import curator_agent
from agents.human import human_agent

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
    workflow = StateGraph(SREState)
    
    # Add Nodes from Imported Agents
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
    
    workflow.add_conditional_edges("scout", 
        lambda s: "human" if s["anomaly_frequency"] >= 3 else ("cag" if s["is_anomaly"] else END))
    
    workflow.add_conditional_edges("cag", lambda s: "guardrail" if s["cache_hit"] else "brain")
    workflow.add_edge("brain", "guardrail")
    workflow.add_conditional_edges("guardrail", lambda s: "fixer" if s["decision"] == "ALLOW" else "jules")
    
    workflow.add_edge("human", "curator")
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
        "service": "", "namespace": "", "env": "", "anomaly_frequency": 0
    }
    
    # Simulate a frequency surge for testing if anomaly is true
    if is_anomaly:
        initial_state["anomaly_frequency"] = 4 

    return await graph.ainvoke(initial_state)
