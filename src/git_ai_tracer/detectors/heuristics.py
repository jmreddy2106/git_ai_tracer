"""Orchestrator combining file, commit, dependency, and metadata analysis."""

from typing import Dict, List, Optional
from git_ai_tracer.detectors.agents import detect_agent_frameworks
from git_ai_tracer.detectors.tools import detect_tools
from git_ai_tracer.models import RepositoryAnalysis


def analyze_repository_artifacts(
    name: str,
    full_name: str,
    html_url: str,
    file_paths: List[str],
    manifest_contents: Optional[Dict[str, str]] = None,
    commit_messages: Optional[List[str]] = None,
    description: Optional[str] = None,
    topics: Optional[List[str]] = None,
    stars: int = 0,
    forks: int = 0,
    primary_language: Optional[str] = None,
    default_branch: str = "main",
    created_at: Optional[str] = None,
    pushed_at: Optional[str] = None,
) -> RepositoryAnalysis:
    """Run full heuristic analysis on a repository's artifacts."""
    # 1. Detect AI Coding Tools
    detected_tools = detect_tools(
        file_paths=file_paths,
        commit_messages=commit_messages,
    )

    # 2. Detect Agent Frameworks & Architectures
    agent_detection = detect_agent_frameworks(
        file_paths=file_paths,
        manifest_contents=manifest_contents,
        topics=topics,
        description=description,
        repo_name=name,
    )

    # 3. Determine if repository is AI-powered
    is_ai_powered = len(detected_tools) > 0 or agent_detection.is_agent_project

    return RepositoryAnalysis(
        name=name,
        full_name=full_name,
        html_url=html_url,
        description=description,
        default_branch=default_branch,
        stars=stars,
        forks=forks,
        primary_language=primary_language,
        topics=topics or [],
        created_at=created_at,
        pushed_at=pushed_at,
        is_ai_powered=is_ai_powered,
        detected_tools=detected_tools,
        agent_detection=agent_detection,
    )
