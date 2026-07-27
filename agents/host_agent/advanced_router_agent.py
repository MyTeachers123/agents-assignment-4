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
# TODO BONUS: Routing Logic Functions
# =============================================================================

def analyze_query_intent(query: str) -> dict:
    """
    Analyze query to determine routing strategy.

    TODO: Implement query analysis that returns:
      - needs_data: bool (does the query need customer/ticket data?)
      - needs_support: bool (does the query need support/help?)
      - urgency: str ('low', 'medium', 'high')
      - execution_mode: str ('sequential', 'data_only', 'support_only')

    Hints:
      - Check for data keywords: 'customer', 'ticket', 'id', 'list', 'search'
      - Check for support keywords: 'help', 'issue', 'problem', 'reset', 'fix'
      - Check for urgency keywords: 'urgent', 'immediately', 'asap', 'critical'

    Example return:
        {
            'needs_data': True,
            'needs_support': True,
            'urgency': 'medium',
            'execution_mode': 'sequential'
        }
    """
    raise NotImplementedError("BONUS TODO: Implement analyze_query_intent")


# =============================================================================
# TODO BONUS: Callback Functions for Dynamic Routing
# =============================================================================

def should_run_customer_data_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback to determine if Customer Data Agent should run.

    TODO: Check callback_context.state for routing_decision.
      - If needs_data is False, return Content to skip the agent
      - If needs_data is True (or missing), return None to run it

    Hints:
      - routing_decision = callback_context.state.get('routing_decision', {})
      - Return None to run the agent
      - Return types.Content(parts=[types.Part(text="...")]) to skip
    """
    raise NotImplementedError("BONUS TODO: Implement should_run_customer_data_agent callback")


def should_run_support_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    Callback to determine if Support Agent should run.

    TODO: Similar to should_run_customer_data_agent but checks needs_support.
    """
    raise NotImplementedError("BONUS TODO: Implement should_run_support_agent callback")


# =============================================================================
# TODO BONUS: Router Agent with Dynamic Instruction
# =============================================================================

def create_router_instruction(readonly_context) -> str:
    """
    Dynamic instruction for router agent based on query analysis.

    TODO: Implement this function to:
      1. Get the user's query from readonly_context.latest_user_message
      2. Call analyze_query_intent(query)
      3. Store routing_decision in session state. NOTE: an instruction provider receives a
         ReadonlyContext, whose .state is a read-only view — assigning to it does not reliably
         persist. Compute and store the decision in a before_agent_callback on the router agent
         (which receives a writable CallbackContext); this function can then read it back.
      4. Return a dynamic instruction string based on the analysis
    """
    raise NotImplementedError("BONUS TODO: Implement create_router_instruction")


# =============================================================================
# TODO BONUS: Create Advanced Agent
# =============================================================================

def create_agent():
    """
    Create the advanced router agent with dynamic routing capabilities.

    TODO: Assemble the full orchestrator:
      1. Create router_agent (Agent with dynamic instruction)
      2. Create remote_customer_data (RemoteA2aAgent with before_agent_callback)
      3. Create remote_support (RemoteA2aAgent with before_agent_callback)
      4. Create sequential_execution_agent (SequentialAgent with both remotes)
      5. Create orchestrator (SequentialAgent with router + executor)

    Returns:
        Configured SequentialAgent with router and conditional sub-agents
    """
    raise NotImplementedError(
        "BONUS TODO: Create the advanced router agent. "
        "See the docstring above for the architecture."
    )
