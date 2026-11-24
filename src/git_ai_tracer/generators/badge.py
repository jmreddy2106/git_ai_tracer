"""Dynamic SVG badge generator for GitHub profile READMEs."""

from pathlib import Path
from git_ai_tracer.models import ScanSummary


def render_svg_badge(label: str, value: str, color_a: str = "#24292e", color_b: str = "#2ea44f") -> str:
    """Render a clean flat-square SVG badge."""
    font_family = "Verdana,DejaVu Sans,sans-serif"
    label_len = len(label) * 7 + 14
    value_len = len(value) * 7 + 14
    total_width = label_len + value_len

    label_x = label_len / 2
    value_x = label_len + (value_len / 2)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_len}" height="20" fill="{color_a}"/>
    <rect x="{label_len}" width="{value_len}" height="20" fill="{color_b}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="{font_family}" text-rendering="geometricPrecision" font-size="110">
    <text aria-hidden="true" x="{label_x * 10}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(label_len - 14) * 10}">{label}</text>
    <text x="{label_x * 10}" y="140" transform="scale(.1)" fill="#fff" textLength="{(label_len - 14) * 10}">{label}</text>
    <text aria-hidden="true" x="{value_x * 10}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{(value_len - 14) * 10}">{value}</text>
    <text x="{value_x * 10}" y="140" transform="scale(.1)" fill="#fff" textLength="{(value_len - 14) * 10}">{value}</text>
  </g>
</svg>"""


def format_compact_number(n: int) -> str:
    """Format large numbers into clean badge strings like 48.9k+."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M+"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}k+"
    return str(n)


def generate_all_badges(summary: ScanSummary, output_dir: str = "badges"):
    """Generate and save SVG badges based on scan summary."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Adoption Rate Badge
    adoption_val = f"{summary.ai_adoption_rate}%"
    color = "#2ea44f" if summary.ai_adoption_rate >= 50 else "#0969da" if summary.ai_adoption_rate >= 20 else "#8c959f"
    svg_adoption = render_svg_badge("AI Adoption", adoption_val, "#1f2428", color)
    (out_path / "adoption_rate.svg").write_text(svg_adoption, encoding="utf-8")

    # 2. Agent Projects Badge
    agent_val = f"{summary.agent_repos_count} repos"
    svg_agents = render_svg_badge("AI Agents", agent_val, "#1f2428", "#8250df")
    (out_path / "agent_status.svg").write_text(svg_agents, encoding="utf-8")

    # 3. Top AI Tool Badge
    top_tool = "None"
    if summary.tool_counts:
        top_tool = max(summary.tool_counts.items(), key=lambda x: x[1])[0]
    svg_tools = render_svg_badge("Top AI Tool", top_tool, "#1f2428", "#d97706")
    (out_path / "ai_tools.svg").write_text(svg_tools, encoding="utf-8")

    # 4. Total AI Assisted Repos Badge
    ai_repos_val = f"{summary.ai_assisted_repos_count} / {summary.total_repos_scanned}"
    svg_assisted = render_svg_badge("AI-Assisted Repos", ai_repos_val, "#1f2428", "#0284c7")
    (out_path / "ai_assisted.svg").write_text(svg_assisted, encoding="utf-8")

    # 5. Global Public Ecosystem Badges
    eco = summary.ecosystem_counts
    if eco:
        claude_count = eco.get("Claude Code", 0)
        agents_count = eco.get("Autonomous AI Agents", 0)
        mcp_count = eco.get("Model Context Protocol (MCP)", 0)
        langgraph_count = eco.get("LangGraph Workflows", 0)

        if claude_count > 0:
            svg_c = render_svg_badge("Claude Code Projects", format_compact_number(claude_count), "#1f2428", "#d97706")
            (out_path / "global_claude.svg").write_text(svg_c, encoding="utf-8")

        if agents_count > 0:
            svg_a = render_svg_badge("Public AI Agents", format_compact_number(agents_count), "#1f2428", "#8250df")
            (out_path / "global_agents.svg").write_text(svg_a, encoding="utf-8")

        if mcp_count > 0:
            svg_m = render_svg_badge("MCP Servers", format_compact_number(mcp_count), "#1f2428", "#2ea44f")
            (out_path / "global_mcp.svg").write_text(svg_m, encoding="utf-8")

        if langgraph_count > 0:
            svg_l = render_svg_badge("LangGraph Repos", format_compact_number(langgraph_count), "#1f2428", "#0969da")
            (out_path / "global_langgraph.svg").write_text(svg_l, encoding="utf-8")
