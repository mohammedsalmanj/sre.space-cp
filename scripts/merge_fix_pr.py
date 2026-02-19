import os
import requests
from dotenv import load_dotenv

load_dotenv()

def merge_pr(pr_number):
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    owner = "mohammedsalmanj"
    repo = "sre.space-cp"
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/merge"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    res = requests.put(url, headers=headers)
    if res.status_code == 200:
        print(f"SUCCESS: PR #{pr_number} Merged")
    else:
        print(f"ERROR: {res.status_code} - {res.text}")

if __name__ == "__main__":
    merge_pr(404)
