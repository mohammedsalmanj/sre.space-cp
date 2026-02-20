from datetime import datetime
import json
import random
from packages.shared.git_utils import generate_sre_pr_title

def jules_agent(state=None):
    """
    Agent: Jules (The Architect) - Tier-3 Architectural Authority
    
    Jules is the senior architect of the squad. Unlike other agents that react 
    to real-time incidents, Jules performs deep architectural reviews and 
    systemic optimizations.
    
    Mission:
    - Identifying long-term technical debt.
    - Suggesting infrastructure optimizations (cost, performance, security).
    - Hardening the system against recurring classes of failures.
    
    Cycle: Scheduled (Daily at 09:30 AM) or triggered manually.
    """
    logs = []
    current_time = datetime.now().strftime('%H:%M:%S')
    
    print(f"[{current_time}] [JULES] Initiating Daily Architectural Review...")
    logs.append(f"[{current_time}] [JULES] TIER-3 SCHEDULED SCAN: Assessing system-wide integrity.")
    
    # Logic: Select optimizations from a pre-defined architectural knowledge base
    # In a real scenario, this would involve static analysis or cloud resource scanning.
    optimizations = [
        "RESOURCES: Identifying and reaping orphan cloud volumes and snapshots > 30 days old.",
        "COST: Suggesting Reserved Instance (RI) conversion for stable policy-service base load.",
        "SECURITY: Rotating IAM keys for service-account-sre and updating secrets.",
        "PERFORMANCE: Analyzing p99 latency distributions - recommending CDN edge caching for static assets.",
        "CLEANUP: Purging temporary build artifacts and optimizing Docker image layers."
    ]
    
    # Choose a subset of optimizations for the current review cycle
    selected = random.sample(optimizations, 3)
    
    # Real GitHub Integration: Publish the findings for human review
    from packages.shared.github_service import GitHubService
    from packages.shared.reporting import format_jules_refactor
    gh = GitHubService()
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    report_title = f"[DAILY-REVIEW] Architectural Integrity & Optimization {current_date}"
    
    # format_jules_refactor generates a Markdown report for the GitHub issue
    dummy_state = {"service": "Infrastructure/Cluster"}
    report_body = format_jules_refactor(dummy_state, selected)
    
    print(f"[{current_time}] [JULES] Generating Optimization Proposal...")
    gh_res = gh.create_issue(title=report_title, body=report_body, labels=["architectural", "daily-optimizer"])
    
    # Handle the API result and update logs
    if "number" in gh_res:
        print(f"[{current_time}] [JULES] Daily Report Published -> #{gh_res['number']}")
        logs.append(f"[{current_time}] [JULES] Optimization Proposal Created -> #{gh_res['number']}")
    else:
        print(f"[{current_time}] [JULES] Warning: GitHub reporting failed.")

    # Return state if Jules is being run as part of a LangGraph cycle
    if state:
        state["logs"].extend(logs)
        return state
    return logs

# Helper logic complete.
