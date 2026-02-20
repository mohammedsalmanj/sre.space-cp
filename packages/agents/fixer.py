from datetime import datetime
from packages.shared.git_utils import generate_sre_commit_message

def fixer_agent(state):
    """Agent: Fixer (Execution)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW": return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Executing '{state['remediation']}' on Cluster...")
    
    # Prepare standard commit message for GitOps traceability
    commit_msg = generate_sre_commit_message(
        action_type="remediation",
        description=state.get('remediation', 'Apply patch'),
        incident_id=state.get('incident_id', 'unknown')
    )
    
    # Real GitHub Integration: Create Branch & PR
    import base64
    import time
    from packages.shared.github_service import GitHubService
    from packages.shared.reporting import format_patch_deployed
    
    gh = GitHubService()
    timestamp = int(time.time())
    branch_name = f"fix/incident-{state.get('incident_id', 'unknown')}-{timestamp}"
    
    try:
        # 1. Get Main SHA
        main_ref = gh.get_ref("heads/main")
        main_sha = main_ref.get("object", {}).get("sha")
        
        if main_sha:
            # 2. Create Unique Branch
            gh.create_ref(branch_name, main_sha)
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Created branch: {branch_name}")
            
            # 3. "Deploy" Patch (Simulated file update for GitOps)
            patch_content = base64.b64encode(f"# SRE Patch {timestamp}\n{state['remediation']}".encode()).decode()
            gh.update_file(f"packages/remediations/patch-{timestamp}.md", commit_msg, patch_content, branch_name)
            
            # 4. Create PR
            pr_res = gh.create_pr(
                title=f"[AUTO-FIX] {state.get('service', 'System')} - Incident {state.get('incident_id', 'unknown')}",
                head=branch_name,
                body=format_patch_deployed(state)
            )
            
            if "number" in pr_res:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Pull Request Created: #{pr_res['number']}")
            else:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Warning: PR creation failed.")
    except Exception as e:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] Critical GitOps Error: {str(e)}")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [FIXER] [ACT] Patch cycle complete.")
    state["logs"] = logs
    return state
