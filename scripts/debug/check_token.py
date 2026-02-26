import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
repo = "sre.space-cp" # Adjust if your .env repo is different
owner = "mohammedsalmanj"

print(f"Checking Token Permissions for {owner}/{repo}...")

# Check Issues (Read/Write)
url = f"https://api.github.com/repos/{owner}/{repo}/issues"
try:
    # Try creating a dummy issue to test WRITE permission
    issue_data = {"title": "SRE Token Write Check 2", "body": "Verifying permissions."}
    res = requests.post(url, headers=headers, json=issue_data, timeout=10)
    
    if res.status_code == 201:
        print("✅ WRITE ACCESS VALIDATED (Issue Created)")
        # Clean up
        issue_num = res.json().get('number')
        requests.patch(f"{url}/{issue_num}", headers=headers, json={"state": "closed"})
    elif res.status_code == 403:
        print("❌ WRITE ACCESS DENIED (403 Forbidden)")
        print("   -> Token lacks 'Issues: Read/Write' permission.")
    else:
        print(f"⚠️ Unexpected status: {res.status_code}")
except Exception as e:
    print(f"Error checking permissions: {e}")
