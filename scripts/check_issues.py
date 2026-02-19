import os
import requests
from dotenv import load_dotenv

load_dotenv()

def list_recent_issues():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    owner = "mohammedsalmanj"
    repo = "sre.space-cp"
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    res = requests.get(url, headers=headers, params={"state": "open", "per_page": 5})
    if res.status_code == 200:
        issues = res.json()
        for issue in issues:
            print(f"#{issue['number']}: {issue['title']}")
    else:
        print(f"Failed: {res.status_code} - {res.text}")

if __name__ == "__main__":
    list_recent_issues()
