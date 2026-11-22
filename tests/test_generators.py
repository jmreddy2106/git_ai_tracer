"""Tests for badge, markdown, and dashboard generators."""

from pathlib import Path
import tempfile
from git_ai_tracer.generators.badge import generate_all_badges, render_svg_badge
from git_ai_tracer.generators.dashboard import generate_dashboard_html
from git_ai_tracer.generators.markdown import generate_markdown_report
from git_ai_tracer.models import RepositoryAnalysis, ScanSummary, ToolDetection, ToolCategory, AgentDetection


def create_sample_summary() -> ScanSummary:
    repo = RepositoryAnalysis(
        name="ai-agent-service",
        full_name="jmreddy2106/ai-agent-service",
        html_url="https://github.com/jmreddy2106/ai-agent-service",
        description="Autonomous customer service agent using LangGraph",
        stars=15,
        forks=2,
        primary_language="Python",
        is_ai_powered=True,
        detected_tools=[
            ToolDetection(tool_name="Claude Code", category=ToolCategory.CODING_ASSISTANT, confidence=0.98),
            ToolDetection(tool_name="Cursor", category=ToolCategory.CODING_ASSISTANT, confidence=0.95),
        ],
        agent_detection=AgentDetection(
            is_agent_project=True,
            frameworks=["LangGraph", "CrewAI"],
            confidence=0.95,
        ),
    )

    return ScanSummary(
        target_type="user",
        target_identifier="jmreddy2106",
        total_repos_scanned=10,
        ai_assisted_repos_count=6,
        agent_repos_count=4,
        ai_adoption_rate=60.0,
        tool_counts={"Claude Code": 4, "Cursor": 3, "GitHub Copilot": 1},
        framework_counts={"LangGraph": 3, "CrewAI": 2},
        repositories=[repo],
    )


def test_svg_badge_rendering():
    svg = render_svg_badge("AI Adoption", "60.0%", "#1f2428", "#2ea44f")
    assert "<svg" in svg
    assert "AI Adoption" in svg
    assert "60.0%" in svg


def test_generate_all_badges():
    summary = create_sample_summary()
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_all_badges(summary, output_dir=tmpdir)
        badge_files = [p.name for p in Path(tmpdir).glob("*.svg")]
        assert "adoption_rate.svg" in badge_files
        assert "agent_status.svg" in badge_files
        assert "ai_tools.svg" in badge_files
        assert "ai_assisted.svg" in badge_files


def test_generate_markdown_report():
    summary = create_sample_summary()
    with tempfile.TemporaryDirectory() as tmpdir:
        report_file = Path(tmpdir) / "REPORT.md"
        content = generate_markdown_report(summary, output_file=str(report_file))
        assert "# 🤖 Git AI Tracer Report" in content
        assert "60.0%" in content
        assert "Claude Code" in content
        assert "LangGraph" in content
        assert report_file.exists()


def test_generate_dashboard_html():
    summary = create_sample_summary()
    with tempfile.TemporaryDirectory() as tmpdir:
        html_file = Path(tmpdir) / "index.html"
        html = generate_dashboard_html(summary, output_path=str(html_file))
        assert "<!DOCTYPE html>" in html
        assert "Git AI Tracer Dashboard" in html
        assert "jmreddy2106" in html
        assert "ai-agent-service" in html
        assert html_file.exists()
