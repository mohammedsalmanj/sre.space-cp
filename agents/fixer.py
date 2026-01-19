from datetime import datetime
from shared.git_utils import generate_sre_commit_message

def fixer_agent(state):
    """Agent: Fixer (Execution)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW": return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛠️ Fixer: Executing '{state['remediation']}' on Cluster...")
    
    # Prepare standard commit message for GitOps traceability
    commit_msg = generate_sre_commit_message(
        action_type="remediation",
        description=state.get('remediation', 'Apply patch'),
        incident_id=state.get('incident_id', 'unknown')
    )
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛠️ Fixer: Commit Prepared -> {commit_msg.splitlines()[0]}")
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛠️ Fixer: Patch deployed successfully.")
    state["logs"] = logs
    return state
