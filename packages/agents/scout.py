from datetime import datetime
import asyncio
from packages.shared.telemetry import get_metrics
from packages.shared.event_bus.factory import get_event_bus

def scout_agent(state):
    """
    Agent: Scout (Detection) - Phase: [OBSERVE]
    Uses real-time telemetry to monitor system health.
    """
    logs = state.get("logs", [])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [OBSERVE] Sampling telemetry streams and activity indicators...")
    
    # 1. Fetch Real Metrics
    metrics = get_metrics()
    error_rate = metrics["error_rate"]
    avg_latency = metrics["avg_latency"]
    frequency = state.get("anomaly_frequency", 0)
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [OBSERVE] Telemetry State: ErrorRate={round(error_rate*100, 2)}%, Latency={round(avg_latency)}ms, Frequency={frequency}")
    
    is_detected = False
    anomaly_msg = ""

    # 2. Logic-based Detection
    if error_rate > 0.10: # 10% threshold for production alert
        is_detected = True
        anomaly_msg = f"CRITICAL_ERROR_RATE: {round(error_rate*100, 1)}% detected in policy-service."
        state["anomaly_type"] = "500"
    elif avg_latency > 2000: # 2s latency threshold
        is_detected = True
        anomaly_msg = f"LATENCY_BREACH: Average p95 latency reached {round(avg_latency)}ms."
        state["anomaly_type"] = "latency"
    
    # 3. Handle injected failure
    if state.get("is_anomaly") and not is_detected:
        is_detected = True
        anomaly_msg = f"INJECTED_FAULT_SIGNAL: {state.get('anomaly_type').upper()} anomaly reported by Engineering Controls."

    if is_detected:
        state["is_anomaly"] = True
        state["error_spans"] = [{"message": anomaly_msg, "error_rate": error_rate, "latency": avg_latency}]
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [OBSERVE] 🚨 Anomalous condition identified: {anomaly_msg}")
        
        # 4. Event Bus Signaling
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [OBSERVE] Persistence signal emitted to event bus.")
    else:
        state["is_anomaly"] = False
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [SCOUT] [OBSERVE] Telemetry within operational boundaries.")

    state["logs"] = logs
    return state
