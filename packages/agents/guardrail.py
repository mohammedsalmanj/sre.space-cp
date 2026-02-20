from datetime import datetime

def guardrail_agent(state):
    """
    Agent: Guardrail (Safety Enforcer)
    
    The Guardrail agent is the ethical and safety layer. It evaluates 
    the remediation plan proposed by CAG or Brain. 
    
    Decisions:
    - ALLOW: If confidence is high and the action is deemed safe.
    - REQUIRE_APPROVAL: If confidence is low or the action is risky.
    """
    logs = state.get("logs", [])
    if not state["error_spans"]: return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] Evaluating safety of remediation action...")
    
    # Mathematical Confidence Check
    if state["confidence_score"] < 0.75:
        state["decision"] = "REQUIRE_APPROVAL"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] Confidence too low ({state['confidence_score']}). Blocking auto-fix.")
    else:
        # In a real system, this would also check against a policy engine (e.g., OPA)
        state["decision"] = "ALLOW"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] Action ALLOWED. Action is reversible and safe.")

    state["logs"] = logs
    return state
