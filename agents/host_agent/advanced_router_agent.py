"""
BONUS Part A: Advanced Router Agent with Dynamic Routing (+15 points)

This is an OPTIONAL bonus implementation that adds intelligent routing:
  - Analyzes query intent to determine which agents to invoke
  - Uses before_agent_callback to conditionally skip agents
  - Includes a router LLM agent for task decomposition

Architecture:
  Orchestrator (SequentialAgent)
    -> Router Agent (LLM Agent) -- analyzes query, sets routing decision
    -> Sequential Executor (SequentialAgent)
         -> RemoteA2aAgent("customer_data") with before_agent_callback
         -> RemoteA2aAgent("support_specialist") with before_agent_callback

Requirements for bonus points:
  - analyze_query_intent function works correctly (5 pts)
  - Callback functions properly skip/run agents (4 pts)
  - Router agent with dynamic instruction (3 pts)
  - Full orchestrator assembled correctly (3 pts)
"""

import sys
import os
import logging
import re
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Apply A2A compatibility patch BEFORE importing RemoteA2aAgent
from shared import a2a_compat  # noqa: F401

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    GEMINI_MODEL,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [ROUTER_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Routing Logic Functions
# =============================================================================

DATA_KEYWORDS = (
    "customer", "ticket", "account", "id", "list", "search", "show", "status",
    "history", "record", "stats", "statistics", "open tickets", "my tickets",
)
SUPPORT_KEYWORDS = (
    "help", "issue", "problem", "reset", "fix", "can't", "cannot", "unable",
    "error", "login", "log in", "password", "payment", "billing", "charge",
    "refund", "slow", "crash", "timeout", "how do i", "how to", "not working",
)
URGENCY_HIGH = ("urgent", "immediately", "asap", "critical", "emergency", "now")
URGENCY_MEDIUM = ("soon", "important", "today", "blocked", "failed")


def analyze_query_intent(query: str) -> dict:
    """Analyze a user query with keyword rules to choose a routing strategy.

    Args:
        query: The raw user query text.

    Returns:
        dict: ``needs_data`` (bool), ``needs_support`` (bool), ``urgency``
        ('low' | 'medium' | 'high') and ``execution_mode``
        ('sequential' | 'data_only' | 'support_only').
    """
    text = (query or "").lower()

    def has_any(keywords) -> bool:
        """Whole-word / whole-phrase match, so 'id' does not match 'did'."""
        return any(re.search(rf"(?<!\w){re.escape(k)}(?!\w)", text) for k in keywords)

    needs_data = has_any(DATA_KEYWORDS) or bool(re.search(r"\d", text))
    needs_support = has_any(SUPPORT_KEYWORDS)

    if has_any(URGENCY_HIGH):
        urgency = "high"
    elif has_any(URGENCY_MEDIUM):
        urgency = "medium"
    else:
        urgency = "low"

    if needs_data and needs_support:
        mode = "sequential"
    elif needs_data:
        mode = "data_only"
    elif needs_support:
        mode = "support_only"
    else:
        # Unclear intent: run both agents so the user still gets an answer
        needs_data, needs_support, mode = True, True, "sequential"

    decision = {
        "needs_data": needs_data,
        "needs_support": needs_support,
        "urgency": urgency,
        "execution_mode": mode,
    }
    logger.info("Routing decision for %r: %s", query[:80] if query else "", decision)
    return decision


def _user_text(user_content: Optional[types.Content]) -> str:
    """Extract plain text from the user's Content object (empty string if none)."""
    if not user_content or not user_content.parts:
        return ""
    return " ".join(p.text for p in user_content.parts if getattr(p, "text", None))


# =============================================================================
# Callback Functions for Dynamic Routing
# =============================================================================

def store_routing_decision(callback_context: CallbackContext) -> Optional[types.Content]:
    """before_agent_callback for the router: analyze the query and save the decision.

    Runs on a writable CallbackContext, so the decision persists in session
    state for the conditional callbacks below.

    Returns:
        None, so the router agent itself always runs.
    """
    try:
        query = _user_text(callback_context.user_content)
        callback_context.state["routing_decision"] = analyze_query_intent(query)
    except Exception as exc:  # never block the pipeline on a routing error
        logger.warning("Routing analysis failed (%s); defaulting to sequential", exc)
        callback_context.state["routing_decision"] = {
            "needs_data": True, "needs_support": True,
            "urgency": "medium", "execution_mode": "sequential",
        }
    return None


def should_run_customer_data_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """before_agent_callback deciding whether the Customer Data Agent runs.

    Returns:
        None to run the agent, or a Content message to skip it when the
        routing decision says no data lookup is needed.
    """
    routing_decision = callback_context.state.get("routing_decision", {}) or {}
    if routing_decision.get("needs_data", True):
        logger.info("Running customer_data agent")
        return None
    logger.info("Skipping customer_data agent (mode=%s)", routing_decision.get("execution_mode"))
    return types.Content(
        role="model",
        parts=[types.Part(text="[Router] Customer data lookup skipped: not needed for this query.")],
    )


def should_run_support_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """before_agent_callback deciding whether the Support Agent runs.

    Returns:
        None to run the agent, or a Content message to skip it when the
        routing decision says no troubleshooting is needed.
    """
    routing_decision = callback_context.state.get("routing_decision", {}) or {}
    if routing_decision.get("needs_support", True):
        logger.info("Running support_specialist agent")
        return None
    logger.info("Skipping support_specialist agent (mode=%s)", routing_decision.get("execution_mode"))
    return types.Content(
        role="model",
        parts=[types.Part(text="[Router] Support guidance skipped: this was a data-only request.")],
    )


# =============================================================================
# Router Agent with Dynamic Instruction
# =============================================================================

def create_router_instruction(readonly_context) -> str:
    """Build the router agent's instruction from the stored routing decision.

    Reads ``routing_decision`` (written by ``store_routing_decision``) from
    state; falls back to analyzing the query directly if it is missing.

    Returns:
        str: Instruction describing the plan for this specific query.
    """
    decision = readonly_context.state.get("routing_decision")
    if not decision:
        decision = analyze_query_intent(_user_text(readonly_context.user_content))

    steps = []
    if decision["needs_data"]:
        steps.append("the Customer Data Agent will look up account and ticket data")
    if decision["needs_support"]:
        steps.append("the Support Agent will provide troubleshooting and ticket actions")

    return (
        "You are the routing coordinator for a customer support system.\n"
        f"Query analysis: execution_mode={decision['execution_mode']}, "
        f"urgency={decision['urgency']}.\n"
        f"Plan: {'; then '.join(steps)}.\n"
        "Reply with ONE short sentence telling the user what will happen next "
        "(for high urgency, acknowledge that the request is being prioritized). "
        "Restate any customer ID or ticket ID from the query so the next agents "
        "can use it. Do not answer the question yourself."
    )


# =============================================================================
# Create Advanced Agent
# =============================================================================

def create_agent():
    """Create the advanced router: analyze the query, then conditionally run agents.

    Returns:
        SequentialAgent: router agent followed by a sequential executor whose
        remote A2A agents are skipped by callbacks when not needed.
    """
    router_agent = Agent(
        model=GEMINI_MODEL,
        name="query_router",
        description="Analyzes the query and decides which specialist agents to call",
        instruction=create_router_instruction,
        before_agent_callback=store_routing_decision,
    )

    remote_customer_data = RemoteA2aAgent(
        name="customer_data",
        description="Access customer and ticket data from MCP server",
        agent_card=f"{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        before_agent_callback=should_run_customer_data_agent,
    )

    remote_support = RemoteA2aAgent(
        name="support_specialist",
        description="Provide customer support and troubleshooting solutions",
        agent_card=f"{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        before_agent_callback=should_run_support_agent,
    )

    sequential_execution_agent = SequentialAgent(
        name="conditional_executor",
        description="Runs the selected specialist agents in order",
        sub_agents=[remote_customer_data, remote_support],
    )

    return SequentialAgent(
        name="advanced_customer_support_host",
        description="Dynamic router with conditional A2A agent execution",
        sub_agents=[router_agent, sequential_execution_agent],
    )
