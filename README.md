# Assignment 4: A2A Multi-Agent Customer Support System

**UCLA Extension - Agentic AI Course**

---

## Overview

| Part | Focus | Points |
|------|-------|--------|
| **Part 1** | MCP Tools + Customer Data Agent | 40 |
| **Part 2** | Multi-Agent A2A System | 40 |
| **Part 3** | Code Quality | 20 |
| **Bonus** | Advanced Routing Patterns | +25 |

Build a **multi-agent customer support system** using Google ADK and the **A2A (Agent-to-Agent) protocol**. Your system will have three agents coordinating via A2A to handle customer queries.

## Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Host Agent (Port 10022)     │  ← SequentialAgent Orchestrator
│  Coordinates sub-agents      │
└──────┬──────────────┬────────┘
       │  A2A         │  A2A
       ▼              ▼
┌──────────────┐  ┌──────────────────┐
│ Customer Data│  │  Support Agent   │
│ Agent (10020)│  │   (Port 10021)   │
│ + McpToolset │  │  + McpToolset    │
│  (all tools) │  │  (filtered)      │
└──────┬───────┘  └──────┬───────────┘
       │    SSE          │  SSE
       └────────┬────────┘
                ▼
       ┌─────────────────┐
       │  MCP Server     │
       │  (Port 8080)    │
       │  15 DB Tools    │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │  SQLite DB      │
       │  support.db     │
       └─────────────────┘
```

---

# Part 1: McpToolset Configuration + Customer Data Agent (40 points)

## What's Provided

- **MCP Server** (`mcp_server/`) - Fully functional MCP server (FastMCP + SSE transport) with 15 tools for customer/ticket CRUD
- **Database** (`database/`) - SQLite setup with 15 customers and 25 tickets
- **McpToolset scaffold** (`agents/shared/mcp_toolset.py`) - Factory functions to configure ADK McpToolset with tool_filter
- **Config** (`agents/shared/agents_config.py`) - Ports, URLs, model settings

## How McpToolset Works

Google ADK's `McpToolset` connects to an MCP server via SSE, **auto-discovers all tools**, and makes them available to ADK agents. No manual wrapper functions needed — just configure which tools each agent should access using `tool_filter`:

```python
from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams

# All tools (no filter)
toolset = McpToolset(
    connection_params=SseConnectionParams(url="http://localhost:8080/sse"),
)

# Filtered tools (agent only sees these)
toolset = McpToolset(
    connection_params=SseConnectionParams(url="http://localhost:8080/sse"),
    tool_filter=["get_customer", "list_customers", "get_ticket"],
)
```

## What You Implement

### 1. McpToolset Configuration (15 pts)

File: `agents/shared/mcp_toolset.py`

Configure **two toolset factory functions** that return `McpToolset` instances with appropriate `tool_filter` lists:

| Toolset Factory | Purpose | Tools to Include |
|----------------|---------|-----------------|
| `create_customer_data_toolset()` | Broad data access for customer data agent | All 15 tools (full access) |
| `create_support_toolset()` | Support-safe tools only | Exclude admin ops: `disable_customer`, `activate_customer`, `delete_ticket`, `add_customer`, `update_customer` |

**Requirements:**
- Each factory returns an `McpToolset` instance
- Use `SseConnectionParams(url=MCP_SSE_URL)` for the connection
- `tool_filter` lists contain valid MCP tool names
- Support toolset excludes destructive/admin tools

### 2. Customer Data Agent (10 pts)

File: `agents/customer_data_agent/agent.py`

Create an ADK `Agent` with:
- Gemini model from config
- System instruction describing capabilities (>100 chars)
- `tools=[create_customer_data_toolset()]`

### 3. Agent Instruction Quality (10 pts)

- Agent instruction should describe the agent's role and available capabilities
- Instruction should guide the LLM on how to use the auto-discovered tools
- Clear, detailed instructions improve agent performance

### 4. Error Handling (5 pts)

- McpToolset handles MCP errors automatically
- Agent instruction should guide graceful error communication to users

---

# Part 2: Multi-Agent A2A System (40 points)

## What You Implement

### 1. Support Agent (10 pts)

File: `agents/support_agent/agent.py`

Create an ADK `Agent` with:
- A knowledge-base system instruction
- `tools=[create_support_toolset()]` for data-driven support (filtered to exclude admin ops)
- Troubleshooting guidance for: login issues, password resets, billing problems, performance issues
- Empathetic, solution-oriented tone

### 2. Host Agent - Orchestrator (10 pts)

File: `agents/host_agent/agent.py`

Create a `SequentialAgent` that:
- Uses `RemoteA2aAgent` to connect to Customer Data Agent and Support Agent
- References agent cards via well-known URL path
- Orchestrates the workflow: data lookup → support guidance

### 3. Agent Cards (10 pts)

File: `agents/create_agents.py`

Define `AgentCard` for each agent:
- `create_customer_data_agent_card()` - with data management skills
- `create_support_agent_card()` - with troubleshooting skills
- `create_host_agent_card()` - with orchestration skills
- Each card must have: name, url, description, skills with examples
- `AgentCard` also requires `version`, `capabilities`, `default_input_modes` and `default_output_modes` (omitting them raises a pydantic ValidationError); see the docstrings in `create_agents.py`

### 4. A2A Integration (10 pts)

- Host agent must use `RemoteA2aAgent` (not direct function calls)
- Agent cards must use correct URLs from config
- Proper imports from `a2a.types` and `google.adk.agents`

## Key Classes

```python
from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
```

---

# Part 3: Code Quality (20 points)

| Component | Points |
|-----------|--------|
| Docstrings on all public functions | 5 |
| Agent instruction quality and depth | 5 |
| Error handling patterns across codebase | 5 |
| Code organization and proper imports | 5 |

---

## Bonus: Advanced Routing Patterns (+25 points)

### Advanced Router (15 pts)

File: `agents/host_agent/advanced_router_agent.py`

Implement dynamic routing with:
- Query analysis to determine which agents to call
- Conditional execution (skip agents when not needed)
- Callback functions for routing decisions

### Parallel Router (10 pts)

File: `agents/host_agent/parallel_router_agent.py`

Implement parallel execution with:
- `ParallelAgent` to run both sub-agents simultaneously
- Response synthesis agent to combine results
- Output stored in agent state via an `after_agent_callback` on each `RemoteA2aAgent` (`RemoteA2aAgent` has no `output_key` field)

Switch modes via `HOST_AGENT_MODE` in `.env` (applies to `adk web host_agent`; `python run_agents.py` always serves the basic `host_agent/agent.py` on port 10022):
```bash
HOST_AGENT_MODE=basic      # Sequential (default)
HOST_AGENT_MODE=advanced   # Dynamic routing (bonus)
HOST_AGENT_MODE=parallel   # Parallel execution (bonus)
```

---

## Evaluation Rubric

### Part 1: McpToolset + Data Agent (40 pts)

| Component | Points |
|-----------|--------|
| McpToolset configuration (2 toolsets) | 15 |
| Customer data agent instruction | 10 |
| McpToolset integration with agent | 10 |
| Error handling and instruction quality | 5 |

### Part 2: Multi-Agent A2A (40 pts)

| Component | Points |
|-----------|--------|
| Support agent implementation | 10 |
| Host agent (SequentialAgent) | 10 |
| AgentCard definitions (3 agents) | 10 |
| A2A integration (RemoteA2aAgent) | 10 |

### Part 3: Code Quality (20 pts)

| Component | Points |
|-----------|--------|
| Docstrings and documentation | 5 |
| Agent instructions quality | 5 |
| Error handling patterns | 5 |
| Code organization | 5 |

### Bonus: Advanced Routing (+25 pts)

| Component | Points |
|-----------|--------|
| Advanced router with conditional execution | 15 |
| Parallel agent implementation | 10 |

---

## Getting Started

### 1. Environment Setup

```bash
conda create -n a2a-agents python=3.11 -y
conda activate a2a-agents

# Install all dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 2. Setup Database

```bash
cd database
python database_setup.py
# Choose 'y' for sample data (15 customers, 25 tickets)
cd ..
```

### 3. Start MCP Server

```bash
cd mcp_server
pip install -r requirements.txt
python app.py
# Server runs on http://localhost:8080 and blocks this terminal.
# Leave it running and open a new terminal (at the repo root) for step 4.
```

### 4. Start Agent System

```bash
# Install agent dependencies
pip install -r agents/requirements.txt

# Start all agents
python run_agents.py --mode start
# Agents on ports 10020, 10021, 10022

# Or run test scenarios
python test_scenarios.py
```

### 5. Verify Your Implementation

```bash
# Part 1: McpToolset configuration
python -m tests.test_mcp_toolset

# Part 2: Agent structure
python -m tests.test_agents

# Part 3: A2A integration
python -m tests.test_a2a
```

---

## Testing with ADK Web UI

```bash
cd agents
# Run one at a time: each command serves the web UI on port 8000 and blocks the terminal
adk web customer_data_agent
adk web support_agent
adk web host_agent
```

### Test Queries

**Customer Data Agent:**
- "Get customer 5's information"
- "List all active customers"
- "Show open high-priority tickets"
- "Create a ticket for customer 1 about login issues"

**Support Agent:**
- "I can't login to my account"
- "How do I reset my password?"
- "My payment failed, what should I do?"

**Host Agent (orchestrated):**
- "I'm having login issues, can you check my account and help?"
- "Show my open tickets and help resolve them"
- "Check account 5 and create a ticket for billing issues"

---

## Submission

This assignment uses **GitHub Classroom**. Your work is submitted by pushing to your repository's `main` branch.

### Steps

1. Verify all three agents work with `adk web`
2. Run test scenarios: `python test_scenarios.py`
3. Run the verification tests:
   ```bash
   python -m tests.test_mcp_toolset
   python -m tests.test_agents
   python -m tests.test_a2a
   ```
4. Complete `docs/reflection_template.md`
5. Commit and push your changes:
   ```bash
   git add -A
   git commit -m "Submit assignment 4"
   git push origin main
   ```
6. Verify your submission on GitHub — go to your repository page and confirm all files are present

### How Grading Works

- Your score and feedback are posted in Canvas. Nothing creates a Pull Request on your repository, so you will not find results in the **Pull Requests** tab
- You can push multiple times before the deadline

### Important

- **Do NOT commit sensitive files** — `.env`, `database/support.db`, and `__pycache__/` are already in `.gitignore`
- Make sure your code passes the local tests before pushing

---

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [A2A Protocol Specification](https://github.com/google/a2a)
- [A2A SDK (Python)](https://pypi.org/project/a2a-sdk/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Gemini API](https://ai.google.dev/)
