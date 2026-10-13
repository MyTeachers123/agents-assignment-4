"""
Run Customer Support A2A Multi-Agent System (GIVEN - fully implemented)
Starts all agent servers and provides a client interface

This script runs from the project root directory.
"""

import asyncio
import logging
import os
import sys
import threading
import time
from typing import Any

# Add agents directory to Python path
agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents')
sys.path.insert(0, agents_dir)

# Load .env BEFORE importing agent modules: shared/agents_config.py reads
# GEMINI_MODEL and MCP_SERVER_URL at import time.
from dotenv import load_dotenv
project_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(project_root, '.env'))

# IMPORTANT: Apply A2A compatibility patch BEFORE any A2A imports
from shared import a2a_compat  # noqa: F401

import httpx
import nest_asyncio
import uvicorn

from a2a.client import ClientConfig, ClientFactory, create_text_message_object
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import TransportProtocol
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

from google.adk.a2a.executor.a2a_agent_executor import (
    A2aAgentExecutor,
    A2aAgentExecutorConfig,
)
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from create_agents import create_all_agents

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def print_agent_card(agent_card, port: int):
    """Print agent card in a nice formatted way."""
    print("\n" + "="*80)
    print(f"AGENT: {agent_card.name}")
    print("="*80)
    print(f"URL: http://127.0.0.1:{port}")
    print(f"Description: {agent_card.description}")
    print(f"Protocol: {agent_card.protocol_version}")
    print(f"Transport: {agent_card.preferred_transport}")
    print(f"\nSkills:")
    for skill in agent_card.skills:
        print(f"  - {skill.name}: {skill.description}")
        print(f"    Examples:")
        examples = skill.examples if hasattr(skill, 'examples') else []
        for example in examples[:3]:  # Show first 3 examples
            print(f"      * {example}")
    print("="*80 + "\n")

# Apply nest_asyncio for Jupyter/Colab compatibility
nest_asyncio.apply()


def create_agent_a2a_server(agent, agent_card):
    """
    Create an A2A server for an ADK agent with logging.

    Args:
        agent: The ADK agent instance
        agent_card: The agent card with metadata

    Returns:
        A2AStarletteApplication instance
    """
    runner = Runner(
        app_name=agent.name,
        agent=agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )

    config = A2aAgentExecutorConfig()
    executor = A2aAgentExecutor(runner=runner, config=config)

    # Create custom request handler with logging. DefaultRequestHandler has no
    # handle_request(); A2A message/send and message/stream requests arrive at
    # on_message_send() and on_message_send_stream().
    class LoggingRequestHandler(DefaultRequestHandler):
        def _log_request(self, params):
            agent_name = agent_card.name
            logger.info(f"[{agent_name}] Received request")

            # Log request details
            if hasattr(params, 'message') and params.message:
                msg_text = ""
                if hasattr(params.message, 'parts') and params.message.parts:
                    for part in params.message.parts:
                        if hasattr(part, 'root') and hasattr(part.root, 'text'):
                            msg_text += part.root.text
                if msg_text:
                    logger.info(f"[{agent_name}] Message: {msg_text[:100]}...")

        async def on_message_send(self, params, context=None):
            self._log_request(params)
            response = await super().on_message_send(params, context)
            logger.info(f"[{agent_card.name}] Sending response")
            return response

        async def on_message_send_stream(self, params, context=None):
            self._log_request(params)
            async for event in super().on_message_send_stream(params, context):
                yield event
            logger.info(f"[{agent_card.name}] Sending response")

    request_handler = LoggingRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    return A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )


async def run_agent_server(agent, agent_card, port: int) -> None:
    """Run a single agent server."""
    app = create_agent_a2a_server(agent, agent_card)

    config = uvicorn.Config(
        app.build(),
        host='127.0.0.1',
        port=port,
        log_level='warning',
        loop='none',  # Use the current event loop
    )

    server = uvicorn.Server(config)
    await server.serve()


async def start_all_servers() -> None:
    """Start all agent servers."""
    logger.info("Creating agents...")
    agents_config = create_all_agents()

    # Print agent cards
    print("\n" + " STARTING MULTI-AGENT SYSTEM ".center(80, "="))
    for agent_name, config in agents_config.items():
        print_agent_card(config['card'], config['port'])

    # Create tasks for all servers
    tasks = []
    for agent_name, config in agents_config.items():
        task = asyncio.create_task(
            run_agent_server(
                config['agent'],
                config['card'],
                config['port']
            )
        )
        tasks.append(task)

    # Give servers time to start
    await asyncio.sleep(3)

    print("\n" + "="*80)
    print(" ALL AGENT SERVERS STARTED AND READY ".center(80))
    print("="*80)
    print(f"Customer Data Agent:  http://127.0.0.1:{agents_config['customer_data']['port']}")
    print(f"Support Agent:        http://127.0.0.1:{agents_config['support']['port']}")
    print(f"Host Agent:           http://127.0.0.1:{agents_config['host']['port']}")
    print("="*80 + "\n")

    # Keep servers running
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down servers...")


def run_servers_in_background() -> None:
    """Run servers in a background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_all_servers())


class A2AClient:
    """Simple A2A client for testing agents."""

    def __init__(self, default_timeout: float = 240.0):
        self._agent_info_cache: dict[str, dict[str, Any] | None] = {}
        self.default_timeout = default_timeout

    async def send_message(self, agent_url: str, message: str) -> str:
        """
        Send a message to an A2A agent.

        Args:
            agent_url: The agent's base URL
            message: The message to send

        Returns:
            The agent's response
        """
        timeout_config = httpx.Timeout(
            timeout=self.default_timeout,
            connect=10.0,
            read=self.default_timeout,
            write=10.0,
            pool=5.0,
        )

        async with httpx.AsyncClient(timeout=timeout_config) as httpx_client:
            # Check cache for agent card
            if agent_url in self._agent_info_cache and self._agent_info_cache[agent_url] is not None:
                agent_card_data = self._agent_info_cache[agent_url]
            else:
                # Fetch agent card
                agent_card_response = await httpx_client.get(
                    f'{agent_url}{AGENT_CARD_WELL_KNOWN_PATH}'
                )
                agent_card_data = self._agent_info_cache[agent_url] = agent_card_response.json()

            # Create AgentCard from data
            from a2a.types import AgentCard
            agent_card = AgentCard(**agent_card_data)

            # Create A2A client
            config = ClientConfig(
                httpx_client=httpx_client,
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                use_client_preference=True,
            )

            factory = ClientFactory(config)
            client = factory.create(agent_card)

            # Create and send message
            message_obj = create_text_message_object(content=message)

            # Collect responses
            responses = []
            async for response in client.send_message(message_obj):
                responses.append(response)

            # Extract response text
            if responses and isinstance(responses[-1], tuple) and len(responses[-1]) > 0:
                task = responses[-1][0]
                if task.artifacts:
                    return ''.join(
                        getattr(part.root, 'text', '') for part in task.artifacts[0].parts
                    )
                # Failed or empty task: raise with the agent's status message instead
                # of returning the Task repr (which looks like a real answer to callers).
                message = task.status.message
                detail = ' '.join(
                    getattr(part.root, 'text', '') for part in message.parts
                ) if message else ''
                raise RuntimeError(
                    f"A2A task {task.status.state.value} with no artifacts: "
                    f"{detail or 'no status message (check the agent server logs)'}"
                )

            return 'No response received'


async def test_agents():
    """Test all agents."""
    client = A2AClient()

    print("\n" + "="*80)
    print("TESTING CUSTOMER SUPPORT A2A AGENTS")
    print("="*80 + "\n")

    checks = [
        ("1. Testing Customer Data Agent", "http://localhost:10020",
         "Show me all open tickets with high priority"),
        ("2. Testing Support Agent", "http://localhost:10021",
         "I can't login to my account, what should I do?"),
        ("3. Testing Host Agent (Orchestrator)", "http://localhost:10022",
         "I'm having login issues, can you check my account and help me resolve this?"),
    ]
    for title, url, query in checks:
        print(title)
        print("-"*80)
        try:
            response = await client.send_message(url, query)
            print(f"Response: {response}\n")
        except Exception as e:
            print(f"[FAIL] {e}\n")

    print("="*80)
    print("All tests completed!")
    print("="*80 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Customer Support A2A Multi-Agent System"
    )
    parser.add_argument(
        '--mode',
        choices=['start', 'test'],
        default='start',
        help='Mode: start servers or run tests'
    )

    args = parser.parse_args()

    if args.mode == 'start':
        # Start servers in background thread
        logger.info("Starting agent servers...")
        server_thread = threading.Thread(target=run_servers_in_background, daemon=True)
        server_thread.start()

        # Wait for servers to be ready
        time.sleep(5)

        logger.info("\n" + "="*80)
        logger.info("Servers are running! Press Ctrl+C to stop.")
        logger.info("="*80 + "\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nShutting down...")

    elif args.mode == 'test':
        # Start servers first
        logger.info("Starting agent servers for testing...")
        server_thread = threading.Thread(target=run_servers_in_background, daemon=True)
        server_thread.start()

        # Wait for servers to be ready
        time.sleep(5)

        # Run tests
        asyncio.run(test_agents())


if __name__ == "__main__":
    main()
