"""Pydantic data models for Git AI Tracer."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    FILE = "file"
    CONFIG = "config"
    DEPENDENCY = "dependency"
    COMMIT = "commit"
    TOPIC = "topic"
    DESCRIPTION = "description"


class Evidence(BaseModel):
    type: EvidenceType
    match: str
    confidence: float = Field(ge=0.0, le=1.0)
    details: Optional[str] = None


class ToolCategory(str, Enum):
    CODING_ASSISTANT = "coding_assistant"
    AUTONOMOUS_DEV = "autonomous_dev"
    PROMPT_ENGINEERING = "prompt_engineering"
    APP_GENERATOR = "app_generator"


class ToolDetection(BaseModel):
    tool_name: str
    category: ToolCategory = ToolCategory.CODING_ASSISTANT
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[Evidence] = Field(default_factory=list)


class AgentCategory(str, Enum):
    MULTI_AGENT = "Multi-Agent System"
    WORKFLOW_GRAPH = "Workflow & Graph Agent"
    MCP_PROTOCOL = "Model Context Protocol (MCP)"
    AUTONOMOUS_DEV = "Autonomous Dev Agent"
    SOCIAL_WEB3 = "Social & Web3 Agent"
    FRAMEWORK = "General Agent Framework"


class AgentDetection(BaseModel):
    is_agent_project: bool = False
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    categories: List[AgentCategory] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)


class RepositoryAnalysis(BaseModel):
    name: str
    full_name: str
    html_url: str
    description: Optional[str] = None
    default_branch: str = "main"
    stars: int = 0
    forks: int = 0
    primary_language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    pushed_at: Optional[str] = None
    
    # AI Analysis Results
    is_ai_powered: bool = False
    detected_tools: List[ToolDetection] = Field(default_factory=list)
    agent_detection: AgentDetection = Field(default_factory=AgentDetection)
    
    # Metadata
    scan_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ScanSummary(BaseModel):
    target_type: str = "ecosystem"  # "ecosystem" or "user"
    target_identifier: str = "Public GitHub Ecosystem"
    scan_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_repos_scanned: int = 0
    ai_assisted_repos_count: int = 0
    agent_repos_count: int = 0
    ai_adoption_rate: float = 0.0  # percentage
    
    # Global GitHub Public Repository Census Counts
    ecosystem_counts: Dict[str, int] = Field(default_factory=dict)
    
    tool_counts: Dict[str, int] = Field(default_factory=dict)
    framework_counts: Dict[str, int] = Field(default_factory=dict)
    agent_category_counts: Dict[str, int] = Field(default_factory=dict)
    
    repositories: List[RepositoryAnalysis] = Field(default_factory=list)
