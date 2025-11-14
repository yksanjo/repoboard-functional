"""GitHub API client for fetching repository data."""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import settings
from shared.schemas import RepoMetadata


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.github_token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = 0
    
    def _check_rate_limit(self):
        """Check and wait if rate limit is reached."""
        if self.rate_limit_remaining < 10:
            wait_time = max(0, self.rate_limit_reset - time.time() + 1)
            if wait_time > 0:
                print(f"Rate limit reached. Waiting {wait_time:.0f} seconds...")
                time.sleep(wait_time)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to GitHub API with rate limiting."""
        self._check_rate_limit()
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        
        # Update rate limit info
        if "X-RateLimit-Remaining" in response.headers:
            self.rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
        if "X-RateLimit-Reset" in response.headers:
            self.rate_limit_reset = int(response.headers["X-RateLimit-Reset"])
        
        response.raise_for_status()
        return response.json()
    
    def get_trending_repos(self, language: Optional[str] = None, since: str = "daily") -> List[Dict[str, Any]]:
        """
        Get trending repositories.
        Note: GitHub doesn't have an official trending API, so this uses search with sorting.
        """
        query_parts = ["stars:>100"]
        if language:
            query_parts.append(f"language:{language}")
        
        query = " ".join(query_parts)
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
        }
        
        results = []
        for page in range(1, 6):  # Get top 500 repos
            params["page"] = page
            try:
                data = self._make_request("/search/repositories", params)
                results.extend(data.get("items", []))
                time.sleep(0.5)  # Be nice to API
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break
        
        return results
    
    def get_repo_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get detailed information about a repository."""
        return self._make_request(f"/repos/{owner}/{repo}")
    
    def get_repo_readme(self, owner: str, repo: str) -> Optional[str]:
        """Get README content for a repository."""
        try:
            data = self._make_request(f"/repos/{owner}/{repo}/readme")
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content
        except Exception:
            return None
    
    def get_repo_languages(self, owner: str, repo: str) -> Dict[str, float]:
        """Get language statistics for a repository."""
        try:
            data = self._make_request(f"/repos/{owner}/{repo}/languages")
            total = sum(data.values())
            return {lang: count / total for lang, count in data.items()} if total > 0 else {}
        except Exception:
            return {}
    
    def get_repo_file_tree(self, owner: str, repo: str, branch: str = "main") -> Optional[Dict[str, Any]]:
        """Get file tree structure for a repository."""
        try:
            data = self._make_request(f"/repos/{owner}/{repo}/git/trees/{branch}?recursive=1")
            return self._parse_file_tree(data.get("tree", []))
        except Exception:
            return None
    
    def _parse_file_tree(self, tree: List[Dict]) -> Dict[str, Any]:
        """Parse GitHub tree structure into a hierarchical format."""
        result = {}
        for item in tree:
            path_parts = item["path"].split("/")
            current = result
            for part in path_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[path_parts[-1]] = {
                "type": item["type"],
                "size": item.get("size", 0),
            }
        return result
    
    def get_repo_commits(self, owner: str, repo: str, since: Optional[datetime] = None) -> int:
        """Get commit count (approximate)."""
        try:
            params = {"per_page": 1}
            if since:
                params["since"] = since.isoformat()
            data = self._make_request(f"/repos/{owner}/{repo}/commits", params)
            # Get total from Link header if available, otherwise estimate
            return len(data) if isinstance(data, list) else 0
        except Exception:
            return 0
    
    def get_repo_contributors(self, owner: str, repo: str) -> int:
        """Get contributor count."""
        try:
            data = self._make_request(f"/repos/{owner}/{repo}/contributors", {"per_page": 1, "anon": "true"})
            # This is an approximation - GitHub doesn't return total count easily
            return len(data) if isinstance(data, list) else 0
        except Exception:
            return 0
    
    def calculate_star_velocity(self, repo_data: Dict[str, Any]) -> float:
        """Calculate stars gained per day."""
        created_at = datetime.fromisoformat(repo_data["created_at"].replace("Z", "+00:00"))
        now = datetime.now(created_at.tzinfo)
        days_old = (now - created_at).days
        if days_old == 0:
            days_old = 1
        return repo_data.get("stargazers_count", 0) / days_old
    
    def fetch_repo_metadata(self, repo_data: Dict[str, Any]) -> RepoMetadata:
        """Fetch complete metadata for a repository."""
        owner = repo_data["owner"]["login"]
        name = repo_data["name"]
        
        # Fetch additional data
        readme = self.get_repo_readme(owner, name)
        languages = self.get_repo_languages(owner, name)
        file_tree = self.get_repo_file_tree(owner, name, repo_data.get("default_branch", "main"))
        
        # Parse dates
        created_at = datetime.fromisoformat(repo_data["created_at"].replace("Z", "+00:00")) if repo_data.get("created_at") else None
        updated_at = datetime.fromisoformat(repo_data["updated_at"].replace("Z", "+00:00")) if repo_data.get("updated_at") else None
        pushed_at = datetime.fromisoformat(repo_data["pushed_at"].replace("Z", "+00:00")) if repo_data.get("pushed_at") else None
        
        star_velocity = self.calculate_star_velocity(repo_data)
        
        return RepoMetadata(
            url=repo_data["html_url"],
            full_name=repo_data["full_name"],
            name=name,
            owner=owner,
            description=repo_data.get("description"),
            readme=readme,
            languages=languages,
            stars=repo_data.get("stargazers_count", 0),
            forks=repo_data.get("forks_count", 0),
            watchers=repo_data.get("watchers_count", 0),
            open_issues=repo_data.get("open_issues_count", 0),
            created_at=created_at,
            updated_at=updated_at,
            pushed_at=pushed_at,
            default_branch=repo_data.get("default_branch", "main"),
            topics=repo_data.get("topics", []),
            license=repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
            archived=repo_data.get("archived", False),
            file_tree=file_tree,
            commit_count=0,  # Would need pagination to get accurate count
            contributor_count=0,  # Would need pagination
            star_velocity=star_velocity,
        )

