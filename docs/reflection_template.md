# Assignment 4: Reflection

## Student Name: _______________

---

## Part 1: MCP Tools + Customer Data Agent

### Toolset Design Decisions
- Which MCP tools did you include in each `tool_filter`, and why?
- How does the support toolset's filter limit what the support agent can do?

### Data Agent Instruction
- What capabilities did you include in the system instruction?
- How does the instruction guide the agent's tool selection?

---

## Part 2: Multi-Agent A2A System

### Support Agent Design
- What knowledge did you embed in the support agent's instruction?
- How does it combine its knowledge base with its filtered MCP toolset?

### Host Agent Orchestration
- How does the SequentialAgent coordinate between sub-agents?
- What happens when the Customer Data Agent returns data to the Support Agent?

### A2A Protocol Insights
- How does agent discovery work via AgentCards?
- What role does the `.well-known/agent-card.json` endpoint play?
- How does RemoteA2aAgent differ from direct function calls?

---

## Part 3: Challenges and Solutions

### Technical Challenges
- What was the most difficult part of the implementation?
- How did you debug agent communication issues?

### Architecture Decisions
- Why is the SequentialAgent pattern appropriate for this use case?
- What are the trade-offs vs. direct agent calls?

---

## Bonus: Routing Modes (if attempted)

### Advanced Router
- How does the dynamic routing decide which agents to call?
- What callback patterns did you use?

### Parallel Router
- How does parallel execution improve latency?
- What synthesis strategy did you use to combine results?

### Mode Comparison

Report measured wall-clock latency (seconds) for the same query in each mode, and how you measured it.

| Mode | Agents Called | Latency | Context Passing |
|------|-------------|---------|-----------------|
| Basic (Sequential) | | | |
| Advanced (Dynamic) | | | |
| Parallel | | | |

---

## Key Learnings
1.
2.
3.

## Ideas for Improvement
-
-
