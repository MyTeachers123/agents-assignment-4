# Assignment 4: Reflection

## Student Name: Ying Chen

---

## Part 1: MCP Tools + Customer Data Agent

### Toolset Design Decisions
- **Customer data toolset:** all 15 MCP tools, listed explicitly in `tool_filter` (customer lookup/management, admin `disable_customer`/`activate_customer`, all ticket operations including `delete_ticket`, and stats/search). This agent is the trusted back-office role, so it gets full access.
- **Support toolset:** 10 tools — read-only customer lookup (`get_customer`, `list_customers`), ticket viewing/search, safe ticket changes (`create_ticket`, `update_ticket_status`, `update_ticket_priority`) and stats. The five admin/destructive tools (`add_customer`, `update_customer`, `disable_customer`, `activate_customer`, `delete_ticket`) are filtered out.
- Because McpToolset only exposes the filtered tools to the LLM, the support agent literally cannot call an admin tool even if a user tries to talk it into it (least privilege enforced in code, not just in the prompt).

### Data Agent Instruction
- The instruction lists every tool and what it is for, a step-by-step method (parse IDs/filters → pick the most specific tool → chain calls when needed → never invent data), rules for destructive actions, priority defaults for new tickets, explicit error handling ("not found", missing IDs, service unavailable) and a concise, ID-rich response format.
- Tool selection is guided by "prefer `get_*` for one record, `list_*` with filters for groups, `search_tickets` for free text", so the model picks the narrowest call.

---

## Part 2: Multi-Agent A2A System

### Support Agent Design
- The knowledge base covers login issues, password resets, payment/billing, performance, feature requests and data export, each with concrete steps and when to escalate.
- It combines this with the filtered toolset: look up the customer and existing tickets first (to personalize and avoid duplicates), then give KB steps, then create/update a ticket with a priority rule. If an admin action is requested, it explains the limit and opens a ticket instead.

### Host Agent Orchestration
- `SequentialAgent` runs `customer_data` then `support_specialist`, both `RemoteA2aAgent`s. Each runs in the same session, so the data agent's reply becomes part of the conversation context the support agent receives.
- The support agent can therefore reference real account status and ticket IDs instead of asking the user again.

### A2A Protocol Insights
- Each agent server publishes an AgentCard (name, URL, description, skills with examples, transport, capabilities). A client only needs the base URL; it fetches the card and knows how to talk to the agent.
- `/.well-known/agent-card.json` (`AGENT_CARD_WELL_KNOWN_PATH`) is the standard discovery endpoint, so no manual configuration of endpoints or schemas is needed.
- `RemoteA2aAgent` sends a task over HTTP/JSON-RPC to an independent server (its own process, model, tools and lifecycle) and tracks task state, instead of calling a Python function in the same process. Agents can be deployed, scaled and replaced independently, even on different frameworks.

---

## Part 3: Challenges and Solutions

### Technical Challenges
- Running three layers (MCP server, three A2A agent servers, client/tests) at the same time and keeping ports 8080/10020–10022 straight.
- On Windows, local asyncio servers hung because the firewall blocked loopback traffic; adding an inbound loopback allow rule fixed it.

### Architecture Decisions
- Sequential fits customer support because guidance depends on the data (account status, existing tickets); data must come first.
- Trade-off vs. direct calls: A2A adds network hops and latency, but gives loose coupling, independent deployment, discovery via cards and a standard protocol across frameworks.

---

## Bonus: Routing Modes

### Advanced Router
- `analyze_query_intent` uses whole-word keyword rules to set `needs_data`, `needs_support`, `urgency` and `execution_mode` (`sequential`, `data_only`, `support_only`; unclear queries default to both).
- A `before_agent_callback` on the router stores `routing_decision` in session state (writable `CallbackContext`). `before_agent_callback`s on each `RemoteA2aAgent` return a `Content` to skip the agent or `None` to run it. The router's instruction is a dynamic provider that reads the decision.

### Parallel Router
- `ParallelAgent` runs both remote agents at once, so latency ≈ the slower agent instead of the sum of both.
- Each `RemoteA2aAgent` has an `after_agent_callback` writing its final reply to its own state key (`customer_data_output`, `support_specialist_output`) — separate keys avoid race conditions. A summary agent (`include_contents='none'`) reads both from state and merges them into one reply.
- Limitation: in parallel mode the support agent cannot see the data agent's result, so it looks the customer up itself.

### Mode Comparison

Query: "I'm having login issues, can you check my account 5 and help?" Measured with `measure_latency.py` (repo root): each mode's orchestrator runs in an ADK `InMemoryRunner` against the live A2A agents, timed with `time.perf_counter()` from sending the query to the final event. One run per mode.

| Mode | Agents Called | Latency | Context Passing |
|------|-------------|---------|-----------------|
| Basic (Sequential) | Data → Support | **64.5 s** (full answer: customer 5 looked up, login ticket #26 created) | Support sees data agent's reply in session history |
| Advanced (Dynamic) | Router (`sequential`) → Data → Support | 9.6 s* | Routing decision in state; skipped agents return a note |
| Parallel | Data ‖ Support → Synthesizer | n/a* | Outputs saved to state keys via after_agent_callback |

\*Run on 2026-10-25 with `gemini-3.5-flash` (the default `gemini-3.8-flash` returned `503 UNAVAILABLE – high demand`). The basic run completed end to end. The advanced and parallel runs started right after it and hit the Gemini **free-tier limit of 5 requests/minute/model** (`429 RESOURCE_EXHAUSTED`): in advanced mode the router correctly chose `sequential` and dispatched both A2A agents, but their LLM calls were rejected, so 9.6 s is not a valid end-to-end latency; parallel mode was rejected immediately. `measure_latency.py` now waits 65 s between modes. Expected result with sufficient quota: parallel ≈ max(data, support) + synthesis, i.e. lower than sequential; advanced saves a full agent call on single-intent queries (e.g. "Get customer 5 info" → `data_only`).

**Error-handling lesson:** both 503 (overload) and 429 (quota) surfaced as A2A task failures; production code should add retry with backoff and fall back to a second model.

---

## Key Learnings
1. Tool filtering (least privilege) is a stronger safety control than prompt instructions alone.
2. AgentCards make agents discoverable and interchangeable; the orchestrator only needs a URL.
3. Orchestration pattern is a latency/context trade-off: sequential shares context, parallel is faster, dynamic routing saves calls.

## Ideas for Improvement
- Replace keyword routing with an LLM classifier (structured output) for ambiguous queries.
- Add authentication to the A2A endpoints and per-customer authorization on MCP tools.
