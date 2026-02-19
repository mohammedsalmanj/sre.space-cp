from datetime import datetime
import random

def scout_agent(state):
    """Agent: Scout (Detection)"""
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Polling OTel traces...")
    
    state["service"] = "policy-service"
    state["namespace"] = "insurance-prod"
    state["env"] = "production"

    if state.get("is_anomaly"):
        state["error_spans"] = [{"exception.message": "HTTP 500: Database connection pool exhausted"}]
        state["anomaly_frequency"] = 1 # Force ensure Auto-Resolve path (bypass Human)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Warning: Detected 1 error span.")
    else:
        state["error_spans"] = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] System health nominal.")

    state["logs"] = logs
    return state
