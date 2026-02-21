from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
import os
import sys

# Ensure shared packages are discoverable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# --- Agent Imports ---
# Every node in the graph is a specialized SRE agent
from packages.agents.scout import scout_agent
from packages.agents.cag import cag_agent
from packages.agents.brain import brain_agent
from packages.agents.guardrail import guardrail_agent
from packages.agents.fixer import fixer_agent
from packages.agents.jules import jules_agent
from packages.agents.curator import curator_agent
from packages.agents.human import human_agent

# --- Pipeline State ---
# This dictionary is passed between agents, representing the memory of the current recovery cycle.
class SREState(TypedDict):
    error_spans: List[Dict[str, Any]]    # OpenTelemetry trace data
    root_cause: str                     # Found by Brain agent
    remediation: str                   # Proposed fix
    status: str                        # Current state (Stable/Fixing)
    logs: List[str]                    # OODA loop logs for UI streaming
    is_anomaly: bool                   # Trigger flag
    anomaly_frequency: int             # Escalation counter
    decision: str                      # Guardrail 'ALLOW' or 'DENY'
    service: str                       # Targeting which service?
    namespace: str                     # K8s/Docker namespace
    env: str                           # Production/Staging

# --- The Agentic Graph (LangGraph) ---
def create_sre_graph():
    """Builds the state machine that governs autonomous SRE reasoning."""
    from apps.control_plane.config import ACTIVE_AGENTS
    
    workflow = StateGraph(SREState)
    
    # 1. Register Agents as Nodes
    workflow.add_node("scout", scout_agent)
    workflow.add_node("cag", cag_agent)
    workflow.add_node("brain", brain_agent)
    workflow.add_node("guardrail", guardrail_agent)
    workflow.add_node("fixer", fixer_agent)
    workflow.add_node("jules", jules_agent)
    workflow.add_node("curator", curator_agent)
    workflow.add_node("human", human_agent)
    
    # 2. Define the Transitions (OODA Flow)
    workflow.set_entry_point("scout")
    
    # --- Dynamic Flow Logic ---
    # These functions decide which agent to invoke next based on the system state
    # and whether the agent is 'Active' in the current environment (Cloud vs Local).

    def scout_next(s):
        # High-frequency anomalies require human intervention
        if s["anomaly_frequency"] >= 3: return "human"
        if not s["is_anomaly"]: return END
        # Skip CAG (Cognitive Agent Guide) in Cloud mode to save token budget
        return "cag" if "cag" in ACTIVE_AGENTS else "brain"

    def cag_next(s):
        # Brain handles logic, CAG provides architectural standards
        return "brain"

    def brain_next(s):
        # Guardrail must validate every proposed fix for safety
        return "guardrail" if "guardrail" in ACTIVE_AGENTS else "fixer"

    def guardrail_next(s):
        # Fixer only runs if Guardrail grants 'ALLOW'
        if s["decision"] == "ALLOW":
            return "fixer"
        return "jules" if "jules" in ACTIVE_AGENTS else "curator"

    def fixer_next(s):
        # Jules performs architectural deep clean after a hotfix
        return "jules" if "jules" in ACTIVE_AGENTS else "curator"

    # 3. Connect the Nodes
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
    """Entry point to trigger the autonomous control plane."""
    graph = create_sre_graph()
    initial_state = {
        "error_spans": [], "root_cause": "", "remediation": "", 
        "status": "Starting", "logs": [], "is_anomaly": is_anomaly,
        "anomaly_frequency": 0, "decision": "", "service": "policy-service", 
        "namespace": "default", "env": "prod"
    }
    
    if is_anomaly:
        initial_state["anomaly_frequency"] = 1

    return await graph.ainvoke(initial_state)
