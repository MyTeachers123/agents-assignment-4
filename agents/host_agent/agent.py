"""
Part 2: Host Agent / Orchestrator (10 points)

Create a SequentialAgent that coordinates between Customer Data Agent and Support Agent
using the A2A (Agent-to-Agent) protocol.

This is the core of the assignment: connecting remote agents via A2A.

Architecture:
  Host Agent (SequentialAgent)
    -> RemoteA2aAgent("customer_data") -- calls Customer Data Agent via A2A
    -> RemoteA2aAgent("support_specialist") -- calls Support Agent via A2A

Requirements (README.md Part 2 "A2A Integration" also grades the
RemoteA2aAgent wiring in this file; see its Evaluation Rubric for the points):
  - Import and apply the A2A compatibility patch (CRITICAL)
  - Create RemoteA2aAgent for Customer Data Agent
  - Create RemoteA2aAgent for Support Agent
  - Create SequentialAgent combining both remote agents

Key concepts:
  - RemoteA2aAgent wraps a remote agent as a local sub-agent
  - agent_card URL = agent_url + AGENT_CARD_WELL_KNOWN_PATH
  - SequentialAgent runs sub-agents in order, passing context between them
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# =============================================================================
# CRITICAL: Apply A2A compatibility patch BEFORE importing RemoteA2aAgent
# This fixes an import issue between google-adk and a2a-sdk versions.
# =============================================================================
from shared import a2a_compat  # noqa: F401

from google.adk.agents import SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
)

# Configure logging for this agent
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [HOST_AGENT] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_agent() -> SequentialAgent:
    """
    Create the Host Agent (Orchestrator).

    TODO: Implement this function to:

    1. Create a RemoteA2aAgent for the Customer Data Agent:
       - name='customer_data'
       - description='Access customer and ticket data from MCP server'
       - agent_card=f'{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}'

    2. Create a RemoteA2aAgent for the Support Agent:
       - name='support_specialist'
       - description='Provide customer support and troubleshooting solutions'
       - agent_card=f'{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}'

    3. Create and return a SequentialAgent:
       - name='customer_support_host'
       - sub_agents=[remote_customer_data, remote_support]

    Example:
        remote_customer_data = RemoteA2aAgent(
            name='customer_data',
            description='Access customer and ticket data from MCP server',
            agent_card=f'{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        )

        remote_support = RemoteA2aAgent(
            name='support_specialist',
            description='Provide customer support and troubleshooting solutions',
            agent_card=f'{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}',
        )

        return SequentialAgent(
            name='customer_support_host',
            sub_agents=[remote_customer_data, remote_support],
        )

    Returns:
        Configured SequentialAgent instance
    """
    raise NotImplementedError(
        "TODO: Create the Host Agent with two RemoteA2aAgent sub-agents "
        "(customer_data and support_specialist) wrapped in a SequentialAgent. "
        "See the docstring above for the exact structure."
    )
