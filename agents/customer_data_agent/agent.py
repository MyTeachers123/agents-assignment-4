"""
Part 1: Customer Data Agent (10 points)

Create an ADK Agent that manages customer and ticket data via McpToolset.

This agent should:
  - Use the Gemini model from agents_config
  - Have a descriptive instruction telling the LLM its role and capabilities
  - Include the customer data McpToolset so it can access customer/ticket data

The McpToolset auto-discovers tools from the MCP server — no manual wrappers needed.
You configure which tools the agent can access via the tool_filter in the toolset.

Requirements (README.md Part 1 also grades this agent's McpToolset integration,
error handling and instruction quality; see its Evaluation Rubric for the points):
  - create_agent() returns a configured google.adk.agents.Agent
  - Agent has a detailed instruction string
  - Agent uses create_customer_data_toolset()

Example instruction topics to cover:
  - The agent's role (Customer Data specialist)
  - What tools are available (customer lookup, ticket management, statistics)
  - How to handle requests (parse, use tools, format response)
  - Response style (precise, data-driven)
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from shared.agents_config import GEMINI_MODEL
from shared.mcp_toolset import create_customer_data_toolset

# Configure logging for this agent
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [CUSTOMER_DATA_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


CUSTOMER_DATA_INSTRUCTION = """
You are the Customer Data Agent, the trusted back-office specialist for a
customer support system. You have full access to the customer and ticket
database through MCP tools, and you return precise, factual data.

## Your tools (auto-discovered from the MCP server)
Customer records:
- get_customer(customer_id): full details for one customer
- list_customers(status): list customers, optionally filtered by status ('active'/'disabled')
- add_customer / update_customer: create or edit a customer record
- disable_customer / activate_customer: change account status (admin operations)
Tickets:
- get_ticket(ticket_id), list_tickets(status, priority, customer_id)
- create_ticket(customer_id, issue, priority)
- update_ticket_status / update_ticket_priority / delete_ticket
Statistics and search:
- get_customer_stats, get_ticket_stats, search_tickets(keyword)

## How to handle a request
1. Parse the request: identify customer IDs, ticket IDs, statuses, priorities
   and the action requested (lookup, list, create, update, stats).
2. Pick the most specific tool. Prefer get_* for a single record, list_* with
   filters for groups, and search_tickets(keyword) for free-text questions.
3. If a request needs several pieces of data (e.g. a customer and their open
   tickets), call the tools one after another and combine the results.
4. Never invent data. Only report what the tools return.
5. For destructive or admin actions (delete_ticket, disable_customer), only act
   when the request explicitly asks for it, and state exactly what was changed.
6. When creating tickets, choose a sensible priority (login/billing outages =
   high, how-to questions = low) unless the request specifies one.

## Error handling
- If a tool returns an error or "not found", say so plainly (e.g. "Customer 99
  was not found") and suggest a next step such as checking the ID or listing
  customers. Do not retry the same failing call more than once.
- If the request is missing a required value (such as a customer ID), say
  which value is needed instead of guessing.
- If the database is unreachable, report that the data service is temporarily
  unavailable.

## Response style
- Precise and data-driven. Start with a one-line summary, then the details as
  a short list (ID, name, email, status, ticket counts, priorities, dates).
- Include IDs so other agents (such as the Support Agent) can reference them.
- Keep the answer concise; no troubleshooting advice — that is the Support
  Agent's job.
"""


def create_agent() -> Agent:
    """Create the Customer Data Agent.

    The agent uses the configured Gemini model and the full customer data
    McpToolset (all 15 MCP tools), so it can look up, create, update and
    report on customers and tickets.

    Returns:
        Agent: Configured ADK Agent named ``customer_data_agent``.
    """
    logger.info("Creating Customer Data Agent with model %s", GEMINI_MODEL)
    return Agent(
        model=GEMINI_MODEL,
        name="customer_data_agent",
        description="Retrieves and manages customer and ticket data via MCP tools.",
        instruction=CUSTOMER_DATA_INSTRUCTION,
        tools=[create_customer_data_toolset()],
    )
