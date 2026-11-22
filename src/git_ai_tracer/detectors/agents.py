"""Detectors for AI agent frameworks, multi-agent systems, and MCP protocols."""

import json
import re
from typing import Dict, List, Optional, Set
from git_ai_tracer.models import AgentCategory, AgentDetection, Evidence, EvidenceType


class AgentFrameworkRule:
    def __init__(
        self,
        name: str,
        category: AgentCategory,
        python_pkgs: Optional[List[str]] = None,
        npm_pkgs: Optional[List[str]] = None,
        rust_crates: Optional[List[str]] = None,
        go_modules: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        confidence: float = 0.95,
    ):
        self.name = name
        self.category = category
        self.python_pkgs = [p.lower() for p in (python_pkgs or [])]
        self.npm_pkgs = [p.lower() for p in (npm_pkgs or [])]
        self.rust_crates = [p.lower() for p in (rust_crates or [])]
        self.go_modules = [p.lower() for p in (go_modules or [])]
        self.keywords = [k.lower() for k in (keywords or [])]
        self.confidence = confidence


FRAMEWORK_RULES: List[AgentFrameworkRule] = [
    # Multi-Agent Systems
    AgentFrameworkRule(
        name="CrewAI",
        category=AgentCategory.MULTI_AGENT,
        python_pkgs=["crewai", "crewai-tools"],
        keywords=["crewai"],
    ),
    AgentFrameworkRule(
        name="AutoGen",
        category=AgentCategory.MULTI_AGENT,
        python_pkgs=["autogen", "pyautogen", "autogen-agentchat", "autogen-ext"],
        keywords=["autogen", "pyautogen"],
    ),
    AgentFrameworkRule(
        name="MetaGPT",
        category=AgentCategory.MULTI_AGENT,
        python_pkgs=["metagpt"],
        keywords=["metagpt"],
    ),
    AgentFrameworkRule(
        name="OpenAI Swarm",
        category=AgentCategory.MULTI_AGENT,
        python_pkgs=["swarm", "openai-swarm"],
        keywords=["openai swarm", "swarm agent"],
    ),
    AgentFrameworkRule(
        name="ChatDev",
        category=AgentCategory.MULTI_AGENT,
        python_pkgs=["chatdev"],
        keywords=["chatdev"],
    ),

    # Workflow & Graph Agents
    AgentFrameworkRule(
        name="LangGraph",
        category=AgentCategory.WORKFLOW_GRAPH,
        python_pkgs=["langgraph", "langgraph-checkpoint"],
        npm_pkgs=["@langchain/langgraph"],
        keywords=["langgraph"],
    ),
    AgentFrameworkRule(
        name="Temporal / Llama Workflows",
        category=AgentCategory.WORKFLOW_GRAPH,
        python_pkgs=["llama-index-core", "llama-index"],
        npm_pkgs=["llamaindex"],
        keywords=["llama-agents", "agentic workflow"],
    ),

    # Protocol & Tool Interop: Model Context Protocol (MCP)
    AgentFrameworkRule(
        name="Model Context Protocol (MCP)",
        category=AgentCategory.MCP_PROTOCOL,
        python_pkgs=["mcp", "fastmcp"],
        npm_pkgs=["@modelcontextprotocol/sdk"],
        rust_crates=["mcp-server"],
        keywords=["mcp-server", "model-context-protocol", "smithery"],
    ),

    # Autonomous Dev & Coding Agents
    AgentFrameworkRule(
        name="Smolagents",
        category=AgentCategory.AUTONOMOUS_DEV,
        python_pkgs=["smolagents"],
        keywords=["smolagents", "huggingface agents"],
    ),
    AgentFrameworkRule(
        name="SWE-agent",
        category=AgentCategory.AUTONOMOUS_DEV,
        python_pkgs=["sweagent", "swe-agent"],
        keywords=["swe-agent", "swebench"],
    ),
    AgentFrameworkRule(
        name="OpenHands (OpenDevin)",
        category=AgentCategory.AUTONOMOUS_DEV,
        python_pkgs=["openhands", "opendevin"],
        keywords=["openhands", "opendevin"],
    ),

    # Social & Web3 Agents
    AgentFrameworkRule(
        name="ElizaOS",
        category=AgentCategory.SOCIAL_WEB3,
        npm_pkgs=["@elizaos/core", "@ai16z/eliza"],
        keywords=["elizaos", "ai16z", "eliza agent"],
    ),
    AgentFrameworkRule(
        name="Rig / Virtuals",
        category=AgentCategory.SOCIAL_WEB3,
        npm_pkgs=["@virtuals-protocol/game"],
        rust_crates=["rig-core"],
        keywords=["virtuals-protocol", "rig agent"],
    ),

    # General Agent / LLM Orchestration Frameworks
    AgentFrameworkRule(
        name="LangChain",
        category=AgentCategory.FRAMEWORK,
        python_pkgs=["langchain", "langchain-core", "langchain-community"],
        npm_pkgs=["@langchain/core", "langchain"],
        go_modules=["github.com/tmc/langchaingo"],
        rust_crates=["langchain-rust"],
        keywords=["langchain agent"],
    ),
    AgentFrameworkRule(
        name="DSPy",
        category=AgentCategory.FRAMEWORK,
        python_pkgs=["dspy-ai", "dspy"],
        keywords=["dspy-ai", "dspy agent"],
    ),
    AgentFrameworkRule(
        name="Semantic Kernel",
        category=AgentCategory.FRAMEWORK,
        python_pkgs=["semantic-kernel"],
        npm_pkgs=["@microsoft/semantic-kernel"],
        keywords=["semantic-kernel"],
    ),
]


def parse_python_requirements(content: str) -> Set[str]:
    """Extract package names from requirements.txt or pyproject.toml."""
    packages = set()
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Strip version specifiers (==, >=, <=, ~=, <, >)
        match = re.match(r"^([a-zA-Z0-9_\-\.]+)", line)
        if match:
            packages.add(match.group(1).lower())
    return packages


def parse_package_json(content: str) -> Set[str]:
    """Extract dependency names from package.json."""
    packages = set()
    try:
        data = json.loads(content)
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        if isinstance(deps, dict):
            packages.update(k.lower() for k in deps.keys())
        if isinstance(dev_deps, dict):
            packages.update(k.lower() for k in dev_deps.keys())
    except Exception:
        pass
    return packages


def parse_cargo_toml(content: str) -> Set[str]:
    """Extract dependency crate names from Cargo.toml."""
    crates = set()
    in_deps = False
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("[") and "dependencies" in line:
            in_deps = True
            continue
        elif line.startswith("["):
            in_deps = False
            continue
        if in_deps and "=" in line:
            name = line.split("=")[0].strip()
            crates.add(name.lower())
    return crates


def detect_agent_frameworks(
    file_paths: List[str],
    manifest_contents: Optional[Dict[str, str]] = None,
    topics: Optional[List[str]] = None,
    description: Optional[str] = None,
    repo_name: Optional[str] = None,
) -> AgentDetection:
    """Detect whether a repository is designed for or builds an AI Agent."""
    manifests = manifest_contents or {}
    all_topics = [t.lower() for t in (topics or [])]
    desc = (description or "").lower()
    name = (repo_name or "").lower()
    
    # Check for dedicated MCP markers in file paths
    file_evidence: List[Evidence] = []
    for p in file_paths:
        lower_p = p.lower()
        if "smithery.yaml" in lower_p or lower_p.endswith("mcp.json") or "/mcp/" in lower_p:
            file_evidence.append(
                Evidence(
                    type=EvidenceType.CONFIG,
                    match=p,
                    confidence=0.95,
                    details="MCP configuration detected in project files.",
                )
            )

    # Aggregate extracted packages
    py_packages: Set[str] = set()
    npm_packages: Set[str] = set()
    rust_crates: Set[str] = set()

    for filename, content in manifests.items():
        lower_fn = filename.lower()
        if "requirements" in lower_fn or lower_fn.endswith(".txt"):
            py_packages.update(parse_python_requirements(content))
        elif "pyproject.toml" in lower_fn or "setup.py" in lower_fn:
            py_packages.update(parse_python_requirements(content))
        elif "package.json" in lower_fn:
            npm_packages.update(parse_package_json(content))
        elif "cargo.toml" in lower_fn:
            rust_crates.update(parse_cargo_toml(content))

    detected_frameworks: List[str] = []
    detected_categories: Set[AgentCategory] = set()
    evidences: List[Evidence] = list(file_evidence)

    # Check against registered framework rules
    for rule in FRAMEWORK_RULES:
        matched = False
        # Python check
        for pkg in rule.python_pkgs:
            if pkg in py_packages:
                matched = True
                evidences.append(
                    Evidence(
                        type=EvidenceType.DEPENDENCY,
                        match=f"Python: {pkg}",
                        confidence=rule.confidence,
                        details=f"Dependency '{pkg}' belongs to {rule.name}",
                    )
                )
        # NPM check
        for pkg in rule.npm_pkgs:
            if pkg in npm_packages:
                matched = True
                evidences.append(
                    Evidence(
                        type=EvidenceType.DEPENDENCY,
                        match=f"NPM: {pkg}",
                        confidence=rule.confidence,
                        details=f"Dependency '{pkg}' belongs to {rule.name}",
                    )
                )
        # Rust check
        for crate in rule.rust_crates:
            if crate in rust_crates:
                matched = True
                evidences.append(
                    Evidence(
                        type=EvidenceType.DEPENDENCY,
                        match=f"Crate: {crate}",
                        confidence=rule.confidence,
                        details=f"Crate '{crate}' belongs to {rule.name}",
                    )
                )
        # Keyword / Topic check
        for kw in rule.keywords:
            if kw in all_topics:
                matched = True
                evidences.append(
                    Evidence(
                        type=EvidenceType.TOPIC,
                        match=f"Topic: {kw}",
                        confidence=0.90,
                        details=f"GitHub repository topic matches {rule.name}",
                    )
                )
            elif kw in desc and not matched:
                matched = True
                evidences.append(
                    Evidence(
                        type=EvidenceType.DESCRIPTION,
                        match=kw,
                        confidence=0.80,
                        details=f"Repository description references {rule.name}",
                    )
                )

        if matched:
            detected_frameworks.append(rule.name)
            detected_categories.add(rule.category)

    # Generic AI Agent Topic checks
    agent_topics = {"ai-agent", "ai-agents", "autonomous-agents", "autonomous-agent", "agentic-ai", "agentic-workflow", "mcp-server"}
    for t in all_topics:
        if t in agent_topics and not any(t in e.match for e in evidences):
            evidences.append(
                Evidence(
                    type=EvidenceType.TOPIC,
                    match=f"Topic: {t}",
                    confidence=0.92,
                    details=f"Explicit AI Agent GitHub topic: '{t}'",
                )
            )
            detected_categories.add(AgentCategory.FRAMEWORK)

    # Repository Name Heuristics (e.g. workspace-intelligence-agent)
    if re.search(r"(^|[-_])agent(s)?([-_]|$)", name):
        evidences.append(
            Evidence(
                type=EvidenceType.DESCRIPTION,
                match=f"Repo Name: {name}",
                confidence=0.85,
                details=f"Repository name contains agent designation: '{name}'",
            )
        )
        detected_categories.add(AgentCategory.FRAMEWORK)

    # Description Heuristics for agent keywords
    desc_agent_keywords = [
        ("multi-agent", AgentCategory.MULTI_AGENT),
        ("autonomous agent", AgentCategory.AUTONOMOUS_DEV),
        ("agent platform", AgentCategory.MULTI_AGENT),
        ("ai agent", AgentCategory.FRAMEWORK),
        ("agentic", AgentCategory.WORKFLOW_GRAPH),
        ("ai-powered agent", AgentCategory.FRAMEWORK),
    ]
    for kw, cat in desc_agent_keywords:
        if kw in desc:
            evidences.append(
                Evidence(
                    type=EvidenceType.DESCRIPTION,
                    match=f"Desc: {kw}",
                    confidence=0.88,
                    details=f"Description explicitly mentions '{kw}'",
                )
            )
            detected_categories.add(cat)

    is_agent = len(evidences) > 0
    overall_confidence = round(max((e.confidence for e in evidences), default=0.0), 2)

    return AgentDetection(
        is_agent_project=is_agent,
        confidence=overall_confidence,
        categories=sorted(list(detected_categories), key=lambda x: x.value),
        frameworks=sorted(list(set(detected_frameworks))),
        evidence=evidences,
    )
