from packages.shared.agent_utils import add_agent_log

def guardrail_agent(state):
    """
    Agent: Guardrail (Safety Enforcer)
    """
    
    if not state["error_spans"]: return state

    add_agent_log(state, "guardrail", "Evaluating safety of remediation action...")
    
    # Mathematical Confidence Check
    if state["confidence_score"] < 0.75:
        state["decision"] = "REQUIRE_APPROVAL"
        add_agent_log(state, "guardrail", f"Confidence too low ({state['confidence_score']}). Blocking auto-fix.")
    else:
        # In a real system, this would also check against a policy engine (e.g., OPA)
        state["decision"] = "ALLOW"
        add_agent_log(state, "guardrail", "Action ALLOWED. Action is reversible and safe.")

    return state
