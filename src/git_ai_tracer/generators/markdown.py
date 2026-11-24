"""Markdown report generator for repository summaries and profile embedding."""

from pathlib import Path
from git_ai_tracer.models import ScanSummary


def render_progress_bar(percentage: float, width: int = 15) -> str:
    """Render a text progress bar."""
    filled = int(round((percentage / 100.0) * width))
    bar = "█" * filled + "░" * (width - filled)
    return f"`{bar}` {percentage:.1f}%"


def generate_markdown_report(summary: ScanSummary, output_file: str = "AI_METRICS.md") -> str:
    """Generate comprehensive markdown metrics document."""
    lines = []
    target = summary.target_identifier or "Ecosystem"
    lines.append(f"# 🤖 Git AI Tracer Report: `{target}`\n")
    lines.append(f"*Last updated: {summary.scan_timestamp} UTC*\n")

    # Badges row
    lines.append("## 📊 Overview Badges\n")
    if summary.ecosystem_counts:
        lines.append("[![Public AI Agents](badges/global_agents.svg)](AI_METRICS.md) ")
        lines.append("[![Claude Code Projects](badges/global_claude.svg)](AI_METRICS.md) ")
        lines.append("[![MCP Servers](badges/global_mcp.svg)](AI_METRICS.md) ")
    lines.append("[![AI Adoption](badges/adoption_rate.svg)](AI_METRICS.md) ")
    lines.append("[![AI Agents](badges/agent_status.svg)](AI_METRICS.md) ")
    lines.append("[![Top AI Tool](badges/ai_tools.svg)](AI_METRICS.md)\n")

    # Global Ecosystem Census Table (if present)
    if summary.ecosystem_counts:
        lines.append("## 🌐 Global GitHub Open-Source Census\n")
        lines.append("*Live count of publicly available repositories discovered across all of GitHub:*\n")
        lines.append("| Category / Technology | Total Public Repositories | Type |")
        lines.append("| :--- | :---: | :--- |")
        total_eco = sum(summary.ecosystem_counts.values()) or 1
        for label, count in sorted(summary.ecosystem_counts.items(), key=lambda x: x[1], reverse=True):
            category_tag = "AI Agent Ecosystem" if ("Agent" in label or "MCP" in label or "Crew" in label or "Lang" in label or "Auto" in label or "Eliza" in label) else "AI Coding Assistant"
            lines.append(f"| **{label}** | **{count:,}** | {category_tag} |")
        lines.append("")

    # Metrics Summary Table
    lines.append("### 📈 Tracked Sample Overview\n")
    lines.append("| Metric | Value | Description |")
    lines.append("| :--- | :--- | :--- |")
    lines.append(f"| **Total Repositories Scanned** | **{summary.total_repos_scanned}** | Public repositories evaluated |")
    lines.append(f"| **AI-Tool Assisted Repos** | **{summary.ai_assisted_repos_count}** | Repositories showing Claude Code, Cursor, Copilot, etc. |")
    lines.append(f"| **AI Agent Projects** | **{summary.agent_repos_count}** | Repositories built with agent frameworks / MCP |")
    lines.append(f"| **Overall AI Adoption Rate** | **{summary.ai_adoption_rate}%** | Percentage of active repos with AI footprints |\n")

    # AI Tool Breakdown Table
    lines.append("### 🛠️ AI Coding Tool Distribution\n")
    if summary.tool_counts:
        lines.append("| AI Tool | Detected Projects | Distribution |")
        lines.append("| :--- | :--- | :--- |")
        total_tool_occurrences = sum(summary.tool_counts.values()) or 1
        for tool, count in sorted(summary.tool_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_tool_occurrences) * 100
            bar = render_progress_bar(pct)
            lines.append(f"| **{tool}** | {count} | {bar} |")
    else:
        lines.append("*No AI coding tool signatures detected in current scan.*")
    lines.append("")

    # AI Agent Frameworks Breakdown Table
    lines.append("### 🧠 AI Agent Frameworks & Architectures\n")
    if summary.framework_counts or summary.agent_category_counts:
        lines.append("| Framework / Classification | Repositories | Type |")
        lines.append("| :--- | :--- | :--- |")
        if summary.framework_counts:
            for framework, count in sorted(summary.framework_counts.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| **{framework}** | {count} | Framework / Library |")
        if summary.agent_category_counts:
            for cat, count in sorted(summary.agent_category_counts.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"| **{cat}** | {count} | Architecture Category |")
    else:
        lines.append("*No AI agent frameworks detected in current scan.*")
    lines.append("")

    # Detailed Repository Table
    lines.append("### 📁 Detailed Repository Breakdown\n")
    lines.append("| Repository | AI Tools | Agent Frameworks | Stars | Language |")
    lines.append("| :--- | :--- | :--- | :---: | :--- |")

    for r in summary.repositories:
        tools_str = ", ".join(f"`{t.tool_name}`" for t in r.detected_tools) if r.detected_tools else "—"
        frameworks_str = ", ".join(f"`{f}`" for f in r.agent_detection.frameworks) if r.agent_detection.frameworks else ("Agentic" if r.agent_detection.is_agent_project else "—")
        lang = r.primary_language or "—"
        repo_link = f"[{r.name}]({r.html_url})"
        lines.append(f"| {repo_link} | {tools_str} | {frameworks_str} | {r.stars} | {lang} |")

    lines.append("\n---\n")
    lines.append("### 💡 Embed in Your GitHub Profile README\n")
    lines.append("Add the following markdown snippet to your personal profile `README.md` to display live AI stats:\n")
    lines.append("```markdown")
    lines.append("### 🤖 My AI & LLM Usage Footprint")
    lines.append(f"![AI Adoption](https://raw.githubusercontent.com/{target}/git_ai_tracer/main/badges/adoption_rate.svg)")
    lines.append(f"![AI Agents](https://raw.githubusercontent.com/{target}/git_ai_tracer/main/badges/agent_status.svg)")
    lines.append(f"![Top AI Tool](https://raw.githubusercontent.com/{target}/git_ai_tracer/main/badges/ai_tools.svg)")
    lines.append("```\n")

    content = "\n".join(lines)
    Path(output_file).write_text(content, encoding="utf-8")
    return content
