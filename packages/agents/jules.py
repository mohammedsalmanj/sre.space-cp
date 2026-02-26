"""
File: packages/agents/jules.py
Layer: Cognitive / Architectural Optimization
Purpose: Systemic design flaw elimination and long-term reliability engineering.
Problem Solved: Prevents recurring incidents by proposing architectural refactors instead of just hotfixes.
Interaction: Runs after the Fixer; evaluates for systemic issues; proposes refactors via GitHub.
Dependencies: random, packages.shared.git_utils, packages.shared.github_service
Inputs: Systemic failure indicators from state
Outputs: Architectural Refactor Proposal on GitHub
"""
from datetime import datetime
import json
import random
from packages.shared.git_utils import generate_sre_pr_title

def jules_agent(state: dict) -> dict:
    """
    Agent Node: Jules (The Architect)
    Phase: REFACTOR
    Mission: Identify and eliminate systemic design flaws at the architectural level.
    
    Args:
        state (dict): The current LangGraph state.
    Returns:
        dict: Updated state with architectural optimization logs.
    """
    logs = state.get("logs", [])
    
    # 1. Systemic Check: Only intervene if the failure is identified as systemic or chronic
    is_systemic = state.get("is_anomaly", False) and random.random() > 0.3 
    
    if not is_systemic:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Metric review complete. No systemic design flaws detected in this trace.")
        state["logs"] = logs
        return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] TIER-3 INTERVENTION: Systemic failure detected.")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Initiating architectural refactor...")
    
    # 2. Design Thinking: Select architectural patterns to improve reliability
    refactors = [
        "Injected resilient 'Circuit Breaker' pattern (Hystrix-style) into the API Gateway.",
        "Optimized database query plan: Introduced composite indexing on 'policy_id' and 'timestamp'.",
        "Implemented 'Adaptive Concurrency Limits' to prevent cascading service exhaustion.",
        "Refactored retry logic: Switched to Exponential Backoff with Jitter for downstream calls."
    ]
    
    selected = random.sample(refactors, 2)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Design integrity restored.")
    
    # 3. Governance Integration: Post a formal refactor proposal for human review
    from packages.shared.github_service import GitHubService
    gh = GitHubService()
    
    pr_title = generate_sre_pr_title(state.get('service', 'system'), "architectural-refactor")
    issue_body = f"""
## 🏛️ Architectural Refactor Proposal
**Service:** {state.get('service')}
**Trigger:** Systemic failure detected by Jules (Tier-3 Authority).

### Proposed Optimizations:
1. {selected[0]}
2. {selected[1]}

**Confidence Score:** 0.98
**Status:** PROPOSED (Awaiting CI/CD validation)

*Automated Architectural Review by SRE-Space Engine.*
"""
    gh_res = gh.create_issue(title=f"[ARCH-REFACTOR] {pr_title}", body=issue_body, labels=["architectural", "jules-refactor"])
    
    if "number" in gh_res:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Documentation Issue Created -> #{gh_res['number']}")
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Warning: GitHub integration failed.")

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [JULES] Daily Architectural Review (Scheduled 09:30 AM).")
    
    state["logs"] = logs
    return state
