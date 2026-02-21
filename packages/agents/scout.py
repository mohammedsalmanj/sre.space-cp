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
        # Simulated high-fidelity error message matching user's 'real' experience
        error_msg = ("policy-service: DOWN (HTTPConnectionPool(host='policy-service', port=8002): "
                     "Max retries exceeded with url: /health "
                     "(Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7fc73dbd4a60>: "
                     "Failed to establish a new connection: [Errno 111] Connection refused')))")
        
        state["error_spans"] = [
            {"exception.message": error_msg, "severity": "CRITICAL", "category": "Latency/Saturation"}
        ]
        state["anomaly_frequency"] = state.get("anomaly_frequency", 0) + 1
        
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [ALERT] SRE Scout Alert: Infrastructure Signal Triggered.")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Error: {error_msg}")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Category: Latency/Saturation | Conversion: 0.0%")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Decision: Brain Analysis Required.")
    else:
        # State remains clean if no anomaly is active
        state["error_spans"] = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Telemetry audit complete. System health: 100%.")

    # Pass the updated logs back to the state for UI streaming
    state["logs"] = logs
    return state
