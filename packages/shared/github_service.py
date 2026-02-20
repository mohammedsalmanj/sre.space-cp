import os
import requests
import base64
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
        if not self.token: return {"error": "No token found"}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        data = {"title": title, "body": body, "labels": labels or ["sre-anomaly"]}
        try:
            res = requests.post(url, headers=self.headers, json=data, timeout=30)
            return res.json()
        except Exception as e: return {"error": str(e)}

    def create_comment(self, issue_number, body):
        if not self.token: return {"error": "No token found"}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        try:
            res = requests.post(url, headers=self.headers, json={"body": body}, timeout=30)
            return res.json()
        except Exception as e: return {"error": str(e)}

    def get_ref_sha(self, ref="heads/main"):
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/ref/{ref}"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            return res.json().get("object", {}).get("sha")
        except: return None

    def create_branch(self, branch_name, base_sha):
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs"
        data = {"ref": f"refs/heads/{branch_name}", "sha": base_sha}
        try:
            res = requests.post(url, headers=self.headers, json=data, timeout=10)
            return res.json()
        except Exception as e: return {"error": str(e)}

    def create_or_update_file(self, path, message, content, branch, sha=None):
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{path}"
        data = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch
        }
        if sha: data["sha"] = sha
        try:
            res = requests.put(url, headers=self.headers, json=data, timeout=30)
            return res.json()
        except Exception as e: return {"error": str(e)}

    def create_pr(self, title, head, base="main", body=""):
        if not self.token: return {"error": "No token found"}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls"
        data = {"title": title, "head": head, "base": base, "body": body}
        try:
            res = requests.post(url, headers=self.headers, json=data, timeout=30)
            return res.json()
        except Exception as e: return {"error": str(e)}

    def merge_pr(self, pull_number, commit_title=None):
        if not self.token: return {"error": "No token found"}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pull_number}/merge"
        data = {"commit_title": commit_title, "merge_method": "squash"}
        try:
            res = requests.put(url, headers=self.headers, json=data, timeout=30)
            return res.json()
        except Exception as e: return {"error": str(e)}

    def list_issues(self, state="open", per_page=10):
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        params = {"state": state, "per_page": per_page, "sort": "created", "direction": "desc"}
        try:
            res = requests.get(url, headers=self.headers, params=params, timeout=10)
            return res.json()
        except: return []
