"""
BONUS Part B: Parallel Router Agent (+10 points)

This is an OPTIONAL bonus implementation that executes agents in parallel.

Architecture:
  Orchestrator (SequentialAgent)
    -> Parallel Worker (ParallelAgent)
         -> RemoteA2aAgent("customer_data") with after_agent_callback -> state
         -> RemoteA2aAgent("support_specialist") with after_agent_callback -> state
    -> Summary Agent (LLM Agent) -- synthesizes parallel results

Key concepts:
  - ParallelAgent runs sub-agents concurrently instead of one after another
  - RemoteA2aAgent has NO output_key field (passing one raises a pydantic
    "Extra inputs are not permitted" ValidationError). Store each remote agent's
    output in state with an after_agent_callback instead.
  - Summary agent reads state and combines outputs into cohesive response

Requirements for bonus points:
  - RemoteA2aAgent output stored in state via after_agent_callback (3 pts)
  - ParallelAgent correctly assembled (2 pts)
  - Summary agent with dynamic instruction reading state (3 pts)
  - Full orchestrator assembled correctly (2 pts)
"""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORTANT: Apply A2A compatibility patch
from shared import a2a_compat  # noqa: F401

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.readonly_context import ReadonlyContext
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
from shared.agents_config import (
    CUSTOMER_DATA_AGENT_URL,
    SUPPORT_AGENT_URL,
    GEMINI_MODEL,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Summary Instruction Function
# =============================================================================

def create_summary_instruction(readonly_context: ReadonlyContext) -> str:
    """Build the synthesis instruction from the two parallel agents' outputs.

    Returns:
        str: Instruction containing both outputs and how to combine them.
    """
    data_output = readonly_context.state.get("customer_data_output", "") or "(no data returned)"
    support_output = readonly_context.state.get("support_specialist_output", "") or "(no guidance returned)"
    user_query = ""
    if readonly_context.user_content and readonly_context.user_content.parts:
        user_query = " ".join(p.text for p in readonly_context.user_content.parts if p.text)

    return f"""You are the response synthesizer for a customer support system.
Two specialist agents worked on the user's request in parallel.

USER REQUEST:
{user_query}

CUSTOMER DATA AGENT OUTPUT:
{data_output}

SUPPORT AGENT OUTPUT:
{support_output}

Write ONE cohesive, friendly reply that:
1. Starts with the relevant account/ticket facts from the data output.
2. Follows with the support agent's solution steps (numbered).
3. Lists any ticket actions taken (ticket IDs, priority).
4. Removes duplicated information and resolves conflicts in favor of the data output.
5. If either agent reported an error or returned nothing, say so briefly and
   give the best answer possible from the other output.
Do not invent IDs or facts that are not in the outputs above."""


def _make_store_output_callback(state_key: str):
    """Create an after_agent_callback that saves the agent's last reply to state.

    Args:
        state_key: Session state key to write the response text to.

    Returns:
        Callable used as ``after_agent_callback`` on a RemoteA2aAgent.
    """
    def _store_output(callback_context):
        try:
            for event in reversed(callback_context.session.events):
                if (event.author == callback_context.agent_name
                        and event.content and event.content.parts):
                    callback_context.state[state_key] = "".join(
                        p.text or "" for p in event.content.parts)
                    break
            else:
                callback_context.state[state_key] = ""
        except Exception as exc:
            logger.warning("Could not store output for %s: %s", state_key, exc)
            callback_context.state[state_key] = f"(error collecting output: {exc})"
        return None

    return _store_output


# =============================================================================
# Create Parallel Agent
# =============================================================================

def create_agent():
    """Create a parallel router that runs both specialists at once, then synthesizes.

    Returns:
        SequentialAgent: ParallelAgent (data + support) followed by a summary agent.
    """
    remote_customer_data = RemoteA2aAgent(
        name="customer_data",
        description="Access customer and ticket data from MCP server",
        agent_card=f"{CUSTOMER_DATA_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        after_agent_callback=_make_store_output_callback("customer_data_output"),
    )

    remote_support = RemoteA2aAgent(
        name="support_specialist",
        description="Provide customer support and troubleshooting solutions",
        agent_card=f"{SUPPORT_AGENT_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
        after_agent_callback=_make_store_output_callback("support_specialist_output"),
    )

    # Each agent writes to its own state key, so there is no race condition
    parallel_worker_agent = ParallelAgent(
        name="parallel_worker",
        description="Runs data lookup and support guidance concurrently",
        sub_agents=[remote_customer_data, remote_support],
    )

    summary_agent = Agent(
        model=GEMINI_MODEL,
        name="response_synthesizer",
        description="Combines the parallel agents' outputs into one answer",
        instruction=create_summary_instruction,
        include_contents="none",
    )

    return SequentialAgent(
        name="parallel_customer_support_host",
        description="Parallel A2A execution with response synthesis",
        sub_agents=[parallel_worker_agent, summary_agent],
    )
