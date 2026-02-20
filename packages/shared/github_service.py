import os
import requests
from datetime import datetime

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.owner = "mohammedsalmanj"
        self.repo = "sre.space-cp"
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_issue(self, title, body, labels=None):
        print(f"[GitHubService] Creating issue: {title}")
        if not self.token:
            print("[GitHubService] No token found")
            return {"error": "No token found"}
        
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        data = {
            "title": title,
            "body": body,
            "labels": labels or ["sre-anomaly"]
        }
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            print(f"[GitHubService] Response: {response.status_code}")
            return response.json()
        except Exception as e:
            print(f"[GitHubService] Request failed: {str(e)}")
            return {"error": str(e)}

    def create_comment(self, issue_number, body):
        print(f"[GitHubService] Adding comment to issue #{issue_number}")
        if not self.token:
            return {"error": "No token found"}
        
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        data = {"body": body}
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def create_pr(self, title, head, base="main", body=""):
        print(f"[GitHubService] Creating PR: {title}")
        if not self.token:
            return {"error": "No token found"}
        
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls"
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ [GitHubService] Request failed: {str(e)}")
            return {"error": str(e)}

    def merge_pr(self, pull_number, commit_title=None):
        print(f"[GitHubService] Merging PR #{pull_number}")
        if not self.token:
            return {"error": "No token found"}
        
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pull_number}/merge"
        data = {
            "commit_title": commit_title or f"Merging SRE Autonomous PR #{pull_number}",
            "merge_method": "squash"
        }
        try:
            response = requests.put(url, headers=self.headers, json=data, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ [GitHubService] Merge failed: {str(e)}")
            return {"error": str(e)}

    def get_repo_info(self):
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}"
        response = requests.get(url, headers=self.headers, timeout=10)
        return response.json()
