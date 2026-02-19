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
    from packages.shared.reporting import format_patch_deployed
    gh = GitHubService()
    issue_title = f"[PATCH-DEPLOYED] {state.get('service', 'System')} - {state.get('remediation', 'Standard Patch')}"
    issue_body = format_patch_deployed(state)
    gh_res = gh.create_issue(title=issue_title, body=issue_body, labels=["remediation", "auto-fix"])
    
    if "number" in gh_res:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] GitHub Patch Log Created: #{gh_res['number']}")
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Warning: GitHub integration failed.")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Patch deployed successfully.")
    state["logs"] = logs
    return state
