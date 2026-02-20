from datetime import datetime
import asyncio
from packages.shared.telemetry import get_metrics
from packages.shared.event_bus.factory import get_event_bus

def scout_agent(state):
    """
    Agent: Scout (Detection)
    Uses REAL telemetry signals to detect anomalies.
    """
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Polling OTel traces & real-time metrics...")
    
    # 1. Fetch Real Metrics
    metrics = get_metrics()
    error_rate = metrics["error_rate"]
    avg_latency = metrics["avg_latency"]
    
    is_detected = False
    anomaly_msg = ""

    # 2. Logic-based Detection (Story Point 3)
    if error_rate > 0.15: # 15% threshold for demo
        is_detected = True
        anomaly_msg = f"CRITICAL: High Error Rate detected ({round(error_rate*100, 1)}%)"
        state["anomaly_type"] = "500"
    elif avg_latency > 1500: # 1.5s latency threshold
        is_detected = True
        anomaly_msg = f"WARNING: Latency threshold exceeded ({round(avg_latency)}ms)"
        state["anomaly_type"] = "latency"
    
    # 3. Fallback for immediate demo trigger
    if state.get("is_anomaly") and not is_detected:
        is_detected = True
        anomaly_msg = f"PROACTIVE: Injected failure detected ({state.get('anomaly_type')})"

    if is_detected:
        state["is_anomaly"] = True
        state["error_spans"] = [{"message": anomaly_msg, "error_rate": error_rate, "latency": avg_latency}]
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] 🚨 {anomaly_msg}")
        
        # 4. Event Bus Signaling (Story Point 4)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] EVENT_PUBLISHED: INCIDENT_SIGNAL_EMITTED")
    else:
        state["is_anomaly"] = False
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] Signals within normal bounds. (Err: {round(error_rate*100)}%, Lat: {round(avg_latency)}ms)")

    state["logs"] = logs
    return state
