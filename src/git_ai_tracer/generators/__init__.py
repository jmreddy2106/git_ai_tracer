"""Generators for badges, markdown reports, and web dashboards."""

from git_ai_tracer.generators.badge import generate_all_badges
from git_ai_tracer.generators.dashboard import generate_dashboard_html
from git_ai_tracer.generators.markdown import generate_markdown_report

__all__ = ["generate_all_badges", "generate_dashboard_html", "generate_markdown_report"]
