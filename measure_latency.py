"""
Measure wall-clock latency of the three host-agent modes (basic, advanced, parallel).

Prerequisites (each in its own terminal, from the repo root):
  1. MCP server:      cd mcp_server && python app.py
  2. Remote agents:   python run_agents.py --mode start
     (the Customer Data Agent on 10020 and Support Agent on 10021 must be up)

Usage:
  python measure_latency.py
  python measure_latency.py "Your custom query here"

Each mode's orchestrator is built in-process and run with an ADK InMemoryRunner;
its RemoteA2aAgents call the running agents over A2A. Latency is measured with
time.perf_counter() from sending the query until the final event is received.
"""

import asyncio
import os
import sys
import time

from dotenv import load_dotenv

load_dotenv()  # GEMINI_MODEL / GOOGLE_API_KEY must be loaded before agent imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents"))

from shared import a2a_compat  # noqa: F401,E402  (patch before RemoteA2aAgent import)

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from host_agent.agent import create_agent as create_basic  # noqa: E402
from host_agent.advanced_router_agent import create_agent as create_advanced  # noqa: E402
from host_agent.parallel_router_agent import create_agent as create_parallel  # noqa: E402

DEFAULT_QUERY = "I'm having login issues, can you check my account 5 and help?"
MODES = {"basic": create_basic, "advanced": create_advanced, "parallel": create_parallel}


async def run_mode(mode: str, query: str) -> tuple[float, list[str], str]:
    """Run one orchestrator mode on the query and time it.

    Args:
        mode: One of 'basic', 'advanced', 'parallel'.
        query: The user query to send.

    Returns:
        tuple: (latency in seconds, authors of events in order, final text).
    """
    agent = MODES[mode]()
    runner = InMemoryRunner(agent=agent, app_name=f"latency_{mode}")
    session = await runner.session_service.create_session(
        app_name=f"latency_{mode}", user_id="tester")
    message = types.Content(role="user", parts=[types.Part(text=query)])

    authors: list[str] = []
    final_text = ""
    start = time.perf_counter()
    async for event in runner.run_async(
            user_id="tester", session_id=session.id, new_message=message):
        if event.author and event.author not in authors:
            authors.append(event.author)
        if event.content and event.content.parts:
            text = "".join(p.text or "" for p in event.content.parts)
            if text.strip():
                final_text = text
    elapsed = time.perf_counter() - start
    return elapsed, authors, final_text


async def main() -> None:
    """Run every mode once with the same query and print a summary table."""
    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY
    print(f"Query: {query}\n")
    results = []
    for mode in MODES:
        print(f"=== {mode} ===")
        try:
            elapsed, authors, final_text = await run_mode(mode, query)
            print(f"Agents called: {' -> '.join(authors)}")
            print(f"Latency: {elapsed:.1f} s")
            print(f"Final answer (first 300 chars): {final_text[:300]}\n")
            if not final_text.strip() or elapsed < 2:
                print("[WARN] Empty or very fast reply: are the MCP server and "
                      "run_agents.py running? This timing is probably not valid.\n")
            results.append((mode, " -> ".join(authors), f"{elapsed:.1f} s"))
        except Exception as exc:  # keep measuring the other modes
            print(f"[ERROR] {mode} failed: {type(exc).__name__}: {exc}\n")
            results.append((mode, "error", "n/a"))

    print("\n| Mode | Agents Called | Latency |")
    print("|------|---------------|---------|")
    for mode, authors, latency in results:
        print(f"| {mode} | {authors} | {latency} |")


if __name__ == "__main__":
    asyncio.run(main())
