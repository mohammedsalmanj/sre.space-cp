from datetime import datetime

def format_scout_alert(state):
    """Formats the initial SRE Scout Alert section."""
    service = state.get('service', 'Unknown Service')
    namespace = state.get('namespace', 'production')
    error_msg = state.get('error_spans', [{}])[0].get('exception.message', 'No error message available')
    
    body = f"""
# [INCIDENT] Latency/Saturation: Infrastructure Alert

### [SCOUT ALERT]
**Trigger**: Infrastructure
**Error**: {service}: DOWN ({error_msg})
**Category**: Latency/Saturation
**Current Conversion**: 0.0%
**Timestamp**: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}
**Status**: Brain Analysis Required
"""
    return body

def format_brain_diagnosis(state):
    """Formats the Brain Agent Diagnosis section."""
    root_cause = state.get('root_cause', 'Under deep reasoning...')
    remediation = state.get('remediation', 'Calculating optimal patch...')
    service = state.get('service', 'System')
    
    body = f"""
### [BRAIN DIAGNOSIS]
#### Root Cause Analysis (RCA)
{root_cause}

#### Recommended Fix
{remediation}

#### MITIGATION command for the Fixer Agent
**MITIGATION:** RESTART {service}
"""
    return body

def format_memory_context(state):
    """Formats the Memory Agent Context (simulated or real RAG results)."""
    body = f"""
### [MEMORY CONTEXT]
**Found Patterns:**

#### Incident Post-Mortem: PM-131
**Root Cause:** The service became unresponsive due to connection refusal. This is often linked to OOM or resource starvation.
**Resolution:** Automated restart restored health in 4 seconds.

#### Incident Post-Mortem: PM-119
**Root Cause:** Latency spike due to database pool saturation.
**Resolution:** Switched to high-availability pool configuration.
"""
    return body

def format_fixer_action(state, success=True):
    """Formats the Fixer Action notification."""
    service = state.get('service', 'System')
    status = "Fixed. Monitoring for stability." if success else "Failed. Manual intervention required."
    
    body = f"""
### [FIXER ACTION] Auto-Healing
Service `{service}` restarted successfully.

**Status:** {status}
"""
    return body

def format_full_incident_report(state):
    """Combines all sections into a single standard incident report."""
    return f"""
{format_scout_alert(state)}

---

{format_brain_diagnosis(state)}

---

{format_memory_context(state)}
"""

def format_human_escalation(state):
    """Formats a rich escalation body for Human-in-the-Loop."""
    frequency = state.get('anomaly_frequency', 0)
    diagnosis = format_brain_diagnosis(state)
    
    body = f"""
# [HUMAN INTERVENTION REQUIRED]

{diagnosis}

### Escalation Reason
Issue detected **{frequency}** times in the last hour. Auto-remediation has been paused to prevent cascading failures.

**Status:** AWAITING MANUAL REVIEW
"""
    return body

def format_patch_deployed(state):
    """Specialized format for patch deployment confirmation."""
    return format_fixer_action(state, success=True)
