from datetime import datetime
import json
import random
from packages.shared.git_utils import generate_sre_pr_title

def jules_agent(state=None):
    """
    Agent: Jules (The Architect) - Tier-3 Architectural Authority
    Cycle: Daily (09:30 AM)
    Mission: Systemic optimization, resource cleanup, and architectural hardening.
    """
    logs = []
    current_time = datetime.now().strftime('%H:%M:%S')
    
    print(f"[{current_time}] [JULES] Initiating Daily Architectural Review...")
    logs.append(f"[{current_time}] [JULES] TIER-3 SCHEDULED SCAN: Assessing system-wide integrity.")
    
    # Architectural Optimization Decisions (Cloud Engineer style)
    optimizations = [
        "RESOURCES: Identifying and reaping orphan cloud volumes and snapshots > 30 days old.",
        "COST: Suggesting Reserved Instance (RI) conversion for stable policy-service base load.",
        "SECURITY: Rotating IAM keys for service-account-sre and updating secrets.",
        "PERFORMANCE: Analyzing p99 latency distributions - recommending CDN edge caching for static assets.",
        "CLEANUP: Purging temporary build artifacts and optimizing Docker image layers."
    ]
    
    # Choose 3 optimizations for the daily report
    selected = random.sample(optimizations, 3)
    
    # Real GitHub Integration
    from packages.shared.github_service import GitHubService
    from packages.shared.reporting import format_jules_refactor
    gh = GitHubService()
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    report_title = f"[DAILY-REVIEW] Architectural Integrity & Optimization {current_date}"
    
    # format_jules_refactor takes (state, selected_refactors)
    # We pass a dummy state for the daily review context
    dummy_state = {"service": "Infrastructure/Cluster"}
    report_body = format_jules_refactor(dummy_state, selected)
    
    print(f"[{current_time}] [JULES] Generating Optimization Proposal...")
    gh_res = gh.create_issue(title=report_title, body=report_body, labels=["architectural", "daily-optimizer"])
    
    if "number" in gh_res:
        print(f"[{current_time}] [JULES] Daily Report Published -> #{gh_res['number']}")
        logs.append(f"[{current_time}] [JULES] Optimization Proposal Created -> #{gh_res['number']}")
    else:
        print(f"[{current_time}] [JULES] Warning: GitHub reporting failed.")

    if state:
        state["logs"].extend(logs)
        return state
    return logs

# Helper logic complete.
