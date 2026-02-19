import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
load_dotenv()

from packages.shared.github_service import GitHubService

def raise_standard_pr():
    gh = GitHubService()
    title = "[FEAT] Standardized SRE Incident Reporting"
    head = "fix/standardize-incident-reporting"
    body = """
## Standardized Incident Reporting

This PR establishes a new professional standard for incident reporting, aligning with the format used in high-maturity SRE organizations (e.g., Issue #137).

### Key Features:
1. **Unified Incident Thread**: The initial agent (CAG or Brain) now creates a comprehensive incident report (`[INCIDENT]`) and stores the ID. Subsequent agents (Fixer) now post updates as **comments** on the same issue rather than creating separate logs.
2. **Rich Reporting Template**: Implemented `format_full_incident_report` in `reporting.py`, which includes:
    - **Scout Alert**: Metadata about the detection.
    - **Brain Diagnosis**: Detailed RCA and recommended mitigation.
    - **Memory Context**: Historical patterns and past post-mortems for context.
    - **Fixer Action**: Automated execution results.
3. **Cross-Agent Sync**: Added `incident_number` to the SRE State to ensure all agents are aware of the active GitHub thread.
4. **Platform Stability**: Completely removed emojis from reports and logs to prevent `UnicodeEncodeError` on Windows consoles.

### Verification:
- Chaos test (HTTP 500) successfully triggered.
- **Issue #410** created with full Scout+Brain+Memory context.
- **Fixer Comment** added to #410 with auto-healing confirmation.
- No crashes or encoding errors detected.

*Automated Stability Patch by SRE-Space Engine.*
"""
    res = gh.create_pr(title=title, head=head, body=body)
    if "number" in res:
        print(f"SUCCESS: PR Raised #{res['number']}")
        return res['number']
    else:
        print(f"ERROR: {res}")
        return None

if __name__ == "__main__":
    raise_standard_pr()
