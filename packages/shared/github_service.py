import os
import requests
from datetime import datetime

class GitHubService:
    """
    Standard Operating Procedure: GitHub Veracity Interface.
    This service acts as the 'hands' of the SRE squad, interacting with GitHub
    to document incidents, propose fixes via PRs, and manage the GitOps flow.
    """
    def __init__(self):
        # Authentication token for GitHub API (must have 'repo' scope)
        self.token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.owner = "mohammedsalmanj"
        self.repo = "sre.space-cp"
        self.base_url = "https://api.github.com"
        # Standard GitHub API Headers
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_issue(self, title, body, labels=None):
        """
        Spawns a 'War Room' issue for the SRE incident. 
        Labels help categorize the incident for the Brain agent's memory lookup.
        """
        print(f"[GitHubService] Creating issue: {title}")
        if not self.token:
            print("[GitHubService] No GITHUB_TOKEN found in environment.")
            return {"error": "No token found"}
        
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        data = {
            "title": title,
            "body": body,
            "labels": labels or ["sre-anomaly"]
        }
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            return response.json()
        except Exception as e:
            print(f"❌ [GitHubService] Request failed: {str(e)}")
            return {"error": str(e)}

    def create_pr(self, title, head, base="main", body=""):
        """
        Creates a Pull Request representing a proposed autonomous fix.
        The 'head' branch should containing the code patch.
        """
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
            print(f"❌ [GitHubService] PR creation failed: {str(e)}")
            return {"error": str(e)}

    def create_ref(self, ref, sha):
        """Creates a new Git reference (branch) for the remediation activity."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs"
        data = {"ref": f"refs/heads/{ref}", "sha": sha}
        res = requests.post(url, headers=self.headers, json=data, timeout=10)
        return res.json()

    def get_ref(self, ref="heads/main"):
        """Retrieves the SHA of a specific branch, typically to fork from it."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/ref/{ref}"
        res = requests.get(url, headers=self.headers, timeout=10)
        return res.json()

    def update_file(self, path, message, content, branch, sha=None):
        """
        Low-level content update. Used by Fixer/Jules agents to apply patches
        directly through the GitHub contents API without local clone.
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{path}"
        data = {
            "message": message,
            "content": content,
            "branch": branch
        }
        if sha: data["sha"] = sha
        res = requests.put(url, headers=self.headers, json=data, timeout=10)
        return res.json()

    def get_repo_info(self):
        """Connectivity check for the GitHub veracity feed."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}"
        response = requests.get(url, headers=self.headers, timeout=10)
        return response.json()
