"""Command-line interface for Git AI Tracer."""

import asyncio
import http.server
import json
import os
import socketserver
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from git_ai_tracer.generators.badge import generate_all_badges
from git_ai_tracer.generators.dashboard import generate_dashboard_html
from git_ai_tracer.generators.markdown import generate_markdown_report
from git_ai_tracer.models import ScanSummary
from git_ai_tracer.scanner.github_client import GitHubClient
from git_ai_tracer.scanner.local_scanner import scan_local_repository

app = typer.Typer(
    name="git-ai-tracer",
    help="🛰️ Git AI Tracer: Track AI Coding Tools & AI Agent Frameworks across GitHub.",
    add_completion=False,
)
console = Console()


def _save_and_generate_artifacts(summary: ScanSummary, json_path: str = "data/metrics.json"):
    """Persist metrics and generate badges, markdown, and dashboard."""
    p = Path(json_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(summary.model_dump_json(indent=2), encoding="utf-8")

    # Generate badges
    generate_all_badges(summary, output_dir="badges")

    # Generate Markdown report
    generate_markdown_report(summary, output_file="AI_METRICS.md")

    # Generate HTML Dashboard
    generate_dashboard_html(summary, output_path="docs/index.html")

    console.print(f"[bold green]✓[/bold green] Saved dataset to [cyan]{json_path}[/cyan]")
    console.print("[bold green]✓[/bold green] Generated SVG badges in [cyan]badges/[/cyan]")
    console.print("[bold green]✓[/bold green] Generated Markdown report at [cyan]AI_METRICS.md[/cyan]")
    console.print("[bold green]✓[/bold green] Generated Web Dashboard at [cyan]docs/index.html[/cyan]")


def _display_summary_table(summary: ScanSummary):
    """Render a clean summary table in the terminal."""
    if summary.ecosystem_counts:
        eco_table = Table(title="🌐 Global GitHub Public Repository Census", show_header=True)
        eco_table.add_column("Category / Technology", style="cyan")
        eco_table.add_column("Total Public Repos on GitHub", style="bold green")
        for k, v in sorted(summary.ecosystem_counts.items(), key=lambda x: x[1], reverse=True):
            eco_table.add_row(k, f"{v:,}")
        console.print(eco_table)

    table = Table(title=f"🛰️ AI Tracer Indexed Repositories — {summary.target_identifier}", show_header=True)
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="bold magenta")

    table.add_row("Tracked Public Repositories", str(summary.total_repos_scanned))
    table.add_row("AI-Tool Assisted Repos", f"{summary.ai_assisted_repos_count} ({summary.ai_adoption_rate}%)")
    table.add_row("AI Agent Repos", str(summary.agent_repos_count))

    if summary.tool_counts:
        top_tools = ", ".join(f"{k} ({v})" for k, v in sorted(summary.tool_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        table.add_row("Top AI Tools Detected", top_tools)

    if summary.framework_counts:
        top_frameworks = ", ".join(f"{k} ({v})" for k, v in sorted(summary.framework_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        table.add_row("Top Agent Frameworks", top_frameworks)

    console.print(table)


@app.command()
def scan(
    user: str = typer.Option(..., "--user", "-u", help="GitHub username to scan (e.g. jmreddy2106)"),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)"),
    limit: int = typer.Option(100, "--limit", "-l", help="Max repositories to scan"),
    output: str = typer.Option("data/metrics.json", "--output", "-o", help="Path to save output JSON metrics"),
    generate: bool = typer.Option(True, "--generate/--no-generate", help="Generate badges, markdown report, and web dashboard"),
):
    """Scan all public repositories for a specified GitHub user."""
    console.print(Panel(f"Scanning public repositories for GitHub user: [bold cyan]@{user}[/bold cyan]...", title="Git AI Tracer"))

    client = GitHubClient(token=token)

    with console.status("[bold green]Fetching and analyzing repositories..."):
        try:
            summary = asyncio.run(client.scan_user(user, limit=limit))
        except Exception as e:
            console.print(f"[bold red]Scan failed:[/bold red] {e}")
            raise typer.Exit(code=1)

    _display_summary_table(summary)

    if generate:
        _save_and_generate_artifacts(summary, json_path=output)


@app.command()
def search(
    query: str = typer.Option("topic:ai-agent", "--query", "-q", help="Search query on GitHub (e.g. topic:ai-agent, topic:claude-code)"),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="GitHub Personal Access Token"),
    limit: int = typer.Option(30, "--limit", "-l", help="Max repositories to scan"),
    output: str = typer.Option("data/metrics.json", "--output", "-o", help="Path to save output JSON metrics"),
    generate: bool = typer.Option(True, "--generate/--no-generate", help="Generate badges, markdown, and dashboard"),
):
    """Scan public GitHub repositories matching a search query or topic."""
    console.print(Panel(f"Searching and scanning GitHub for: [bold cyan]{query}[/bold cyan]...", title="Git AI Tracer"))

    client = GitHubClient(token=token)

    with console.status("[bold green]Searching and analyzing repositories..."):
        try:
            summary = asyncio.run(client.scan_search(query, limit=limit))
        except Exception as e:
            console.print(f"[bold red]Search failed:[/bold red] {e}")
            raise typer.Exit(code=1)

    _display_summary_table(summary)

    if generate:
        _save_and_generate_artifacts(summary, json_path=output)


@app.command(name="track-ecosystem")
def track_ecosystem(
    repos_per_topic: int = typer.Option(8, "--repos-per-topic", "-r", help="Number of public sample repos to deeply inspect per topic"),
    token: Optional[str] = typer.Option(None, "--token", "-t", help="GitHub Personal Access Token"),
    output: str = typer.Option("data/metrics.json", "--output", "-o", help="Path to save output JSON metrics"),
    generate: bool = typer.Option(True, "--generate/--no-generate", help="Generate badges, markdown report, and web dashboard"),
):
    """Scan and census publicly available repositories across all of GitHub for AI tools and AI agents."""
    console.print(Panel("Scanning global public GitHub ecosystem for AI tools & Agent frameworks...", title="Git AI Tracer Global Ecosystem Tracker"))

    client = GitHubClient(token=token)

    with console.status("[bold green]Conducting global public GitHub census and inspecting top projects..."):
        try:
            summary = asyncio.run(client.scan_ecosystem(repos_per_topic=repos_per_topic))
        except Exception as e:
            console.print(f"[bold red]Ecosystem scan failed:[/bold red] {e}")
            raise typer.Exit(code=1)

    _display_summary_table(summary)

    if generate:
        _save_and_generate_artifacts(summary, json_path=output)


@app.command(name="scan-local")
def scan_local(
    path: str = typer.Argument(".", help="Path to local directory or git repository"),
):
    """Scan a local directory on disk for AI coding tools and agent frameworks."""
    console.print(Panel(f"Scanning local directory: [bold cyan]{path}[/bold cyan]...", title="Git AI Tracer Local Scan"))

    try:
        analysis = scan_local_repository(path)
    except Exception as e:
        console.print(f"[bold red]Local scan failed:[/bold red] {e}")
        raise typer.Exit(code=1)

    # Display results
    table = Table(title=f"Analysis for {analysis.name}")
    table.add_column("Property", style="cyan")
    table.add_column("Details", style="magenta")

    tools_str = ", ".join(f"{t.tool_name} (conf: {t.confidence})" for t in analysis.detected_tools) if analysis.detected_tools else "None"
    table.add_row("Detected AI Tools", tools_str)

    agent_str = ", ".join(analysis.agent_detection.frameworks) if analysis.agent_detection.frameworks else ("Agentic" if analysis.agent_detection.is_agent_project else "None")
    table.add_row("Agent Frameworks", agent_str)

    table.add_row("AI Powered?", "[green]Yes[/green]" if analysis.is_ai_powered else "[yellow]No[/yellow]")

    console.print(table)


@app.command()
def report(
    input_file: str = typer.Option("data/metrics.json", "--input", "-i", help="Input metrics JSON path"),
):
    """Re-generate badges, markdown report, and HTML dashboard from existing metrics JSON."""
    p = Path(input_file)
    if not p.exists():
        console.print(f"[bold red]File not found:[/bold red] {input_file}")
        raise typer.Exit(code=1)

    data = json.loads(p.read_text(encoding="utf-8"))
    summary = ScanSummary(**data)
    _save_and_generate_artifacts(summary, json_path=input_file)


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="Port to serve dashboard on"),
    docs_dir: str = typer.Option("docs", "--docs-dir", "-d", help="Directory containing index.html"),
):
    """Start local web server to preview the dashboard."""
    docs_path = Path(docs_dir).resolve()
    if not (docs_path / "index.html").exists():
        console.print(f"[bold red]Error:[/bold red] {docs_path}/index.html does not exist. Run a scan first!")
        raise typer.Exit(code=1)

    os.chdir(docs_path)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        console.print(f"[bold green]Serving dashboard at:[/bold green] [bold cyan]http://localhost:{port}[/bold cyan]")
        console.print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\nServer stopped.")


if __name__ == "__main__":
    app()
