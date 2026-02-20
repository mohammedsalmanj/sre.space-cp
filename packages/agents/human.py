from datetime import datetime
import os

def human_agent(state):
    """
    Agent: Human (The Investigator) - Human-in-the-Loop
    
    The Human agent is triggered when autonomous remediation is deemed too risky 
    or when an anomaly repeats too frequently, suggesting a systemic failure 
    that requires human intuition.
    
    Mission:
    - Escalate the incident to the SRE team via Email and GitHub.
    - Pause the autonomous loop to prevent "flapping" or damage.
    """
    logs = state.get("logs", [])
    frequency = state.get("anomaly_frequency", 0)
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [HUMAN] HUMAN INTERVENTION TRIGGERED!")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [HUMAN] Reason: Issue detected {frequency} times in the last hour.")
    
    # Send Notification and Create Escalation Ticket
    from packages.shared.notifications import send_sre_alert
    from packages.shared.github_service import GitHubService
    from packages.shared.reporting import format_human_escalation
    
    gh = GitHubService()
    issue_title = f"[HUMAN-REQUIRED] {state.get('service', 'System')} - Repeated Anomaly Detected"
    issue_body = format_human_escalation(state)
    
    # Create the critical escalation issue
    gh_res = gh.create_issue(title=issue_title, body=issue_body, labels=["critical", "human-needed"])
    
    if "number" in gh_res:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [HUMAN] GitHub Issue Created: #{gh_res['number']}")
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [HUMAN] Warning: Failed to create GitHub Issue.")

    # Trigger external alert (Simulated email)
    success = send_sre_alert(
        subject=f"CRITICAL: Repeated SRE Anomaly in {state.get('service', 'Unknown Service')}",
        body=f"SRE Engine Alert:\nService: {state.get('service')}\nRoot Cause: {state.get('root_cause')}\nFrequency: {frequency} detections\nStatus: AUTO-REMEDIATION PAUSED."
    )
    
    if success:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [HUMAN] Alert triggered for mohammedsalmanj@outlook.com")
    
    state["logs"] = logs
    state["status"] = "Awaiting Human"
    return state
