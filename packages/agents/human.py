from datetime import datetime
import os

def human_agent(state):
    """
    Agent: Human (The Investigator) - Human-in-the-Loop
    """
    from packages.shared.agent_utils import add_agent_log
    frequency = state.get("anomaly_frequency", 0)
    
    add_agent_log(state, "human", "HUMAN INTERVENTION TRIGGERED!")
    add_agent_log(state, "human", f"Reason: Issue detected {frequency} times in the last hour.")
    
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
        add_agent_log(state, "human", f"GitHub Issue Created: #{gh_res['number']}")
    else:
        add_agent_log(state, "human", "Warning: Failed to create GitHub Issue.")

    # Trigger external alert (Simulated email)
    success = send_sre_alert(
        subject=f"CRITICAL: Repeated SRE Anomaly in {state.get('service', 'Unknown Service')}",
        body=f"SRE Engine Alert:\nService: {state.get('service')}\nRoot Cause: {state.get('root_cause')}\nFrequency: {frequency} detections\nStatus: AUTO-REMEDIATION PAUSED."
    )
    
    if success:
        add_agent_log(state, "human", "Alert triggered for mohammedsalmanj@outlook.com")
    
    state["status"] = "Awaiting Human"
    return state
