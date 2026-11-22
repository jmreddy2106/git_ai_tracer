"""SQLite caching layer for repository scans to minimize GitHub API calls."""

import json
import sqlite3
from pathlib import Path
from typing import Optional
from git_ai_tracer.models import RepositoryAnalysis


class ScanCache:
    def __init__(self, db_path: str = "data/cache.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS repo_cache (
                    full_name TEXT PRIMARY KEY,
                    pushed_at TEXT,
                    analysis_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def get(self, full_name: str, pushed_at: Optional[str]) -> Optional[RepositoryAnalysis]:
        """Return cached analysis if repository has not changed since last scan."""
        if not pushed_at:
            return None
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT pushed_at, analysis_json FROM repo_cache WHERE full_name = ?",
                (full_name,),
            )
            row = cursor.fetchone()
            if row:
                cached_pushed_at, analysis_json = row
                if cached_pushed_at == pushed_at:
                    try:
                        data = json.loads(analysis_json)
                        return RepositoryAnalysis(**data)
                    except Exception:
                        return None
        return None

    def set(self, analysis: RepositoryAnalysis):
        """Save analysis to SQLite cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO repo_cache (full_name, pushed_at, analysis_json, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (analysis.full_name, analysis.pushed_at, analysis.model_dump_json()),
            )
            conn.commit()
