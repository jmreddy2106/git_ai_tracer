"""Scanner for local directory or git repositories on disk."""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from git_ai_tracer.detectors.heuristics import analyze_repository_artifacts
from git_ai_tracer.models import RepositoryAnalysis


def get_git_commit_messages(repo_dir: Path, limit: int = 15) -> List[str]:
    """Retrieve recent commit messages from local git log."""
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_dir), "log", f"-n{limit}", "--pretty=%B%x1e"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            return [m.strip() for m in res.stdout.split("\x1e") if m.strip()]
    except Exception:
        pass
    return []


def scan_local_repository(repo_path: str) -> RepositoryAnalysis:
    """Analyze a local directory as a Git AI Tracer repository."""
    path = Path(repo_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Local path '{repo_path}' does not exist.")

    name = path.name
    full_name = f"local/{name}"

    file_paths: List[str] = []
    manifest_contents: Dict[str, str] = {}

    # Traverse directory (ignore .git, .venv, node_modules)
    ignored_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for f in files:
            full_file = Path(root) / f
            rel_file = str(full_file.relative_to(path))
            file_paths.append(rel_file)

            # Read manifests
            lower_name = f.lower()
            if lower_name in ["requirements.txt", "pyproject.toml", "package.json", "cargo.toml", "smithery.yaml"]:
                try:
                    with open(full_file, "r", encoding="utf-8", errors="ignore") as mf:
                        manifest_contents[rel_file] = mf.read()
                except Exception:
                    pass

    # Extract commit messages
    commits = get_git_commit_messages(path)

    return analyze_repository_artifacts(
        name=name,
        full_name=full_name,
        html_url=f"file://{path}",
        file_paths=file_paths,
        manifest_contents=manifest_contents,
        commit_messages=commits,
        description="Local repository scan",
        stars=0,
        forks=0,
        primary_language=None,
    )
