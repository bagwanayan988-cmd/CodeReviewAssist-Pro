import os
import tempfile
import zipfile
from urllib.parse import urlparse

import requests

from app.services.ai_service import AIService


class GitHubService:
    """
    Handles downloading GitHub repositories,
    fetching repository metadata,
    and sending source code to AIService.
    """

    SUPPORTED_EXTENSIONS = {
        ".py",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".sql",
        ".json",
        ".xml",
        ".md",
    }

    MAX_FILE_SIZE = 100 * 1024
    MAX_TOTAL_CHARS = 50000

    @staticmethod
    def analyze_repository(repo_url: str, language: str = "Repository"):

        owner, repo = GitHubService._parse_repo_url(repo_url)

        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"

        response = requests.get(zip_url, timeout=30)

        if response.status_code != 200:
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
            response = requests.get(zip_url, timeout=30)

        response.raise_for_status()

        with tempfile.TemporaryDirectory() as temp_dir:

            zip_path = os.path.join(temp_dir, "repo.zip")

            with open(zip_path, "wb") as f:
                f.write(response.content)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            combined_code = GitHubService._collect_source_code(temp_dir)

        if not combined_code.strip():
            raise ValueError("No supported source code files found.")

        ai = AIService()

        return ai.review_code(
            code=combined_code,
            language=language,
        )

    @staticmethod
    def get_repository_info(repo_url: str):
        """
        Fetch repository information from GitHub API.
        """

        owner, repo = GitHubService._parse_repo_url(repo_url)

        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        response = requests.get(api_url, timeout=15)

        response.raise_for_status()

        data = response.json()

        return {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "owner": data.get("owner", {}).get("login"),
            "description": data.get("description"),
            "language": data.get("language"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "watchers": data.get("watchers_count"),
            "open_issues": data.get("open_issues_count"),
            "default_branch": data.get("default_branch"),
            "updated_at": data.get("updated_at"),
            "html_url": data.get("html_url"),
        }

    @staticmethod
    def _parse_repo_url(url: str):

        parsed = urlparse(url)

        if parsed.netloc.lower() != "github.com":
            raise ValueError("Only GitHub repositories are supported.")

        parts = parsed.path.strip("/").split("/")

        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository URL.")

        owner = parts[0]
        repo = parts[1]

        if repo.endswith(".git"):
            repo = repo[:-4]

        return owner, repo

    @staticmethod
    def _collect_source_code(root_folder: str):

        collected = []
        total_chars = 0

        for root, dirs, files in os.walk(root_folder):

            dirs[:] = [
                d for d in dirs
                if d not in {
                    ".git",
                    "node_modules",
                    "__pycache__",
                    "venv",
                    ".venv",
                }
            ]

            for filename in files:

                ext = os.path.splitext(filename)[1].lower()

                if ext not in GitHubService.SUPPORTED_EXTENSIONS:
                    continue

                path = os.path.join(root, filename)

                if os.path.getsize(path) > GitHubService.MAX_FILE_SIZE:
                    continue

                try:

                    with open(
                        path,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:

                        code = f.read()

                except Exception:
                    continue

                header = f"\n\n===== FILE: {filename} =====\n"

                chunk = header + code

                if total_chars + len(chunk) > GitHubService.MAX_TOTAL_CHARS:

                    remaining = GitHubService.MAX_TOTAL_CHARS - total_chars

                    collected.append(chunk[:remaining])

                    return "".join(collected)

                collected.append(chunk)

                total_chars += len(chunk)

        return "".join(collected)