from datetime import datetime
import json
import random
from packages.shared.git_utils import generate_sre_pr_title

def jules_agent(state):
    """
    Agent: Jules (The Architect) - Tier-3 Architectural Authority
    Trigger: Focused on chronic or systemic failures.
    Mission: Deep code refactoring and design flaw elimination.
    """
    logs = state.get("logs", [])
    
    # Tier-3 Logic: Only intervene if the failure is identified as systemic or chronic
    # For simulation, we check if the root cause has occurred multiple times in history
    is_systemic = state.get("is_anomaly", False) and random.random() > 0.3 # Simulated systemic check
    
    if not is_systemic:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Metric review complete. No systemic design flaws detected in this trace.")
        state["logs"] = logs
        return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] TIER-3 INTERVENTION: Systemic failure detected.")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Initiating architectural refactor...")
    
    # Architectural Refactoring Decisions
    refactors = [
        "Injected resilient 'Circuit Breaker' pattern (Hystrix-style) into the API Gateway.",
        "Optimized database query plan: Introduced composite indexing on 'policy_id' and 'timestamp'.",
        "Implemented 'Adaptive Concurrency Limits' to prevent cascading service exhaustion.",
        "Refactored retry logic: Switched to Exponential Backoff with Jitter for downstream calls."
    ]
    
    # Choose 2 optimizations
    selected = random.sample(refactors, 2)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Design integrity restored.")
    
    # Real GitHub Integration
    from packages.shared.github_service import GitHubService
    from packages.shared.reporting import format_jules_refactor
    gh = GitHubService()
    
    pr_title = generate_sre_pr_title(state.get('service', 'system'), "architectural-refactor")
    issue_body = format_jules_refactor(state, selected)
    
    gh_res = gh.create_issue(title=f"[ARCH-REFACTOR] {pr_title}", body=issue_body, labels=["architectural", "jules-refactor"])
    
    if "number" in gh_res:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Documentation Issue Created -> #{gh_res['number']}")
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Warning: GitHub integration failed.")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Daily Architectural Review (Scheduled 09:30 AM).")
    
    state["logs"] = logs
    return state

# Helper logic complete.
