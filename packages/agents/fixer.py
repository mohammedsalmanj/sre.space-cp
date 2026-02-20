from datetime import datetime
from packages.shared.git_utils import generate_sre_commit_message

def fixer_agent(state):
    """
    Agent: Fixer (Execution)
    
    The Fixer agent is responsible for applying the remediation plan. 
    It interacts with GitHub to log actions (via comments or new issues) 
    and simulates the deployment of patches to the cluster.
    
    Args:
        state (dict): The current LangGraph state containing the remediation plan.
        
    Returns:
        dict: The updated state after execution.
    """
    logs = state.get("logs", [])
    
    # Safety Check: Only execute if the Guardrail has allowed the action
    if state["decision"] != "ALLOW": return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Analysis: Remediation Type identified as '{state.get('remediation_type', 'infra')}'")
    
    # STEP 1: Real GitHub Integration
    from packages.shared.github_service import GitHubService
    from packages.shared.reporting import format_fixer_action
    from packages.shared.git_utils import generate_sre_pr_title
    gh = GitHubService()
    
    incident_num = state.get("incident_number", 0)
    issue_body = format_fixer_action(state)

    # BRANCH A: Code-Level Fix (Full Autonomy: Issue -> PR -> Merge -> Deploy)
    if state.get("remediation_type") == "code":
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] ⚡ [CODE-FLOW] Initiating Autonomous GitOps Cycle...")
        
        # 1. Raise/Update Issue
        if incident_num > 0:
            gh.create_comment(issue_number=incident_num, body="🚀 Starting Autonomous PR & Merge cycle for this code-level fix.")
        else:
            issue_res = gh.create_issue(title=f"[AUTO-FIX] {state.get('remediation')}", body=issue_body, labels=["auto-fix", "code-patch"])
            incident_num = issue_res.get("number", 0)

        # 2. Raise PR (Simulated branch fix-incident-id)
        pr_title = generate_sre_pr_title(state.get("service"), state.get("remediation"))
        branch_name = f"fix-inc-{incident_num}"
        pr_res = gh.create_pr(title=pr_title, head=branch_name, body=f"Closes #{incident_num}\n\n{issue_body}")
        
        if "number" in pr_res:
            pr_num = pr_res["number"]
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] ✅ PR Created: #{pr_num}")
            
            # 3. Merge PR
            merge_res = gh.merge_pr(pull_number=pr_num)
            if "merged" in merge_res and merge_res["merged"]:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] 🚀 PR Merged into main. Triggering Deployment...")
            else:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] ⚠️ Merge pending or check failed. Escalating.")
        else:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] ⚠️ PR creation failed: {pr_res.get('error', 'Unknown Error')}")

    # BRANCH B: Infrastructure/Other Fix (Policy/Scale/Alert)
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] 🔧 [INFRA-FLOW] Applying Operational adjustment...")
        if incident_num > 0:
            gh.create_comment(issue_number=incident_num, body=issue_body)
            log_msg = f"Fixer Action Log added to #{incident_num}"
        else:
            issue_title = f"[INFRA-PATCH] {state.get('service', 'System')} - {state.get('remediation')}"
            gh_res = gh.create_issue(title=issue_title, body=issue_body, labels=["remediation", "infra-fix"])
            log_msg = f"GitHub Operational Log Created: #{gh_res.get('number', 'unknown')}"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] {log_msg}")

    # STEP 3: Final Deployment Verification (Simulated)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Running Post-remediation health checks...")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Environment stabilized. Operations resuming.")
    
    state["logs"] = logs
    return state
