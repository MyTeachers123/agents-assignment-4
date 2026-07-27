"""
Part 1: McpToolset Configuration for Google ADK Agents (20 points)

Google ADK's McpToolset auto-discovers all tools from an MCP server and makes them
available to ADK agents — no manual wrapper functions needed. Your job is to configure
toolsets with appropriate `tool_filter` lists so each agent only gets the tools it needs.

The MCP server exposes these 15 tools (see mcp_server/app.py):
  Customer: get_customer, list_customers, add_customer, update_customer,
            disable_customer, activate_customer
  Ticket:   get_ticket, list_tickets, create_ticket, update_ticket_status,
            update_ticket_priority, delete_ticket
  Stats:    get_ticket_stats, get_customer_stats, search_tickets

You must implement two toolset factory functions that return McpToolset instances
with `tool_filter` selecting only the tools appropriate for each agent's role.

Requirements for each toolset:
  - Return a McpToolset connected to the MCP server via SSE
  - Use tool_filter to select only relevant tools
  - Customer data toolset: broad data access (lookup, list, create, update, stats)
  - Support toolset: support-safe tools only (exclude admin ops like disable/delete)

Grading (20 points):
  - Both toolsets return McpToolset instances: 5 pts
  - tool_filter lists are correct and non-empty: 5 pts
  - Customer data toolset includes core tools: 5 pts
  - Support toolset excludes admin/destructive tools: 5 pts
"""

import os
import logging

from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams
from shared.agents_config import MCP_SERVER_URL

# Setup logging
logger = logging.getLogger(__name__)

# SSE endpoint URL for the MCP server
MCP_SSE_URL = f"{MCP_SERVER_URL}/sse"
logger.info(f"[MCP_TOOLSET] MCP SSE URL: {MCP_SSE_URL}")


# =============================================================================
# EXAMPLE: Full toolset with no filter (all 15 tools) - for reference only
# =============================================================================
def create_full_toolset() -> McpToolset:
    """Create an McpToolset with ALL MCP server tools (no filter).

    This is provided as a reference. In practice, agents should use
    filtered toolsets so each agent only has access to the tools it needs.

    Returns:
        McpToolset: Toolset connected to MCP server with all tools
    """
    logger.info("[MCP_TOOLSET] Creating full toolset (no filter)")
    return McpToolset(
        connection_params=SseConnectionParams(url=MCP_SSE_URL),
    )


# =============================================================================
# TODO 1: Customer Data Toolset (10 pts)
# =============================================================================
# Create a toolset for the Customer Data Agent with tool_filter selecting
# data-access and management tools.
#
# The customer data agent is the trusted back-office role and gets FULL access:
# list all 15 tools explicitly (see README "Tools to Include: All 15 tools").
#   - Looking up customers (get_customer, list_customers)
#   - Managing customer records (add_customer, update_customer)
#   - Ticket operations (get_ticket, list_tickets, create_ticket,
#     update_ticket_status, update_ticket_priority, delete_ticket)
#   - Statistics and search (get_ticket_stats, get_customer_stats, search_tickets)
#   - Admin operations (disable_customer, activate_customer)
#
# Hint:
#   return McpToolset(
#       connection_params=SseConnectionParams(url=MCP_SSE_URL),
#       tool_filter=[...list of tool name strings...],
#   )

def create_customer_data_toolset() -> McpToolset:
    """Create an McpToolset for the Customer Data Agent.

    Includes tools for customer lookup, ticket management, statistics,
    and admin operations. This agent has broad data access.

    Returns:
        McpToolset: Toolset with customer data tools
    """
    raise NotImplementedError(
        "TODO: Return McpToolset with tool_filter selecting customer data tools. "
        "Use SseConnectionParams(url=MCP_SSE_URL) and a tool_filter list."
    )


# =============================================================================
# TODO 2: Support Toolset (10 pts)
# =============================================================================
# Create a toolset for the Support Agent with tool_filter selecting only
# support-appropriate tools. The support agent should NOT have access to
# destructive or admin operations.
#
# The support agent needs tools for:
#   - Looking up customers (get_customer, list_customers)
#   - Viewing tickets (get_ticket, list_tickets, search_tickets)
#   - Creating/updating tickets (create_ticket, update_ticket_status,
#     update_ticket_priority)
#   - Statistics (get_ticket_stats, get_customer_stats)
#
# The support agent should NOT have:
#   - disable_customer (admin only)
#   - activate_customer (admin only)
#   - delete_ticket (destructive)
#   - add_customer (admin only)
#   - update_customer (admin only)
#
# Hint:
#   return McpToolset(
#       connection_params=SseConnectionParams(url=MCP_SSE_URL),
#       tool_filter=[...list of support-safe tool names...],
#   )

def create_support_toolset() -> McpToolset:
    """Create an McpToolset for the Support Agent.

    Includes only support-safe tools: lookups, ticket management, and stats.
    Excludes admin operations (disable/activate customer, delete ticket,
    add/update customer).

    Returns:
        McpToolset: Toolset with support-safe tools only
    """
    raise NotImplementedError(
        "TODO: Return McpToolset with tool_filter selecting support-safe tools. "
        "Exclude admin tools: disable_customer, activate_customer, delete_ticket, "
        "add_customer, update_customer."
    )
