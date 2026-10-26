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
    CUSTOMER_DATA_AGENT_PORT,
    SUPPORT_AGENT_PORT,
    HOST_AGENT_PORT,
)

# Import agent creation functions
from customer_data_agent.agent import create_agent as create_customer_data_agent
from support_agent.agent import create_agent as create_support_agent
from host_agent.agent import create_agent as create_host_agent


# =============================================================================
# Customer Data Agent Card
# =============================================================================

def create_customer_data_agent_card() -> AgentCard:
    """Create the A2A AgentCard for the Customer Data Agent.

    Returns:
        AgentCard: Card served at the agent's well-known URL, advertising
        data-management and statistics skills (JSON output).
    """
    return AgentCard(
        name="Customer Data Agent",
        url=CUSTOMER_DATA_AGENT_URL,
        description=(
            "Back-office data specialist with full MCP access to the customer "
            "and ticket database: lookups, listing, ticket creation/updates, "
            "admin account operations and statistics."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["application/json"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="manage_customer_data",
                name="Manage Customer Data",
                description="Access and manage customer information and tickets",
                tags=["customers", "tickets", "data", "database", "mcp"],
                examples=[
                    "Get customer information for ID 5",
                    "List all active customers",
                    "Show me all open tickets with high priority",
                    "Create a ticket for customer 1 about login issues",
                ],
            ),
            AgentSkill(
                id="customer_statistics",
                name="Customer and Ticket Statistics",
                description="Report customer and ticket statistics and search tickets",
                tags=["stats", "reporting", "search"],
                examples=[
                    "How many open tickets are there?",
                    "Search tickets mentioning 'payment'",
                ],
            ),
        ],
    )


# =============================================================================
# Support Agent Card
# =============================================================================

def create_support_agent_card() -> AgentCard:
    """Create the A2A AgentCard for the Support Agent.

    Returns:
        AgentCard: Card advertising troubleshooting/support skills.
    """
    return AgentCard(
        name="Support Agent",
        url=SUPPORT_AGENT_URL,
        description=(
            "Customer support specialist with a troubleshooting knowledge base "
            "(login, password, billing, performance, data export) and "
            "support-safe MCP tools for looking up customers and managing tickets."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="provide_support",
                name="Provide Customer Support",
                description="Troubleshoot issues and provide solutions",
                tags=["support", "troubleshooting", "solutions", "help"],
                examples=[
                    "I can't login to my account",
                    "How do I reset my password?",
                    "My payment failed, what should I do?",
                    "The dashboard is very slow to load",
                ],
            ),
        ],
    )


# =============================================================================
# Host Agent Card
# =============================================================================

def create_host_agent_card() -> AgentCard:
    """Create the A2A AgentCard for the Host (orchestrator) Agent.

    Returns:
        AgentCard: Card advertising the comprehensive support skill.
    """
    return AgentCard(
        name="Customer Support Host Agent",
        url=HOST_AGENT_URL,
        description=(
            "Orchestrator that delegates over A2A: first the Customer Data Agent "
            "looks up account and ticket data, then the Support Agent provides "
            "troubleshooting guidance and ticket actions."
        ),
        version="1.0",
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport=TransportProtocol.jsonrpc,
        skills=[
            AgentSkill(
                id="comprehensive_support",
                name="Comprehensive Customer Support",
                description="Provides complete support by combining data access and solutions",
                tags=["orchestration", "support", "data", "coordination"],
                examples=[
                    "I'm having login issues, can you check my account?",
                    "Show me my open tickets and help resolve them",
                    "Check account 5 and create a ticket for billing issues",
                ],
            ),
        ],
    )


# =============================================================================
# Factory Function
# =============================================================================

def create_all_agents():
    """Create all agents and their AgentCards for the support system.

    Returns:
        dict: ``{"customer_data" | "support" | "host": {"agent", "card", "port"}}``.
    """
    return {
        "customer_data": {
            "agent": create_customer_data_agent(),
            "card": create_customer_data_agent_card(),
            "port": CUSTOMER_DATA_AGENT_PORT,
        },
        "support": {
            "agent": create_support_agent(),
            "card": create_support_agent_card(),
            "port": SUPPORT_AGENT_PORT,
        },
        "host": {
            "agent": create_host_agent(),
            "card": create_host_agent_card(),
            "port": HOST_AGENT_PORT,
        },
    }
