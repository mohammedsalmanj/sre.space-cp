import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def test_github():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    owner = "mohammedsalmanj"
    repo = "sre.space-cp"
    
    if not token:
        print("Error: GITHUB_PERSONAL_ACCESS_TOKEN not found")
        return

    print(f"Testing GitHub Access for {owner}/{repo}...")
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Test user
    res = requests.get("https://api.github.com/user", headers=headers)
    if res.status_code == 200:
        user = res.json()
        print(f"Token OK: Authenticated as {user['login']}")
    else:
        print(f"Token Failed: {res.status_code} {res.text}")
        return

    # Test repo
    res = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
    if res.status_code == 200:
        print(f"Repo OK: Found {owner}/{repo}")
    else:
        print(f"Repo Failed: {res.status_code} {res.text}")

if __name__ == "__main__":
    test_github()
