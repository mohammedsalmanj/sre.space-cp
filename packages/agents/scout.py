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
    from packages.shared.agent_utils import add_agent_log
    add_agent_log(state, "scout", "Polling OTel traces...")
    
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
        add_agent_log(state, "scout", f"Detected anomaly -> {msg}")
    else:
        # System is healthy
        state["error_spans"] = []
        add_agent_log(state, "scout", "System health nominal.")

    return state
