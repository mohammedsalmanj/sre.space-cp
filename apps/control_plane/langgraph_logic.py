"""
File: apps/control_plane/langgraph_logic.py
Layer: Application / Orchestration
Purpose: Defines the cognitive OODA loop (Observe-Orient-Decide-Act) using LangGraph.
Problem Solved: Coordinates multiple specialized SRE agents into a unified, stateful recovery process.
Interaction: Orchestrates Scout, Brain, Fixer, and other agents; invoked by the FastAPI main app.
Dependencies: langgraph, packages.agents.*
Inputs: Initial anomaly trigger (boolean)
Outputs: Final recovery state and comprehensive OODA logs
"""
from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
import os
import sys

# Ensure shared packages are discoverable in the monorepo root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# --- Cognitive Agent Node Imports ---
from packages.agents.scout import scout_agent
from packages.agents.cag import cag_agent
from packages.agents.brain import brain_agent
from packages.agents.guardrail import guardrail_agent
from packages.agents.fixer import fixer_agent
from packages.agents.jules import jules_agent
from packages.agents.curator import curator_agent
from packages.agents.human import human_agent

class SREState(TypedDict):
    """
    Global state shared across all agents in the recovery cycle.
    Acts as the 'working memory' for a single autonomous OODA loop iteration.
    """
    error_spans: List[Dict[str, Any]]    # Normalized OpenTelemetry trace signatures
    root_cause: str                     # Diagnosis produced by Brain agent
    remediation: str                    # Proposed architectural or code-level fix
    status: str                         # Loop status (Stable, Fixing, Escalated)
    logs: List[str]                     # Real-time OODA logs for streaming to the Dashboard
    is_anomaly: bool                    # Trigger flag for the control plane sensory intake
    anomaly_frequency: int              # Tracks repeated failures for auto-escalation
    decision: str                       # Guardrail outcome: 'ALLOW', 'DENY', or 'REQUIRE_APPROVAL'
    service: str                        # Root service affected (e.g. policy-service)
    namespace: str                      # Deployment namespace (e.g. K8s default)
    env: str                            # Operational environment (prod/staging)
    confidence_score: float             # AI diagnostic certainty (0.0 to 1.0)
    blast_radius: int                   # Impact score assessment (1-10)
    issue_number: int                   # GitHub issue ID for governance tracking
    simulation_mode: bool               # Enables shadow execution (Dry-run mode)
    top_incidents: List[Dict[str, Any]]  # RAG-retrieved historical context

def create_sre_graph():
    """
    Builds the state machine that governs autonomous SRE reasoning.
    Defines the OODA transitions and conditional exits between agents.
    
    Returns:
        CompiledGraph: The executable LangGraph state machine.
    """
    from apps.control_plane.config import ACTIVE_AGENTS
    
    workflow = StateGraph(SREState)
    
    # 1. Node Registration: Mapping agent logic functions to graph nodes
    workflow.add_node("scout", scout_agent)
    workflow.add_node("cag", cag_agent)
    workflow.add_node("brain", brain_agent)
    workflow.add_node("guardrail", guardrail_agent)
    workflow.add_node("fixer", fixer_agent)
    workflow.add_node("jules", jules_agent)
    workflow.add_node("curator", curator_agent)
    workflow.add_node("human", human_agent)
    
    # 2. Define the Entry Point: Every cycle begins with sensory Observation (Scout)
    workflow.set_entry_point("scout")
    
    # --- Dynamic Edge Logic: Hardening the Intelligent Flow ---

    def scout_next(s: dict):
        """Logic for transitioning from Observe to Orient phase."""
        if s["anomaly_frequency"] >= 3: return "human" # Escalation threshold
        if not s["is_anomaly"]: return END             # False alarm or recovered
        return "cag" if "cag" in ACTIVE_AGENTS else "brain"

    def cag_next(s: dict):
        """Handoff from fast-path pattern matching to deep reasoning if needed."""
        return "brain"

    def brain_next(s: dict):
        """Decision boundary based on AI diagnostic confidence."""
        if s.get("confidence_score", 0) < 0.85:
            return "human" # Safety fallback
        return "guardrail" if "guardrail" in ACTIVE_AGENTS else "fixer"

    def guardrail_next(s: dict):
        """Security validation exit point."""
        if s["decision"] == "ALLOW":
            return "fixer"
        return "jules" if "jules" in ACTIVE_AGENTS else "curator"

    def fixer_next(s: dict):
        """Cleanup and permanent refactoring check after a hotfix."""
        return "jules" if "jules" in ACTIVE_AGENTS else "curator"

    # 3. Finalize Transitions into a unified state machine
    workflow.add_conditional_edges("scout", scout_next)
    workflow.add_conditional_edges("cag", cag_next)
    workflow.add_conditional_edges("brain", brain_next)
    workflow.add_conditional_edges("guardrail", guardrail_next)
    workflow.add_conditional_edges("fixer", fixer_next)
    
    workflow.add_edge("human", "curator")
    workflow.add_edge("jules", "curator")
    workflow.add_edge("curator", END)
    
    return workflow.compile()

# --- Initial State Factory ---
def get_initial_state(is_anomaly: bool = False, simulation_mode: bool = False) -> SREState:
    """Creates a fresh state for a new OODA loop iteration."""
    return {
        "error_spans": [], "root_cause": "", "remediation": "", 
        "status": "Observation Phase", "logs": [], "is_anomaly": is_anomaly,
        "anomaly_frequency": 1 if is_anomaly else 0, "decision": "", "service": "policy-service", 
        "namespace": "default", "env": "prod", "confidence_score": 1.0,
        "blast_radius": 0, "issue_number": 0, "simulation_mode": simulation_mode,
        "top_incidents": []
    }

# --- Single Instance Pre-compiled Graph (Optimization) ---
# Compiling the graph once at module load time prevents overhead during high-frequency telemetry audits.
_sre_graph = create_sre_graph()

async def run_sre_loop(is_anomaly: bool = False, simulation_mode: bool = False) -> dict:
    """
    Asynchronous entry point to trigger the autonomous control plane loop.
    Reuses the pre-compiled state machine for optimized performance.
    
    Args:
        is_anomaly (bool): Whether to force initial anomaly detection (default: False).
        simulation_mode (bool): Whether to run in dry-run mode (default: False).
    Returns:
        dict: The final state object including audit logs.
    """
    initial_state = get_initial_state(is_anomaly, simulation_mode)
    return await _sre_graph.ainvoke(initial_state)
