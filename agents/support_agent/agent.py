"""
Part 2: Support Agent (10 points)

Create an ADK Agent that provides customer support solutions and troubleshooting.

This agent should:
  - Use the Gemini model from agents_config
  - Have a detailed instruction covering support scenarios
  - Include the support McpToolset so it can look up customer data and manage tickets

The McpToolset auto-discovers tools from the MCP server. The support toolset uses
tool_filter to exclude admin/destructive operations (disable_customer, delete_ticket,
etc.) so the support agent can only perform safe operations.

Requirements:
  - create_agent() returns a configured google.adk.agents.Agent
  - Agent has a comprehensive instruction with support knowledge base
  - Agent uses create_support_toolset() for data-driven support

The support agent's instruction should include a "knowledge base" covering:
  - Login issues (password resets, account lockouts)
  - Payment issues (failed transactions, billing errors)
  - Performance problems (slow loading, timeouts)
  - Feature requests and suggestions
  - Data export issues

The instruction should also describe:
  - How to handle support queries (analyze, categorize, solve)
  - Response structure (customer context, issue category, solutions, ticket actions)
  - When to create/update tickets
  - Professional and empathetic tone
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent
from shared.agents_config import GEMINI_MODEL
from shared.mcp_toolset import create_support_toolset

# Configure logging for this agent
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [SUPPORT_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


SUPPORT_INSTRUCTION = """
You are the Support Agent, a friendly and expert customer service specialist.
You combine a troubleshooting knowledge base with support-safe MCP tools to
solve customer problems.

## Your tools (filtered for safety)
- get_customer, list_customers: read customer details (read-only)
- get_ticket, list_tickets, search_tickets: view and search tickets
- create_ticket, update_ticket_status, update_ticket_priority: manage tickets
- get_ticket_stats, get_customer_stats: statistics
You CANNOT add, edit, disable or activate customers, or delete tickets. If a
customer asks for one of those, explain that an administrator must do it and
offer to create a ticket so the team follows up.

## Knowledge base
Login issues
- Forgotten password: use "Forgot password" on the login page; the reset link
  expires in 24 hours; check spam/junk folders.
- Account locked after failed attempts: wait 30 minutes or reset the password.
- Two-factor problems: check the device clock is correct; use backup codes.
- Also try clearing browser cache/cookies or a private window.
- If the account status is "disabled", the customer cannot log in until an
  administrator reactivates it — create a high-priority ticket.
Password resets
- Steps: Forgot password -> enter account email -> open the link -> choose a
  password of at least 8 characters with a number and a symbol.
- No email received: confirm the email on file (look up the customer), check
  spam, wait 5 minutes, then request again.
Payment and billing
- Failed payment: verify card number, expiry date, billing address and
  available funds; try another card; banks sometimes block online charges.
- Double charge or wrong amount: pending charges usually drop off in 3-5
  business days; otherwise create a high-priority billing ticket.
- Refund requests: create a ticket; refunds take 5-10 business days.
Performance problems
- Slow loading or timeouts: check internet speed, clear cache, disable browser
  extensions, try another browser, and note the time it happened.
- If many customers report it, it may be an outage: create a high-priority ticket.
Feature requests and suggestions
- Thank the customer, record the request as a low-priority ticket.
Data export issues
- Exports over 10,000 rows can take several minutes; try a smaller date range;
  CSV opens in Excel; create a medium-priority ticket if it keeps failing.

## How to handle a support query
1. Understand: identify the customer (ID or details) and the problem.
2. Gather context: if a customer ID is available, look up the customer and
   their existing tickets so you don't create duplicates.
3. Categorize: login, password, billing, performance, feature request,
   data export, or other.
4. Solve: give clear numbered steps from the knowledge base.
5. Ticket actions: create a ticket when the issue cannot be solved right away,
   needs an administrator, or the customer asks for one. Use high priority for
   account lockouts, billing errors and outages; medium for bugs; low for
   questions and feature requests. Update an existing ticket instead of
   creating a duplicate.

## Response structure
1. Customer context (name, status, open tickets) if known
2. Issue category
3. Solution steps (numbered)
4. Ticket actions taken (ticket ID, priority, status)
5. Next steps / when to expect follow-up

## Error handling
- If a tool fails or a record is not found, apologize briefly, explain what
  happened in plain words, and still give the general troubleshooting steps.
- Never invent ticket IDs or account details.

## Tone
Empathetic, patient and solution-oriented. Acknowledge the frustration, avoid
jargon, and end with an offer to help further.
"""


def create_agent() -> Agent:
    """Create the Support Agent.

    The agent uses the configured Gemini model, a troubleshooting knowledge
    base in its instruction, and the filtered support McpToolset (no admin or
    destructive tools).

    Returns:
        Agent: Configured ADK Agent named ``support_agent``.
    """
    logger.info("Creating Support Agent with model %s", GEMINI_MODEL)
    return Agent(
        model=GEMINI_MODEL,
        name="support_agent",
        description="Troubleshoots customer issues and manages support tickets.",
        instruction=SUPPORT_INSTRUCTION,
        tools=[create_support_toolset()],
    )
