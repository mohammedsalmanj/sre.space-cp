from datetime import datetime
import random

def scout_agent(state):
    """
    Agent: Scout (Detection)
    
    The Scout agent is the sensory organ of the SRE squad. Its primary responsibility 
    is to monitor OpenTelemetry traces and identify anomalies such as high latency 
    spikes or 5xx error responses.
    
    Args:
        state (dict): The current LangGraph state containing logs, service info, and anomaly data.
        
    Returns:
        dict: The updated state with identified error spans if an anomaly is detected.
    """
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Polling OTel traces...")
    
    # Mocking target service context for demonstration
    state["service"] = "policy-service"
    state["namespace"] = "insurance-prod"
    state["env"] = "production"

    # Identify if an anomaly has been injected or naturally occurred
    is_anomaly = state.get("is_anomaly")
    anomaly_type = state.get("anomaly_type", "infra")

    if is_anomaly:
        if anomaly_type == "code":
            msg = "HTTP 500: ZeroDivisionError in quote calculator"
        else:
            msg = "HTTP 500: Database connection pool exhausted"
            
        state["error_spans"] = [{"exception.message": msg}]
        state["anomaly_frequency"] = 1 
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Warning: Detected anomaly -> {msg}")
    else:
        # System is healthy
        state["error_spans"] = []
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] System health nominal.")

    state["logs"] = logs
    return state
