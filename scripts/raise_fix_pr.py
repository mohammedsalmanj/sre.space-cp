import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
load_dotenv()

from packages.shared.github_service import GitHubService

def raise_fix_pr():
    gh = GitHubService()
    title = "[FIX] Vercel 404 and Monorepo Naming Refactor"
    head = "fix/vercel-404-monorepo-naming"
    body = """
## Fix: Vercel 404 and Monorepo Alignment

This PR addresses the Vercel deployment issues and standardizes the monorepo structure for better Python import compatibility.

### Key Changes:
1. **Vercel 404 Fix**: Created a root-level `main.py` entry point and updated `vercel.json` to point to it correctly.
2. **Naming Refactor**: Renamed `apps/control-plane` to `apps/control_plane` and `apps/websocket-bridge` to `apps/websocket_bridge` to comply with Python module naming conventions.
3. **Internal Imports**: Updated cross-package imports within `apps/control_plane` to use absolute paths.
4. **Emoji Sanitization**: Removed all emojis from agent logs, issue titles, and print statements to prevent `UnicodeEncodeError` on Windows systems.
5. **Stability**: Confirmed the SRE Control Loop is functional with a successful chaos test (Issue #403).

### Verification:
- App runs locally on port 8001 via root `main.py`.
- Control loop successfully triggered and created a GitHub issue.
- No encoding errors in sanitized logs.

*Automated Fix by SRE-Space Engine.*
"""
    res = gh.create_pr(title=title, head=head, body=body)
    if "number" in res:
        print(f"SUCCESS: PR Raised #{res['number']}")
        return res['number']
    else:
        print(f"ERROR: {res}")
        return None

if __name__ == "__main__":
    raise_fix_pr()
