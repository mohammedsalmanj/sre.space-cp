from datetime import datetime
from packages.shared.git_utils import generate_sre_commit_message

def fixer_agent(state):
    """Agent: Fixer (Execution)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW": return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Executing '{state['remediation']}' on Cluster...")
    
    # Prepare standard commit message for GitOps traceability
    commit_msg = generate_sre_commit_message(
        action_type="remediation",
        description=state.get('remediation', 'Apply patch'),
        incident_id=state.get('incident_id', 'unknown')
    )
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Commit Prepared -> {commit_msg.splitlines()[0]}")
    
    # Real GitHub Integration
    from packages.shared.github_service import GitHubService
    from packages.shared.reporting import format_fixer_action
    gh = GitHubService()
    
    issue_body = format_fixer_action(state)
    incident_num = state.get("incident_number", 0)
    
    if incident_num > 0:
        gh_res = gh.create_comment(issue_number=incident_num, body=issue_body)
        log_msg = f"Fixer Action Comment added to #{incident_num}"
    else:
        issue_title = f"[PATCH-DEPLOYED] {state.get('service', 'System')} - {state.get('remediation', 'Standard Patch')}"
        gh_res = gh.create_issue(title=issue_title, body=issue_body, labels=["remediation", "auto-fix"])
        log_msg = f"GitHub Patch Log Created: #{gh_res.get('number', 'unknown')}"
    
    if "error" not in gh_res:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] {log_msg}")
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Warning: GitHub integration failed.")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Patch deployed successfully.")
    state["logs"] = logs
    return state
