import requests
import base64
from typing import List


class GitHubAPIError(Exception):
    pass


class GitHubAPI:
    def __init__(self, token: str, repo: str):
        self.token = token
        try:
            self.owner, self.repo_name = repo.split('/', 1)
        except ValueError:
            raise ValueError("Invalid repo format. Expected 'owner/repo'")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_pr_diff(self, pr_number: int) -> str:
        """Retrieve the diff for a pull request."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/pulls/{pr_number}"
        headers = self.headers.copy()
        headers["Accept"] = "application/vnd.github.v3.diff"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Failed to get PR diff: {e}") from e

    def post_pr_comment(self, pr_number: int, body: str) -> None:
        """Post a comment on a pull request."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/issues/{pr_number}/comments"
        try:
            response = requests.post(url, headers=self.headers, json={"body": body})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Failed to post PR comment: {e}") from e

    def post_commit_status(self, commit_sha: str, state: str, description: str) -> None:
        """Post a commit status."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/statuses/{commit_sha}"
        data = {"state": state, "description": description}
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Failed to post commit status: {e}") from e

    def get_file_content(self, path: str) -> str:
        """Get the content of a file in the repository."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/contents/{path}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            content = response.json()["content"]
            return base64.b64decode(content).decode("utf-8")
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Failed to get file content: {e}") from e
        except (KeyError, base64.binascii.Error) as e:
            raise GitHubAPIError(f"Failed to decode file content: {e}") from e

    def get_files(self) -> List[str]:
        """Get a list of all files in the main branch."""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo_name}/git/trees/main?recursive=1"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tree = response.json().get("tree", [])
            return [item["path"] for item in tree if item.get("type") == "blob"]
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Failed to get files: {e}") from e
        except (KeyError, TypeError) as e:
            raise GitHubAPIError(f"Failed to parse files response: {e}") from e
