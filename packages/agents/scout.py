"""
File: packages/agents/scout.py
Layer: Cognitive / Observability
Purpose: Continuous system monitoring and initial anomaly detection.
Problem Solved: Identifies health degradations across heterogeneous stacks before they impact end-users.
Interaction: Polls SensoryAdapters for telemetry; triggers the Brain agent if an anomaly is found.
Dependencies: packages.infrastructure.registry, packages.shared.sim_state
Inputs: Current LangGraph state
Outputs: Updated state with metrics, error spans, and anomaly flags
"""
from datetime import datetime
import os
from packages.infrastructure.registry import registry
from packages.shared.sim_state import sim_state

def scout_agent(state: dict) -> dict:
    """
    Agent Node: Scout
    Phase: OBSERVE
    Mission: Monitor system health and identify performance anomalies or errors.
    
    Args:
        state (dict): The current LangGraph state containing telemetry logs and discovery flags.
    Returns:
        dict: The updated state with fresh metrics and anomaly triggers.
    Raises:
        Exception: If the infrastructure adapter fails to poll telemetry.
    """
    logs = state.get("logs", [])
    stack_type = os.getenv("STACK_TYPE", "ec2")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [OBSERVE] Polling telemetry via {stack_type} adapter...")
    
    # 1. Retrieve the universal adapter and simulation engine
    adapter = registry.get_adapter()
    from packages.infrastructure.simulation.chaos_engine import chaos_engine
    
    # 2. Collect telemetry: Check for Shadow Injection if in Simulation Mode
    shadow_telemetry = None
    if state.get("simulation_mode"):
        shadow_telemetry = chaos_engine.get_shadow_telemetry(stack_type)
        if shadow_telemetry:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [SIMULATION] 🛡️ Shadow Injection Active. Using synthetic fault profile.")

    telemetry = shadow_telemetry if shadow_telemetry else adapter.collect()
    state["raw_telemetry_obj"] = telemetry # Preserve for downstream memory enrichment
    
    # 3. Synchronize adapter data with the agent state machine
    state["service"] = telemetry.service_name
    state["telemetry_status"] = telemetry.status
    state["metrics"] = {
        "error_rate": telemetry.error_rate,
        "latency_p95": telemetry.latency_p95,
        "cpu_usage": telemetry.cpu_usage,
        "memory_usage": telemetry.memory_usage
    }
    state["error_spans"] = telemetry.error_spans
    
    # 4. Anomaly Detection Logic: Checks metrics, status, and synthetic simulation state
    current_sim = sim_state.get_state()
    is_anomaly = state.get("is_anomaly") or current_sim["is_anomaly"] or (telemetry.status == "CRITICAL")

    if is_anomaly:
        # Fallback for synthetic reality if the adapter (simulated) misses a span
        if not state["error_spans"]:
            state["error_spans"] = [
                {"exception.message": "Simulated infrastructure failure detected.", "severity": "CRITICAL"}
            ]
        
        state["anomaly_frequency"] = state.get("anomaly_frequency", 0) + 1
        
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [ALERT] Signal Triggered on {stack_type} stack.")
        for span in state["error_spans"]:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Error: {span.get('exception.message', 'Unknown')}")
        
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Decision: Brain Analysis Required.")
    else:
        state["error_spans"] = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Telemetry audit complete. System health: 100%.")

    state["logs"] = logs
    return state
