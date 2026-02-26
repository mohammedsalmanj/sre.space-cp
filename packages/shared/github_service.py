"""
File: packages/shared/github_service.py
Layer: Shared / Integration / Veracity
Purpose: Decouples the SRE control plane from the GitHub REST API.
Problem Solved: Provides a unified interface for incident tracking (Issues) and remediation delivery (PRs) via GitOps.
Interaction: Used by Brain (issue creation), Fixer (PR creation), and Curator (issue closure).
Dependencies: requests, os
Inputs: Issue/PR metadata, file contents for patches
Outputs: GitHub API response objects (JSON)
"""
import os
import requests
from datetime import datetime

class GitHubService:
    """
    Service Layer for GitHub API interactions.
    Handles the 'Veracity' aspect of the SRE OODA loop by creating an external audit trail.
    """
    def __init__(self):
        """Initializes the service with credentials from environment variables."""
        self.token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.owner = "mohammedsalmanj"
        self.repo = "sre.space-cp"
        self.base_url = "https://api.github.com"
        
        # Standard GitHub API Headers (REST v3)
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_issue(self, title: str, body: str, labels: list = None) -> dict:
        """
        Creates a 'War Room' issue for tracking an SRE incident lifecycle.
        
        Args:
            title (str): Descriptive title of the anomaly.
            body (str): Detailed RCA and context in markdown.
            labels (list, optional): Categorization labels (e.g. 'incident').
        Returns:
            dict: The created issue metadata.
        """
        print(f"[GitHubService] Creating issue: {title}")
        if os.getenv("STUB_GITHUB") == "true":
            return {"number": 100 + int(datetime.now().strftime('%M%S')), "title": title}
            
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

    def create_pr(self, title: str, head: str, base: str = "main", body: str = "") -> dict:
        """
        Creates a Pull Request representing an autonomous remediation fix.
        
        Args:
            title (str): PR title.
            head (str): The feature/fix branch name.
            base (str): The target branch (default: main).
            body (str): Description of the fix and audit data.
        Returns:
            dict: The created PR metadata.
        """
        print(f"[GitHubService] Creating PR: {title}")
        if os.getenv("STUB_GITHUB") == "true":
            return {"number": 200 + int(datetime.now().strftime('%M%S')), "title": title}

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

    def create_ref(self, ref: str, sha: str) -> dict:
        """
        Creates a new Git reference (branch) for remediation.
        
        Args:
            ref (str): The short ref name (e.g. 'fix-123').
            sha (str): The source commit SHA.
        Returns:
            dict: Reference creation status.
        """
        if os.getenv("STUB_GITHUB") == "true": return {"ref": ref}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs"
        data = {"ref": f"refs/heads/{ref}", "sha": sha}
        res = requests.post(url, headers=self.headers, json=data, timeout=10)
        return res.json()

    def get_ref(self, ref: str = "heads/main") -> dict:
        """
        Retrieves the latest SHA for a specific branch.
        
        Args:
            ref (str): The ref to query (e.g. 'heads/main').
        Returns:
            dict: The branch reference object.
        """
        if os.getenv("STUB_GITHUB") == "true":
            return {"object": {"sha": "mock_sha_12345"}}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/ref/{ref}"
        res = requests.get(url, headers=self.headers, timeout=10)
        return res.json()

    def update_file(self, path: str, message: str, content: str, branch: str, sha: str = None) -> dict:
        """
        Low-level content update via GitHub contents API.
        
        Args:
            path (str): Repository path for the file.
            message (str): Commit message.
            content (str): Base64 encoded file content.
            branch (str): Target branch.
            sha (str, optional): SHA of the existing file if updating.
        Returns:
            dict: Update confirmation.
        """
        if os.getenv("STUB_GITHUB") == "true": return {"content": {"name": path}}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{path}"
        data = {
            "message": message,
            "content": content,
            "branch": branch
        }
        if sha: data["sha"] = sha
        res = requests.put(url, headers=self.headers, json=data, timeout=10)
        return res.json()

    def get_repo_info(self) -> dict:
        """Connectivity check for verifying repository access."""
        if os.getenv("STUB_GITHUB") == "true":
            return {"name": self.repo, "owner": {"login": self.owner}}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}"
        response = requests.get(url, headers=self.headers, timeout=10)
        return response.json()

    def close_issue(self, issue_number: int) -> dict:
        """
        Closes a GitHub issue upon successful remediation verification.
        
        Args:
            issue_number (int): The ID of the issue to close.
        Returns:
            dict: Issue update status.
        """
        if os.getenv("STUB_GITHUB") == "true": return {"state": "closed"}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        data = {"state": "closed"}
        response = requests.patch(url, headers=self.headers, json=data, timeout=10)
        return response.json()

    def add_comment(self, issue_number: int, body: str) -> dict:
        """
        Adds a programmatic comment to an active incident issue.
        
        Args:
            issue_number (int): The target issue ID.
            body (str): Comment content in markdown.
        Returns:
            dict: Comment creation metadata.
        """
        if os.getenv("STUB_GITHUB") == "true": return {"id": 123}
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        data = {"body": body}
        response = requests.post(url, headers=self.headers, json=data, timeout=10)
        return response.json()
