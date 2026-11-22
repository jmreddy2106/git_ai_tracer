"""Tests for AI tool and AI agent detection engines."""

from git_ai_tracer.detectors.agents import detect_agent_frameworks, parse_python_requirements, parse_package_json
from git_ai_tracer.detectors.heuristics import analyze_repository_artifacts
from git_ai_tracer.detectors.tools import detect_tools
from git_ai_tracer.models import AgentCategory


def test_detect_claude_code():
    paths = ["src/main.py", "CLAUDE.md", "README.md"]
    tools = detect_tools(paths)
    assert any(t.tool_name == "Claude Code" for t in tools)
    claude = next(t for t in tools if t.tool_name == "Claude Code")
    assert claude.confidence >= 0.95


def test_detect_cursor_and_aider():
    paths = [".cursorrules", ".cursor/rules/python.mdc", ".aider.conf.yml"]
    commits = ["aider: implement user authentication", "fix: minor bug"]
    tools = detect_tools(paths, commit_messages=commits)
    
    tool_names = [t.tool_name for t in tools]
    assert "Cursor" in tool_names
    assert "Aider" in tool_names


def test_detect_cline_and_copilot():
    paths = [".clinerules", ".github/copilot-instructions.md"]
    commits = ["Co-authored-by: Copilot <copilot@github.com>"]
    tools = detect_tools(paths, commit_messages=commits)
    
    tool_names = [t.tool_name for t in tools]
    assert "Cline / Roo Code" in tool_names
    assert "GitHub Copilot" in tool_names


def test_parse_python_requirements():
    req = """
    # Comments
    langgraph>=0.2.0
    crewai==0.30.0
    pydantic~=2.7
    fastapi
    """
    pkgs = parse_python_requirements(req)
    assert "langgraph" in pkgs
    assert "crewai" in pkgs
    assert "fastapi" in pkgs


def test_parse_package_json():
    pkg_json = """{
        "dependencies": {
            "@elizaos/core": "^0.1.0",
            "@modelcontextprotocol/sdk": "^1.0.0"
        }
    }"""
    pkgs = parse_package_json(pkg_json)
    assert "@elizaos/core" in pkgs
    assert "@modelcontextprotocol/sdk" in pkgs


def test_detect_multi_agent_system():
    manifests = {
        "requirements.txt": "crewai>=0.28\nautogen>=0.2"
    }
    detection = detect_agent_frameworks(
        file_paths=["requirements.txt"],
        manifest_contents=manifests,
        topics=["ai-agent", "autonomous-agents"],
    )
    assert detection.is_agent_project
    assert "CrewAI" in detection.frameworks
    assert "AutoGen" in detection.frameworks
    assert AgentCategory.MULTI_AGENT in detection.categories


def test_detect_mcp_server():
    manifests = {
        "package.json": '{"dependencies": {"@modelcontextprotocol/sdk": "latest"}}'
    }
    detection = detect_agent_frameworks(
        file_paths=["src/index.ts", "package.json", "smithery.yaml"],
        manifest_contents=manifests,
        topics=["mcp-server"],
    )
    assert detection.is_agent_project
    assert "Model Context Protocol (MCP)" in detection.frameworks
    assert AgentCategory.MCP_PROTOCOL in detection.categories


def test_full_repository_artifact_analysis():
    analysis = analyze_repository_artifacts(
        name="my-agent-hub",
        full_name="user/my-agent-hub",
        html_url="https://github.com/user/my-agent-hub",
        file_paths=["CLAUDE.md", ".cursorrules", "requirements.txt"],
        manifest_contents={"requirements.txt": "langgraph\nlangchain"},
        commit_messages=["Co-authored-by: Claude <noreply@anthropic.com>"],
        description="A collaborative multi-agent workflow system",
        topics=["ai-agents", "langgraph"],
        stars=42,
    )

    assert analysis.is_ai_powered
    assert any(t.tool_name == "Claude Code" for t in analysis.detected_tools)
    assert any(t.tool_name == "Cursor" for t in analysis.detected_tools)
    assert analysis.agent_detection.is_agent_project
    assert "LangGraph" in analysis.agent_detection.frameworks
