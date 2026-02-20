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
    remediation_type: str
    anomaly_type: str
    anomaly_frequency: int
    incident_number: int

# --- Graph Logic ---
def create_sre_graph():
    """
    Orchestrates the SRE Agent Squad using LangGraph.
    
    The graph defines the cognitive cycle:
    Polling (Scout) -> Analysis (CAG/Brain) -> Safety (Guardrail) -> Action (Fixer) -> Feedback (Curator)
    """
    workflow = StateGraph(SREState)
    
    # Add Nodes from Imported Agents
    workflow.add_node("scout", scout_agent)
    workflow.add_node("cag", cag_agent)
    workflow.add_node("brain", brain_agent)
    workflow.add_node("guardrail", guardrail_agent)
    workflow.add_node("fixer", fixer_agent)
    workflow.add_node("curator", curator_agent)
    workflow.add_node("human", human_agent)
    
    # Define Transitions (The "Mind" of the SRE Engine)
    workflow.set_entry_point("scout")
    
    # Transition 1: Scout -> Decision
    # If anomaly frequency is high, escalate to Human. Else if anomaly detected, go to CAG (Fast Fix).
    workflow.add_conditional_edges("scout", 
        lambda s: "human" if s["anomaly_frequency"] >= 3 else ("cag" if s["is_anomaly"] else END))
    
    # Transition 2: CAG (Tier-1) -> Decision
    # If CAG misses (cache miss), escalate to Brain (Tier-2).
    workflow.add_conditional_edges("cag", lambda s: "guardrail" if s["cache_hit"] else "brain")
    
    # Transition 3: Brain -> Guardrail
    workflow.add_edge("brain", "guardrail")
    
    # Transition 4: Guardrail -> Action
    # Only allow Fixer to act if Guardrail confirms safety.
    workflow.add_conditional_edges("guardrail", lambda s: "fixer" if s["decision"] == "ALLOW" else "human")
    
    # Transition 5: Post-Action -> Memory Curator
    workflow.add_edge("human", "curator")
    workflow.add_edge("fixer", "curator")
    workflow.add_edge("curator", END)
    
    return workflow.compile()

async def run_sre_loop(is_anomaly: bool = False, anomaly_type: str = "infra"):
    """
    Executes a single cognitive cycle of the SRE engine.
    
    Args:
        is_anomaly (bool): Whether to inject an anomaly for testing/simulation.
        anomaly_type (str): Type of anomaly ('infra' or 'code')
    """
    graph = create_sre_graph()
    
    # Initial State Initialization (TypedDict compliant)
    initial_state = {
        "error_spans": [], "root_cause": "", "remediation": "", "circuit_breaker_active": False,
        "status": "Starting", "logs": [], "is_anomaly": is_anomaly, "historical_context": "",
        "cache_hit": False, "confidence_score": 0.0, "decision": "", "guardrail_reason": "",
        "service": "policy-service", "namespace": "insurance-cloud", "env": "production", "anomaly_frequency": 0, "incident_number": 0,
        "remediation_type": "infra", "anomaly_type": anomaly_type
    }
    
    # Simulate a frequency surge if anomaly is injected for demo purposes
    if is_anomaly:
        initial_state["anomaly_frequency"] = 1

    return await graph.ainvoke(initial_state)
