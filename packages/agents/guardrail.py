from datetime import datetime

def guardrail_agent(state):
    """ Agent: Guardrail (Safety Enforcer) - Phase: [DECIDE] """
    logs = state.get("logs", [])
    if not state.get("error_spans"): return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] [DECIDE] Evaluating safety of proposed remediation. Confidence: {state.get('confidence_score', 0)}")
    
    # Mathematical Confidence Check
    if state.get("confidence_score", 0) < 0.70:
        state["decision"] = "REQUIRE_APPROVAL"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] [DECIDE] SAFETY_BREACH: Confidence below threshold. Escalating to SRE on-call.")
    else:
        # In a real system, this would also check against OPA/Sentinel policies
        state["decision"] = "ALLOW"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] [DECIDE] POLICY_BYPASS: Remediation plan within safety parameters. Execution permitted.")

    state["logs"] = logs
    return state
