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
    """Create the Host Agent (orchestrator).

    Wraps the Customer Data Agent and Support Agent as RemoteA2aAgents
    (discovered via their Agent Cards at the well-known path) and runs them
    in order with a SequentialAgent: data lookup first, then support guidance.

    Returns:
        SequentialAgent: ``customer_support_host`` with two remote sub-agents.
    """
    logger.info("Creating Host Agent (SequentialAgent with 2 RemoteA2aAgents)")

    # Remote Customer Data Agent, discovered through its A2A Agent Card
    remote_customer_data = RemoteA2aAgent(
        name="customer_data",
        description="Access customer and ticket data from MCP server",
        agent_card=f"{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    # Remote Support Agent, discovered through its A2A Agent Card
    remote_support = RemoteA2aAgent(
        name="support_specialist",
        description="Provide customer support and troubleshooting solutions",
        agent_card=f"{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    # Data lookup first, then support guidance (support sees the data in context)
    return SequentialAgent(
        name="customer_support_host",
        description="Orchestrates data lookup and support guidance via A2A",
        sub_agents=[remote_customer_data, remote_support],
    )
