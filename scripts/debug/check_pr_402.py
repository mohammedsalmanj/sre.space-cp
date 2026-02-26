import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_pr_402():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    owner = "mohammedsalmanj"
    repo = "sre.space-cp"
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/402"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        pr = res.json()
        print(f"PR #402 State: {pr['state']}, Merged: {pr['merged']}")
    else:
        print(f"PR #402 not found or error: {res.status_code}")

if __name__ == "__main__":
    check_pr_402()
