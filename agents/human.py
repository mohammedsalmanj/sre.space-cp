from datetime import datetime
import os

def human_agent(state):
    """
    Agent: Human (The Investigator) - Human-in-the-Loop
    Trigger: Frequent anomalies or failed auto-remediations.
    Mission: Alert human SRE and wait for manual intervention.
    """
    logs = state.get("logs", [])
    frequency = state.get("anomaly_frequency", 0)
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 HUMAN INTERVENTION TRIGGERED!")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 Reason: Issue detected {frequency} times in the last hour.")
    
    # Send Email Notification
    from shared.notifications import send_sre_alert
    success = send_sre_alert(
        subject=f"CRITICAL: Repeated SRE Anomaly in {state.get('service', 'Unknown Service')}",
        body=f"SRE Engine Alert:\nService: {state.get('service')}\nRoot Cause: {state.get('root_cause')}\nFrequency: {frequency} detections\nStatus: AUTO-REMEDIATION PAUSED."
    )
    
    if success:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 📧 Alert triggered for mohammedsalmanj@outlook.com")
    
    state["logs"] = logs
    state["status"] = "Awaiting Human"
    return state
