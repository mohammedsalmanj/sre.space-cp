from datetime import datetime

CAG_FAST_CACHE = {
    "CRITICAL: High Error Rate detected": {
        "root_cause": "System Saturation: DB Pool Exhaustion",
        "remediation": "SCALE: Increase pool size",
        "remediation_type": "infra",
        "confidence": 0.95
    },
    "WARNING: Latency threshold exceeded": {
        "root_cause": "Service Degradation: High latency in downstream dependency",
        "remediation": "SCALE: Add compute resources or optimize queries",
        "remediation_type": "infra",
        "confidence": 0.92
    }
}

def cag_agent(state):
    """ Agent: CAG (Tier-1 Fast Cache) - Phase: [ORIENT] """
    logs = state.get("logs", [])
    if not state.get("error_spans"): return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] [ORIENT] Analyzing incident signature against historical resolution cache...")
    
    # Robust message extraction
    span = state["error_spans"][0]
    msg = span.get("message", span.get("exception.message", "Unknown Error"))
    
    matched = False
    for pattern, known in CAG_FAST_CACHE.items():
        if pattern in msg:
            state["root_cause"] = known["root_cause"]
            state["remediation"] = known["remediation"]
            state["remediation_type"] = known.get("remediation_type", "other")
            state["confidence_score"] = known["confidence"]
            state["cache_hit"] = True
            
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] [ORIENT] SIGNATURE_MATCH: Known incident pattern found in local cache.")
            
            try:
                from packages.shared.github_service import GitHubService
                from packages.shared.reporting import format_full_incident_report
                gh = GitHubService()
                issue_title = f"[INCIDENT] {state.get('service', 'System')} - {state['root_cause']}"
                gh_res = gh.create_issue(title=issue_title, body=format_full_incident_report(state), labels=["incident", "cag-hit"])
                if "number" in gh_res:
                    state["incident_number"] = gh_res["number"]
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] [ORIENT] Incident persisted to GitHub: #{gh_res['number']}")
            except:
                pass
            matched = True
            break
            
    if not matched:
        state["cache_hit"] = False
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] [ORIENT] CACHE_MISS: No historical signature matches. Escalating to Tier-2 [ORIENT/DECIDE].")

    state["logs"] = logs
    return state
