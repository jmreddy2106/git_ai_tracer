# 🛰️ Git AI Tracer

[![CI Tests](https://github.com/jmreddy2106/git_ai_tracer/actions/workflows/tracer_cron.yml/badge.svg)](https://github.com/jmreddy2106/git_ai_tracer/actions)
[![Public AI Agents](badges/global_agents.svg)](AI_METRICS.md)
[![Claude Code Projects](badges/global_claude.svg)](AI_METRICS.md)
[![MCP Servers](badges/global_mcp.svg)](AI_METRICS.md)
[![LangGraph Repos](badges/global_langgraph.svg)](AI_METRICS.md)

**Git AI Tracer** is an automated scanning, classification, and census engine that tracks the **global public GitHub ecosystem**:
1. **Public AI Coding Tool Adoption**: Censuses and tracks projects built with or assisted by **Claude Code** (128k+ repos), **Cursor**, **Aider**, **Cline / Roo Code**, **GitHub Copilot**, and **v0 / Bolt**.
2. **Public AI Agent Ecosystem**: Censuses repositories built *for* AI agents using multi-agent systems (**CrewAI**, **AutoGen**), workflow graphs (**LangGraph**), and protocol standards (**Model Context Protocol / MCP**, **ElizaOS**).
3. **Live Sync & Profile Tracking**: Runs automatically on a daily schedule via GitHub Actions, scanning public repositories across GitHub, updating metrics, generating dynamic SVG badges, and deploying an interactive dashboard to **GitHub Pages**.

---

## 🌟 Key Features

- 🔍 **Zero-Friction Heuristic Scanner**: Scans repository directory trees, config files, package manifests, and commit co-authorship in a single rate-limit-optimized GitHub API query.
- 🤖 **Comprehensive AI Detection Rules**:
  - **Claude Code**: `CLAUDE.md`, `.claude/`, `.claudeignore`, Anthropic co-authorship signatures.
  - **Cursor**: `.cursorrules`, `.cursor/rules/`, `.cursorignore`, Cursor agent commit signatures.
  - **Windsurf**: `.windsurfrules`, `.codeium/`, `.windsurf/`.
  - **Aider**: `.aider.conf.yml`, `.aider.chat.history.md`, conventional `aider:` commits.
  - **Cline / Roo Code**: `.clinerules`, `.roomodes`, `.roo/`, `.cline/`.
  - **GitHub Copilot**: `.github/copilot-instructions.md`, Copilot Workspace commit tags.
  - **Agent Frameworks**: LangGraph, CrewAI, AutoGen, ElizaOS, LlamaIndex, Model Context Protocol (MCP), Smolagents, DSPy, and Semantic Kernel.
- 📊 **Dynamic SVG Badges**: Generates pixel-perfect flat-square badges ready to embed into your personal GitHub profile README.
- 🌐 **Interactive GitHub Pages Dashboard**: Standalone dark-mode web application (`docs/index.html`) featuring search, filters, KPIs, and responsive tables.
- ⚡ **Local Directory Scanning**: Supports offline scanning of local folders and git repositories before pushing to GitHub.
- 🗄️ **Smart SQLite Caching**: Remembers scanned commit timestamps to avoid redundant API calls and prevent rate limiting.

---

## 🚀 Quickstart

### 1. Installation

Requires Python 3.10+:

```bash
# Clone the repository
git clone https://github.com/jmreddy2106/git_ai_tracer.git
cd git_ai_tracer

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### 2. Scan a GitHub Profile

Scan all public repositories of a user (e.g. `jmreddy2106`):

```bash
git-ai-tracer scan --user jmreddy2106
```

> **Tip**: If you have a GitHub token, pass `--token YOUR_TOKEN` or set `export GITHUB_TOKEN=...` to increase the GitHub API rate limit from 60 to 5,000 requests/hour.

### 3. Scan a Local Directory

Analyze any local project folder on your machine:

```bash
git-ai-tracer scan-local /path/to/my-project
```

### 4. Search Public GitHub Ecosystem

Discover and analyze repositories across GitHub by topic or keyword:

```bash
git-ai-tracer search --query "topic:ai-agent" --limit 50
```

### 5. Preview Web Dashboard

Launch the local dashboard server:

```bash
git-ai-tracer serve --port 8000
```
Open `http://localhost:8000` in your browser.

---

## 🤖 Tracking Live on Your GitHub Profile

### Step 1: Push This Repo to GitHub

```bash
git add .
git commit -m "feat: initial commit for Git AI Tracer"
git branch -M main
git remote add origin https://github.com/jmreddy2106/git_ai_tracer.git
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to your repository **Settings** → **Pages**.
2. Under **Build and deployment** → **Source**, select **GitHub Actions**.
3. The included workflow `.github/workflows/tracer_cron.yml` will automatically build and publish the dashboard every night at midnight UTC or whenever manually triggered.

### Step 3: Embed Badges in Your GitHub Profile README

Add this snippet to your personal profile `README.md` (`https://github.com/jmreddy2106/jmreddy2106/blob/main/README.md`):

```markdown
### 🌐 Global AI & LLM Ecosystem Tracker
[![Public AI Agents](https://raw.githubusercontent.com/jmreddy2106/git_ai_tracer/main/badges/global_agents.svg)](https://jmreddy2106.github.io/git_ai_tracer/)
[![Claude Code Projects](https://raw.githubusercontent.com/jmreddy2106/git_ai_tracer/main/badges/global_claude.svg)](https://jmreddy2106.github.io/git_ai_tracer/)
[![MCP Servers](https://raw.githubusercontent.com/jmreddy2106/git_ai_tracer/main/badges/global_mcp.svg)](https://jmreddy2106.github.io/git_ai_tracer/)
[![LangGraph Repos](https://raw.githubusercontent.com/jmreddy2106/git_ai_tracer/main/badges/global_langgraph.svg)](https://jmreddy2106.github.io/git_ai_tracer/)
```

---

## 🏗️ Project Architecture

```
git_ai_tracer/
├── .github/
│   └── workflows/
│       └── tracer_cron.yml     # Daily scheduled scan & auto-deploy to Pages
├── badges/                     # Generated SVG badges for profile README
│   ├── adoption_rate.svg
│   ├── agent_status.svg
│   └── ai_tools.svg
├── data/
│   ├── cache.db                # SQLite cache for GitHub API calls
│   └── metrics.json            # Machine-readable output dataset
├── docs/
│   └── index.html              # Interactive GitHub Pages dashboard
├── src/
│   └── git_ai_tracer/
│       ├── cli.py              # Typer CLI application
│       ├── models.py           # Pydantic data schemas
│       ├── detectors/
│       │   ├── tools.py        # Rules for Claude Code, Cursor, Copilot, etc.
│       │   ├── agents.py       # Detectors for LangGraph, CrewAI, MCP, etc.
│       │   └── heuristics.py   # Analysis orchestrator
│       ├── scanner/
│       │   ├── github_client.py# Rate-limited async GitHub API client
│       │   ├── local_scanner.py# Local directory scanner
│       │   └── cache.py        # SQLite caching layer
│       └── generators/
│           ├── badge.py        # SVG badge generator
│           ├── markdown.py     # AI_METRICS.md generator
│           └── dashboard.py    # GitHub Pages web app generator
└── tests/                      # Pytest test suite
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 📄 License

MIT License. Feel free to use and adapt this for your own GitHub profile and research projects!
