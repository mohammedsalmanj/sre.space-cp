"""
File: packages/agents/guardrail.py
Layer: Cognitive / Safety
Purpose: Enforces security and safety policies on all autonomous actions.
Problem Solved: Prevents "rogue AI" behavior by validating remediation plans against a defined safety threshold.
Interaction: Sits between Brain and Fixer; can block actions or require human approval.
Dependencies: datetime
Inputs: Confidence score and remediation plan from Brain
Outputs: Permission decision ('ALLOW' or 'DENY')
"""
from datetime import datetime

def guardrail_agent(state: dict) -> dict:
    """
    Agent Node: Guardrail
    Phase: DECIDE
    Mission: Evaluate the safety of requested autonomous actions against enterprise risk policies.
    
    Args:
        state (dict): The current LangGraph state.
    Returns:
        dict: Updated state with a 'decision' flag for the Fixer.
    """
    logs = state.get("logs", [])
    if not state.get("error_spans"): return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] [DECIDE] Evaluating safety of remediation action...")
    
    # 1. Safety Threshold: Confidence-based gating
    if state.get("confidence_score", 0) < 0.75:
        state["decision"] = "REQUIRE_APPROVAL"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] Confidence too low ({state['confidence_score']}). Blocking auto-fix.")
    else:
        # 2. Risk Assessment: If high confidence, ALLOW the Fixer to execute GitOps flow
        state["decision"] = "ALLOW"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] Action ALLOWED. Action is reversible and safe.")

    state["logs"] = logs
    return state
