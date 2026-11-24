"""Asynchronous GitHub API client for fetching repository metadata and file trees."""

import base64
import os
from typing import Dict, List, Optional
import httpx
from rich.console import Console

from git_ai_tracer.detectors.heuristics import analyze_repository_artifacts
from git_ai_tracer.models import RepositoryAnalysis, ScanSummary
from git_ai_tracer.scanner.cache import ScanCache

console = Console()


ECOSYSTEM_TOPICS = [
    ("Claude Code", "topic:claude-code"),
    ("Cursor Rules", "topic:cursor-rules"),
    ("Aider", "topic:aider"),
    ("Cline / Roo Code", "topic:cline"),
    ("GitHub Copilot", "topic:copilot"),
    ("Autonomous AI Agents", "topic:ai-agent"),
    ("Model Context Protocol (MCP)", "topic:mcp-server"),
    ("LangGraph Workflows", "topic:langgraph"),
    ("CrewAI Teams", "topic:crewai"),
    ("AutoGen", "topic:autogen"),
    ("ElizaOS", "topic:elizaos"),
]


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None, cache_enabled: bool = True):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.cache = ScanCache() if cache_enabled else None
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitAITracer/0.1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        self.headers = headers

    async def get_user_repositories(self, username: str, limit: int = 100) -> List[dict]:
        """Fetch all public repositories owned by the user."""
        repos = []
        page = 1
        per_page = min(limit, 100)

        async with httpx.AsyncClient(headers=self.headers, timeout=20.0) as client:
            while len(repos) < limit:
                url = f"{self.BASE_URL}/users/{username}/repos"
                params = {
                    "type": "owner",
                    "sort": "updated",
                    "per_page": per_page,
                    "page": page,
                }
                resp = await client.get(url, params=params)
                if resp.status_code == 404:
                    raise ValueError(f"GitHub user '{username}' not found.")
                elif resp.status_code == 403:
                    raise PermissionError(f"GitHub API rate limit exceeded or forbidden: {resp.text}")
                elif resp.status_code != 200:
                    raise RuntimeError(f"GitHub API returned {resp.status_code}: {resp.text}")

                data = resp.json()
                if not data:
                    break
                repos.extend(data)
                if len(data) < per_page:
                    break
                page += 1

        return repos[:limit]

    async def query_public_topic_stats(self, client: httpx.AsyncClient, query: str, limit: int = 10) -> tuple[int, List[dict]]:
        """Query GitHub search to get total count across all of GitHub plus top sample repos."""
        url = f"{self.BASE_URL}/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(limit, 100),
        }
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            return 0, []
        data = resp.json()
        total_count = data.get("total_count", 0)
        items = data.get("items", [])[:limit]
        return total_count, items

    async def search_repositories(self, query: str, limit: int = 50) -> List[dict]:
        """Search public repositories across GitHub by query or topic."""
        async with httpx.AsyncClient(headers=self.headers, timeout=20.0) as client:
            url = f"{self.BASE_URL}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": min(limit, 100),
            }
            resp = await client.get(url, params=params)
            if resp.status_code != 200:
                raise RuntimeError(f"GitHub search failed ({resp.status_code}): {resp.text}")
            data = resp.json()
            return data.get("items", [])[:limit]

    async def get_repo_tree(self, client: httpx.AsyncClient, owner: str, repo: str, default_branch: str) -> List[str]:
        """Fetch the full repository file tree in a single API call."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{default_branch}"
        resp = await client.get(url, params={"recursive": "1"})
        if resp.status_code != 200:
            return []
        data = resp.json()
        tree = data.get("tree", [])
        return [item["path"] for item in tree if "path" in item]

    async def get_repo_commits(self, client: httpx.AsyncClient, owner: str, repo: str, limit: int = 15) -> List[str]:
        """Fetch recent commit messages to inspect co-authorship and signatures."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        resp = await client.get(url, params={"per_page": limit})
        if resp.status_code != 200:
            return []
        commits = resp.json()
        messages = []
        if isinstance(commits, list):
            for c in commits:
                commit_obj = c.get("commit", {})
                msg = commit_obj.get("message", "")
                if msg:
                    messages.append(msg)
        return messages

    async def get_file_content(self, client: httpx.AsyncClient, owner: str, repo: str, path: str, branch: str) -> Optional[str]:
        """Fetch text content of a manifest file (requirements.txt, package.json, etc.)."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        resp = await client.get(url, params={"ref": branch})
        if resp.status_code != 200:
            return None
        data = resp.json()
        encoding = data.get("encoding")
        content_b64 = data.get("content")
        if encoding == "base64" and content_b64:
            try:
                return base64.b64decode(content_b64).decode("utf-8", errors="ignore")
            except Exception:
                return None
        return None

    async def analyze_repo(self, repo_data: dict) -> RepositoryAnalysis:
        """Scan a single repository, leveraging cache if available."""
        full_name = repo_data.get("full_name", "")
        pushed_at = repo_data.get("pushed_at")

        if self.cache:
            cached = self.cache.get(full_name, pushed_at)
            if cached:
                return cached

        name = repo_data.get("name", "")
        owner = repo_data.get("owner", {}).get("login", "")
        html_url = repo_data.get("html_url", "")
        description = repo_data.get("description") or ""
        default_branch = repo_data.get("default_branch") or "main"
        stars = repo_data.get("stargazers_count", 0)
        forks = repo_data.get("forks_count", 0)
        language = repo_data.get("language")
        topics = repo_data.get("topics") or []
        created_at = repo_data.get("created_at")

        file_paths: List[str] = []
        commit_messages: List[str] = []
        manifest_contents: Dict[str, str] = {}

        # Fetch repo tree and commit history
        async with httpx.AsyncClient(headers=self.headers, timeout=20.0) as client:
            file_paths = await self.get_repo_tree(client, owner, name, default_branch)
            commit_messages = await self.get_repo_commits(client, owner, name, limit=10)

            # Check for package manifests
            manifest_candidates = [
                "package.json",
                "requirements.txt",
                "pyproject.toml",
                "Cargo.toml",
                "smithery.yaml",
            ]
            for candidate in manifest_candidates:
                # Find matching file in tree
                matching = [p for p in file_paths if p.lower() == candidate or p.lower().endswith(f"/{candidate}")]
                for m in matching[:2]:  # limit to top 2 to preserve API rate limit
                    content = await self.get_file_content(client, owner, name, m, default_branch)
                    if content:
                        manifest_contents[m] = content

        analysis = analyze_repository_artifacts(
            name=name,
            full_name=full_name,
            html_url=html_url,
            file_paths=file_paths,
            manifest_contents=manifest_contents,
            commit_messages=commit_messages,
            description=description,
            topics=topics,
            stars=stars,
            forks=forks,
            primary_language=language,
            default_branch=default_branch,
            created_at=created_at,
            pushed_at=pushed_at,
        )

        if self.cache:
            self.cache.set(analysis)

        return analysis

    async def scan_user(self, username: str, limit: int = 100) -> ScanSummary:
        """Scan all public repositories for a target user and generate summary."""
        raw_repos = await self.get_user_repositories(username, limit=limit)
        analyses: List[RepositoryAnalysis] = []

        for repo in raw_repos:
            # Skip forks if desired, or include them (default include)
            analysis = await self.analyze_repo(repo)
            analyses.append(analysis)

        return self._build_summary("user", username, analyses)

    async def scan_search(self, query: str, limit: int = 50) -> ScanSummary:
        """Scan public repositories matching a query across GitHub."""
        raw_repos = await self.search_repositories(query, limit=limit)
        analyses: List[RepositoryAnalysis] = []

        for repo in raw_repos:
            analysis = await self.analyze_repo(repo)
            analyses.append(analysis)

        return self._build_summary("ecosystem", query, analyses)

    async def scan_ecosystem(self, repos_per_topic: int = 10) -> ScanSummary:
        """Scan and census public repositories across GitHub for AI tools and agent frameworks."""
        ecosystem_counts: Dict[str, int] = {}
        unique_repos: Dict[str, dict] = {}

        async with httpx.AsyncClient(headers=self.headers, timeout=25.0) as client:
            for label, query in ECOSYSTEM_TOPICS:
                try:
                    total_count, items = await self.query_public_topic_stats(client, query, limit=repos_per_topic)
                    ecosystem_counts[label] = total_count
                    for repo in items:
                        fn = repo.get("full_name")
                        if fn and fn not in unique_repos:
                            unique_repos[fn] = repo
                except Exception as e:
                    console.print(f"[yellow]Warning: query failed for '{query}': {e}[/yellow]")

        analyses: List[RepositoryAnalysis] = []
        for repo in unique_repos.values():
            try:
                analysis = await self.analyze_repo(repo)
                analyses.append(analysis)
            except Exception as e:
                console.print(f"[yellow]Skipping {repo.get('full_name')}: {e}[/yellow]")

        # Sort analyzed repos by stars descending
        analyses.sort(key=lambda r: r.stars, reverse=True)

        return self._build_summary(
            target_type="ecosystem",
            identifier="Global Public GitHub",
            analyses=analyses,
            ecosystem_counts=ecosystem_counts,
        )

    def _build_summary(
        self,
        target_type: str,
        identifier: str,
        analyses: List[RepositoryAnalysis],
        ecosystem_counts: Optional[Dict[str, int]] = None,
    ) -> ScanSummary:
        total = len(analyses)
        ai_assisted = 0
        agent_projects = 0
        tool_counts: Dict[str, int] = {}
        framework_counts: Dict[str, int] = {}
        category_counts: Dict[str, int] = {}

        for a in analyses:
            if a.detected_tools:
                ai_assisted += 1
                for t in a.detected_tools:
                    tool_counts[t.tool_name] = tool_counts.get(t.tool_name, 0) + 1

            if a.agent_detection.is_agent_project:
                agent_projects += 1
                for f in a.agent_detection.frameworks:
                    framework_counts[f] = framework_counts.get(f, 0) + 1
                for cat in a.agent_detection.categories:
                    cat_val = cat.value if hasattr(cat, "value") else str(cat)
                    category_counts[cat_val] = category_counts.get(cat_val, 0) + 1

        adoption_rate = round((ai_assisted / total * 100), 1) if total > 0 else 0.0

        return ScanSummary(
            target_type=target_type,
            target_identifier=identifier,
            total_repos_scanned=total,
            ai_assisted_repos_count=ai_assisted,
            agent_repos_count=agent_projects,
            ai_adoption_rate=adoption_rate,
            ecosystem_counts=ecosystem_counts or {},
            tool_counts=tool_counts,
            framework_counts=framework_counts,
            agent_category_counts=category_counts,
            repositories=analyses,
        )
