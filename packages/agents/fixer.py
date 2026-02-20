from datetime import datetime
import random
import time
from packages.shared.git_utils import generate_sre_commit_message, generate_sre_pr_title
from packages.shared.github_service import GitHubService
from packages.shared.reporting import format_fixer_action

def fixer_agent(state):
    """
    Agent: Fixer (Execution)
    Implements REAL GitOps lifecycle: Branch -> Commit -> PR -> Merge.
    """
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW":
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Vetoed by Guardrail. Action aborted.")
        return state

    remediation = state.get('remediation', 'Apply system patch')
    remediation_type = state.get('remediation_type', 'infra')
    gh = GitHubService()
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] ⚡ [GITOPS-FLOW] Initiating Autonomous Lifecycle...")

    # 1. Create/Comment on Issue
    incident_num = state.get("incident_number", 0)
    if incident_num == 0:
        issue_res = gh.create_issue(
            title=f"[AUTO-FIX] {state.get('service', 'System')} - {remediation}", 
            body=format_fixer_action(state), 
            labels=["auto-fix", remediation_type]
        )
        incident_num = issue_res.get("number", 0)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Incident Issue Raised: #{incident_num}")
    else:
        gh.create_comment(incident_num, f"🚀 Fixer executing remediation: {remediation}")

    # 2. REAL Branch Creation
    main_sha = gh.get_ref_sha()
    if not main_sha:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] ❌ Error: Could not fetch main branch SHA.")
        return state

    ts = int(time.time())
    branch_name = f"fix/incident-{incident_num}-{ts}"
    gh.create_branch(branch_name, main_sha)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] 🌿 Real Branch Created: '{branch_name}'")

    # 3. REAL Commit (Updating a status/fix file)
    fix_path = f"incidents/FIX-{incident_num}.md"
    fix_content = f"# Autonomous Fix Report\nIncident: {incident_num}\nTime: {datetime.now().isoformat()}\nRemediation: {remediation}\nStatus: Applied"
    gh.create_or_update_file(fix_path, f"fix: apply autonomous patch for #{incident_num}", fix_content, branch_name)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] 💾 Real Patch Committed to '{fix_path}'")

    # 4. REAL Pull Request
    pr_title = generate_sre_pr_title(state.get("service"), remediation)
    pr_res = gh.create_pr(title=pr_title, head=branch_name, body=f"Closes #{incident_num}\n\nAutomated fix applied by SRE-Space.")
    pr_num = pr_res.get("number")

    if not pr_num:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] ❌ PR Creation Failed: {pr_res.get('message', 'API Error')}")
        return state
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] ✅ Real PR Opened: #{pr_num}")

    # 5. REAL Autonomous Merge
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] 🤝 Merging PR #{pr_num} into main...")
    merge_res = gh.merge_pr(pr_num)
    
    if merge_res.get("merged"):
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] 🚀 Merge Successful. Deployment in progress...")
        state["status"] = "Success"
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] ⚠️ Merge deferred: {merge_res.get('message', 'Policy check')}")
        state["status"] = "Pending Approval"

    state["logs"] = logs
    state["incident_number"] = incident_num
    return state
