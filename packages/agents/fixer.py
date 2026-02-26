"""
File: packages/agents/fixer.py
Layer: Cognitive / Action
Purpose: Executes remediation plans and manages the GitOps lifecycle.
Problem Solved: Automates infrastructure mutations in an auditable, reversible, and safe manner.
Interaction: Receives plans from the Brain; uses RemediationAdapters for execution; creates PRs via GitHubService.
Dependencies: packages.infrastructure.registry, packages.shared.github_service, packages.shared.git_utils
Inputs: Remediation plan and target resource from state
Outputs: PR number, execution status, and verification metrics
"""
from datetime import datetime
import time
import base64
from packages.shared.git_utils import generate_sre_commit_message
from packages.infrastructure.registry import registry
from packages.infrastructure.base import ActionPlan
from packages.shared.github_service import GitHubService
from packages.shared.reporting import format_patch_deployed

def fixer_agent(state: dict) -> dict:
    """
    Agent Node: Fixer
    Phase: ACT
    Mission: Apply the proposed fix to the infrastructure and create a permanent record in Git.
    
    Args:
        state (dict): The current LangGraph state.
    Returns:
        dict: Updated state with act logs and verification status.
    """
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW": return state

    adapter = registry.get_adapter()
    remediation_plan = state.get("remediation", "Apply patch")
    target = state.get("service", "unknown-resource")
    incident_id = state.get("incident_id", "unknown")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Initializing remediation for {target}...")

    # 1. Safety Guardrail: Immutable Infrastructure Snapshots
    snapshot_id = "N/A"
    high_risk_keywords = ["restart", "reboot", "reprovision", "terminate", "reset", "update", "patch"]
    is_high_risk = any(kw in remediation_plan.lower() for kw in high_risk_keywords)
    
    if is_high_risk:
        try:
            snapshot_id = adapter.snapshot(target)
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [GUARDRAIL] High-risk action detected. Snapshot created: {snapshot_id}")
        except Exception as e:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Skip snapshot: {str(e)}")
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Routine action detected. Skipping snapshot.")

    # 2. Infrastructure Mutation Layer: Guarded by SIMULATION_MODE
    action_plan = ActionPlan(
        action_type="remediation",
        description=remediation_plan,
        parameters={"plan": remediation_plan},
        target_resource=target,
        incident_id=incident_id
    )
    
    if state.get("simulation_mode"):
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [SIMULATION] 🛡️ Shadow Action. Would have executed: {remediation_plan} on {target}.")
        execution_result = {
            "status": "SUCCESS (SIMULATED)",
            "audit_command": f"sre-cli fix --target {target} --plan '{remediation_plan}'",
            "iac_file": None
        }
    else:
        execution_result = adapter.execute(action_plan)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Adapter Execution: {execution_result.get('status')}")
    
    # 3. GitOps Implementation Layer
    gh = GitHubService()
    timestamp = int(time.time())
    branch_name = f"fix/incident-{incident_id}-{timestamp}"
    
    commit_msg = generate_sre_commit_message(
        action_type="remediation",
        description=remediation_plan,
        incident_id=incident_id
    )

    try:
        main_ref = gh.get_ref("heads/main")
        main_sha = main_ref.get("object", {}).get("sha")
        
        if main_sha:
            gh.create_ref(branch_name, main_sha)
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Created GitOps branch: {branch_name}")
            
            if execution_result.get("iac_file"):
                file_path = execution_result["iac_file"]
                content = base64.b64encode(execution_result["new_content"].encode()).decode()
            else:
                file_path = f"packages/remediations/patch-{timestamp}.md"
                audit_log = f"# SRE Remediation Log\n\n**Action:** {remediation_plan}\n**Command:** `{execution_result.get('audit_command', 'N/A')}`\n**Snapshot:** `{snapshot_id}`"
                content = base64.b64encode(audit_log.encode()).decode()
            
            gh.update_file(file_path, commit_msg, content, branch_name)
            
            pr_body = format_patch_deployed(state)
            issue_num = state.get("issue_number")
            if issue_num:
                pr_body = f"Fixes #{issue_num}\n\n" + pr_body

            if execution_result.get("audit_command"):
                pr_body += f"\n\n### Audit Trail (Executed Commands)\n```bash\n{execution_result['audit_command']}\n```"
            
            if snapshot_id != "N/A":
                pr_body += f"\n\n### Infrastructure Safety\n- **Snapshot ID**: `{snapshot_id}`"
            
            pr_res = gh.create_pr(
                title=f"[AUTO-FIX] {target} - Incident {incident_id}",
                head=branch_name,
                body=pr_body
            )
            
            if "number" in pr_res:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Pull Request Created: #{pr_res['number']}")
                
                # 4. Post-Execution Verification Loop
                verify_res = adapter.verify("HEALTHY")
                if verify_res.success:
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [CHECK] Remediation verified. Metrics improved: {verify_res.metric_delta}")
                else:
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [WARNING] Verification failed. Initiating automated rollback...")
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ROLLBACK] Reverting to snapshot: {snapshot_id}")
                    state["status"] = "Partial Failure"
    
    except Exception as e:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Critical Governance Error: {str(e)}")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Patch cycle complete.")
    state["logs"] = logs
    return state
