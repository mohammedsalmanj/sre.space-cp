from datetime import datetime
import random

def scout_agent(state):
    """
    Agent Node: Scout (The Watcher)
    Phase: OBSERVE
    Mission: Monitor the system heartbeat and sensory inputs (traces/metrics).
    """
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [OBSERVE] Polling telemetry streams via OpenTelemetry...")
    
    # Static metadata for the incident context
    state["service"] = "policy-service"
    state["namespace"] = "insurance-prod"
    state["env"] = "production"

    # Simulation Logic: If an anomaly is injected, Scout translates the raw 
    # signal into a structured state for the Brain agent to analyze.
    if state.get("is_anomaly"):
        # In a real system, this would be a query to Jaeger/Prometheus
        state["error_spans"] = [
            {"exception.message": "HTTP 500: Database connection pool exhausted", "severity": "CRITICAL"}
        ]
        # Frequency tracking for escalation logic (Human-in-the-loop)
        state["anomaly_frequency"] = 1 
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Alert: Critical threshold breach detected in policy-service.")
    else:
        # State remains clean if no anomaly is active
        state["error_spans"] = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Telemetry audit complete. System health: 100%.")

    # Pass the updated logs back to the state for UI streaming
    state["logs"] = logs
    return state
