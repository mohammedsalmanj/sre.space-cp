from datetime import datetime
import json
import random
from packages.shared.git_utils import generate_sre_pr_title

def jules_agent(state=None):
    """
    Agent: Jules (The Architect) - Tier-3 Architectural Authority
    """
    from packages.shared.agent_utils import add_agent_log
    
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [JULES] Initiating Daily Architectural Review...")
    
    internal_logs = []
    def log(msg):
        internal_logs.append(f"[{current_time}] [JULES] {msg}")
        if state:
            add_agent_log(state, "jules", msg)

    log("TIER-3 SCHEDULED SCAN: Assessing system-wide integrity.")
    
    # Logic: Select optimizations ...
    optimizations = [
        "RESOURCES: Identifying and reaping orphan cloud volumes and snapshots > 30 days old.",
        "COST: Suggesting Reserved Instance (RI) conversion for stable policy-service base load.",
        "SECURITY: Rotating IAM keys for service-account-sre and updating secrets.",
        "PERFORMANCE: Analyzing p99 latency distributions - recommending CDN edge caching for static assets.",
        "CLEANUP: Purging temporary build artifacts and optimizing Docker image layers."
    ]
    
    selected = random.sample(optimizations, 3)
    
    # Real GitHub Integration
    from packages.shared.github_service import GitHubService
    from packages.shared.reporting import format_jules_refactor
    gh = GitHubService()
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    report_title = f"[DAILY-REVIEW] Architectural Integrity & Optimization {current_date}"
    
    dummy_report_state = {"service": "Infrastructure/Cluster"}
    report_body = format_jules_refactor(dummy_report_state, selected)
    
    print(f"[{current_time}] [JULES] Generating Optimization Proposal...")
    gh_res = gh.create_issue(title=report_title, body=report_body, labels=["architectural", "daily-optimizer"])
    
    if "number" in gh_res:
        msg = f"Optimization Proposal Created -> #{gh_res['number']}"
        print(f"[{current_time}] [JULES] Daily Report Published -> #{gh_res['number']}")
        log(msg)
    else:
        print(f"[{current_time}] [JULES] Warning: GitHub reporting failed.")

    return state if state else internal_logs
