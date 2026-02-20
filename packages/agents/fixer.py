from datetime import datetime
import random
import time
from packages.shared.git_utils import generate_sre_commit_message, generate_sre_pr_title
from packages.shared.github_service import GitHubService
from packages.shared.reporting import format_fixer_action

def fixer_agent(state):
    """
    Agent: Fixer (Execution) - Phase: [ACT]
    Implements REAL GitOps lifecycle: Branch -> Commit -> PR -> Merge.
    """
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW":
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] SAFELINE_VETO: Guardrail blocked execution. Action aborted.")
        return state

    remediation = state.get('remediation', 'System mitigation')
    remediation_type = state.get('remediation_type', 'infra')
    gh = GitHubService()
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] ⚡ Initiating autonomous GitOps remediation lifecycle...")

    # 1. Create/Comment on Issue
    incident_num = state.get("incident_number", 0)
    if incident_num == 0:
        issue_res = gh.create_issue(
            title=f"[AUTO-FIX] {state.get('service', 'System')} - Remediation Plan", 
            body=format_fixer_action(state), 
            labels=["auto-fix", remediation_type]
        )
        incident_num = issue_res.get("number", 0)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] TICKET_INITIALIZED: Incident Issue #{incident_num}")
    else:
        gh.create_comment(incident_num, f"⚙️ Fixer starting ACTUAL remediation: {remediation}")

    # 2. REAL Branch Creation
    main_sha = gh.get_ref_sha()
    if not main_sha:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] ❌ ERROR: Reference SHA resolution failed.")
        return state

    ts = int(time.time())
    branch_name = f"fix/incident-{incident_num}-{ts}"
    gh.create_branch(branch_name, main_sha)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] BRANCH_PROVISIONED: '{branch_name}'")

    # 3. REAL Commit
    fix_path = f"incidents/FIX-{incident_num}.md"
    fix_content = f"--- \nincident: {incident_num}\ntimestamp: {datetime.now().isoformat()}\nremediation: {remediation}\nstatus: DEPLOYED\n---"
    gh.create_or_update_file(fix_path, f"fix: deploy autonomous patch for #{incident_num}", fix_content, branch_name)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] COMMITTED: Remediation manifest pushed to repository.")

    # 4. REAL Pull Request
    pr_title = generate_sre_pr_title(state.get("service"), remediation)
    pr_res = gh.create_pr(title=f"[AUTONOMOUS-FIX] {pr_title}", head=branch_name, body=f"Closes #{incident_num}\n\nREMEDIATION: {remediation}")
    pr_num = pr_res.get("number")

    if not pr_num:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] ❌ PR_REJECTION: {pr_res.get('message', 'API Conflict')}")
        return state
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] PR_VALIDATED: Pull Request #{pr_num} is live.")

    # 5. REAL Autonomous Merge
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Merging fix into primary branch...")
    merge_res = gh.merge_pr(pr_num)
    
    if merge_res.get("merged"):
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] SUCCESS: Remediated state merged. Resetting fault state.")
        state["status"] = "Success"
        # Reset Fault State in Real Time
        from apps.control_plane.runtime_config import update_chaos_mode, update_degraded_mode
        update_chaos_mode(None, False)
        update_degraded_mode(False)
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] DEFERRED: Merge pending automated checks.")
        state["status"] = "Pending Approval"

    state["logs"] = logs
    state["incident_number"] = incident_num
    return state
