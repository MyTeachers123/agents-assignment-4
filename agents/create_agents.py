"""
Part 2: Agent Factory and AgentCard Definitions (Agent Cards, 10 points)

Create AgentCards for A2A discovery and a factory function to create all agents.

AgentCards are the A2A protocol's way of advertising agent capabilities.
They include metadata like name, URL, description, skills, and examples.

Requirements:
  - create_customer_data_agent_card() returns valid AgentCard
  - create_support_agent_card() returns valid AgentCard
  - create_host_agent_card() returns valid AgentCard
  - create_all_agents() returns dict with all agents and cards

Each AgentCard needs:
  - name: Human-readable agent name
  - url: The agent's server URL
  - description: What the agent does
  - version: Version string (e.g., '1.0')
  - capabilities: AgentCapabilities(streaming=True)
  - default_input_modes: ['text/plain']
  - default_output_modes: ['text/plain'] or ['application/json']
  - preferred_transport: TransportProtocol.jsonrpc
  - skills: List of AgentSkill with id, name, description, tags, examples
"""

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    HOST_AGENT_URL,
)

# Import agent creation functions
from customer_data_agent.agent import create_agent as create_customer_data_agent
from support_agent.agent import create_agent as create_support_agent
from host_agent.agent import create_agent as create_host_agent


# =============================================================================
# TODO 1: Customer Data Agent Card
# =============================================================================

def create_customer_data_agent_card() -> AgentCard:
    """
    Create AgentCard for Customer Data Agent.

    TODO: Return an AgentCard with:
      - name='Customer Data Agent'
      - url=CUSTOMER_DATA_AGENT_URL
      - description describing data management capabilities
      - version='1.0'
      - capabilities=AgentCapabilities(streaming=True)
      - default_input_modes=['text/plain']
      - default_output_modes=['application/json']
      - preferred_transport=TransportProtocol.jsonrpc
      - skills: at least one AgentSkill with relevant examples

    Example AgentSkill:
        AgentSkill(
            id='manage_customer_data',
            name='Manage Customer Data',
            description='Access and manage customer information and tickets',
            tags=['customers', 'tickets', 'data', 'database', 'mcp'],
            examples=[
                'Get customer information for ID 5',
                'List all active customers',
                'Show me all open tickets with high priority',
            ],
        )
    """
    raise NotImplementedError(
        "TODO: Create AgentCard for Customer Data Agent. "
        "See the docstring above for required fields."
    )


# =============================================================================
# TODO 2: Support Agent Card
# =============================================================================

def create_support_agent_card() -> AgentCard:
    """
    Create AgentCard for Support Agent.

    TODO: Return an AgentCard with:
      - name='Support Agent'
      - url=SUPPORT_AGENT_URL
      - description describing support capabilities
      - version='1.0'
      - capabilities=AgentCapabilities(streaming=True)
      - default_input_modes=['text/plain']
      - default_output_modes=['text/plain']
      - preferred_transport=TransportProtocol.jsonrpc
      - skills: at least one AgentSkill with support-related examples

    Example AgentSkill:
        AgentSkill(
            id='provide_support',
            name='Provide Customer Support',
            description='Troubleshoot issues and provide solutions',
            tags=['support', 'troubleshooting', 'solutions', 'help'],
            examples=[
                "I can't login to my account",
                'How do I reset my password?',
                'My payment failed, what should I do?',
            ],
        )
    """
    raise NotImplementedError(
        "TODO: Create AgentCard for Support Agent. "
        "See the docstring above for required fields."
    )


# =============================================================================
# TODO 3: Host Agent Card
# =============================================================================

def create_host_agent_card() -> AgentCard:
    """
    Create AgentCard for Host Agent (Orchestrator).

    TODO: Return an AgentCard with:
      - name='Customer Support Host Agent'
      - url=HOST_AGENT_URL
      - description describing orchestration capabilities
      - version='1.0'
      - capabilities=AgentCapabilities(streaming=True)
      - default_input_modes=['text/plain']
      - default_output_modes=['text/plain']
      - preferred_transport=TransportProtocol.jsonrpc
      - skills: at least one AgentSkill describing comprehensive support

    Example AgentSkill:
        AgentSkill(
            id='comprehensive_support',
            name='Comprehensive Customer Support',
            description='Provides complete support by combining data access and solutions',
            tags=['orchestration', 'support', 'data', 'coordination'],
            examples=[
                "I'm having login issues, can you check my account?",
                'Show me my open tickets and help resolve them',
            ],
        )
    """
    raise NotImplementedError(
        "TODO: Create AgentCard for Host Agent. "
        "See the docstring above for required fields."
    )


# =============================================================================
# TODO 4: Factory Function
# =============================================================================

def create_all_agents():
    """
    Create all agents for the customer support system.

    TODO: Create all agents and their cards, return a dictionary with:
      {
          'customer_data': {
              'agent': <Agent from create_customer_data_agent()>,
              'card': <AgentCard from create_customer_data_agent_card()>,
              'port': 10020,
          },
          'support': {
              'agent': <Agent from create_support_agent()>,
              'card': <AgentCard from create_support_agent_card()>,
              'port': 10021,
          },
          'host': {
              'agent': <Agent from create_host_agent()>,
              'card': <AgentCard from create_host_agent_card()>,
              'port': 10022,
          },
      }

    Returns:
        Dictionary with all agents and their cards
    """
    raise NotImplementedError(
        "TODO: Create all agents and agent cards, return them in a dictionary. "
        "See the docstring above for the expected structure."
    )
