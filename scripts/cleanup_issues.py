import requests
import os

token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
owner = "mohammedsalmanj"
repo = "sre.space-cp"

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

def close_all_issues():
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open"
    res = requests.get(url, headers=headers)
    issues = res.json()
    
    print(f"Found {len(issues)} open issues.")
    for issue in issues:
        number = issue["number"]
        try:
            print(f"Closing #{number}...")
            close_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
            requests.patch(close_url, headers=headers, json={"state": "closed"}, timeout=10)
        except Exception as e:
            print(f"Failed to close #{number}: {e}")

if __name__ == "__main__":
    close_all_issues()
