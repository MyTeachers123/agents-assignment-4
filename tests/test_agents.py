"""
Test harness for Part 2: Agent Structure

Verifies that agent creation functions are properly structured:
  - create_agent() functions exist and return Agent instances
  - Agents have proper instruction strings
  - Agents have tools configured

Usage:
    python -m pytest tests/test_agents.py -v
    python -m tests.test_agents
"""

import inspect
import sys
import os

# Add agents directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agents'))


def check_customer_data_agent():
    """Check Customer Data Agent structure."""
    print("Customer Data Agent:")

    results = []

    # Check 1: create_agent exists and is callable
    try:
        from customer_data_agent.agent import create_agent
        print("  [PASS] create_agent() function exists")
        results.append(True)
    except ImportError as e:
        print(f"  [FAIL] Cannot import create_agent: {e}")
        return [False]

    # Check 2: create_agent returns an Agent
    try:
        agent = create_agent()
        from google.adk.agents import Agent
        if isinstance(agent, Agent):
            print("  [PASS] create_agent() returns Agent instance")
            results.append(True)
        else:
            print(f"  [FAIL] create_agent() returns {type(agent).__name__}, expected Agent")
            results.append(False)
    except NotImplementedError:
        print("  [FAIL] create_agent() not implemented yet (raises NotImplementedError)")
        results.append(False)
        return results
    except Exception as e:
        print(f"  [FAIL] create_agent() raised error: {str(e)[:60]}")
        results.append(False)
        return results

    # Check 3: Agent has instruction
    instruction = getattr(agent, 'instruction', '') or ''
    if isinstance(instruction, str) and len(instruction) > 100:
        print(f"  [PASS] Agent has instruction ({len(instruction)} chars)")
        results.append(True)
    else:
        print(f"  [FAIL] Agent instruction too short ({len(instruction) if isinstance(instruction, str) else 'N/A'})")
        results.append(False)

    # Check 4: Agent has McpToolset in tools
    tools = getattr(agent, 'tools', []) or []
    try:
        from google.adk.tools.mcp_tool import McpToolset
        has_toolset = any(isinstance(t, McpToolset) for t in tools)
    except ImportError:
        has_toolset = len(tools) > 0
    if has_toolset:
        print(f"  [PASS] Agent has McpToolset in tools")
        results.append(True)
    else:
        print(f"  [FAIL] Agent tools should contain an McpToolset instance")
        results.append(False)

    # Check 5: Agent name
    name = getattr(agent, 'name', '')
    if name == 'customer_data_agent':
        print(f"  [PASS] Agent name is '{name}'")
        results.append(True)
    else:
        print(f"  [WARN] Agent name is '{name}', expected 'customer_data_agent'")
        results.append(True)  # Not strict on name

    return results


def check_support_agent():
    """Check Support Agent structure."""
    print("\nSupport Agent:")

    results = []

    # Check 1: create_agent exists
    try:
        from support_agent.agent import create_agent
        print("  [PASS] create_agent() function exists")
        results.append(True)
    except ImportError as e:
        print(f"  [FAIL] Cannot import create_agent: {e}")
        return [False]

    # Check 2: create_agent returns an Agent
    try:
        agent = create_agent()
        from google.adk.agents import Agent
        if isinstance(agent, Agent):
            print("  [PASS] create_agent() returns Agent instance")
            results.append(True)
        else:
            print(f"  [FAIL] create_agent() returns {type(agent).__name__}, expected Agent")
            results.append(False)
    except NotImplementedError:
        print("  [FAIL] create_agent() not implemented yet (raises NotImplementedError)")
        results.append(False)
        return results
    except Exception as e:
        print(f"  [FAIL] create_agent() raised error: {str(e)[:60]}")
        results.append(False)
        return results

    # Check 3: Agent has instruction (should be longer for support agent)
    instruction = getattr(agent, 'instruction', '') or ''
    if isinstance(instruction, str) and len(instruction) > 200:
        print(f"  [PASS] Agent has detailed instruction ({len(instruction)} chars)")
        results.append(True)
    elif isinstance(instruction, str) and len(instruction) > 100:
        print(f"  [WARN] Agent instruction could be more detailed ({len(instruction)} chars)")
        results.append(True)
    else:
        print(f"  [FAIL] Agent instruction too short ({len(instruction) if isinstance(instruction, str) else 'N/A'})")
        results.append(False)

    # Check 4: Agent has McpToolset in tools
    tools = getattr(agent, 'tools', []) or []
    try:
        from google.adk.tools.mcp_tool import McpToolset
        has_toolset = any(isinstance(t, McpToolset) for t in tools)
    except ImportError:
        has_toolset = len(tools) > 0
    if has_toolset:
        print(f"  [PASS] Agent has McpToolset in tools")
        results.append(True)
    else:
        print(f"  [FAIL] Agent tools should contain an McpToolset instance")
        results.append(False)

    # Check 5: Agent name
    name = getattr(agent, 'name', '')
    if name == 'support_agent':
        print(f"  [PASS] Agent name is '{name}'")
        results.append(True)
    else:
        print(f"  [WARN] Agent name is '{name}', expected 'support_agent'")
        results.append(True)

    return results


def check_host_agent():
    """Check Host Agent structure."""
    print("\nHost Agent (Orchestrator):")

    results = []

    # Check 1: create_agent exists
    try:
        from host_agent.agent import create_agent
        print("  [PASS] create_agent() function exists")
        results.append(True)
    except ImportError as e:
        print(f"  [FAIL] Cannot import create_agent: {e}")
        return [False]

    # Check 2: create_agent returns a SequentialAgent
    try:
        agent = create_agent()
        from google.adk.agents import SequentialAgent
        if isinstance(agent, SequentialAgent):
            print("  [PASS] create_agent() returns SequentialAgent instance")
            results.append(True)
        else:
            print(f"  [FAIL] create_agent() returns {type(agent).__name__}, expected SequentialAgent")
            results.append(False)
    except NotImplementedError:
        print("  [FAIL] create_agent() not implemented yet (raises NotImplementedError)")
        results.append(False)
        return results
    except Exception as e:
        print(f"  [FAIL] create_agent() raised error: {str(e)[:60]}")
        results.append(False)
        return results

    # Check 3: Has sub_agents
    sub_agents = getattr(agent, 'sub_agents', []) or []
    if len(sub_agents) >= 2:
        print(f"  [PASS] Agent has {len(sub_agents)} sub-agents (need 2+)")
        results.append(True)
    else:
        print(f"  [FAIL] Agent has {len(sub_agents)} sub-agents (need 2+)")
        results.append(False)

    # Check 4: Sub-agents are RemoteA2aAgent instances
    try:
        from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
        remote_count = sum(1 for sa in sub_agents if isinstance(sa, RemoteA2aAgent))
        if remote_count >= 2:
            print(f"  [PASS] {remote_count} sub-agents are RemoteA2aAgent")
            results.append(True)
        else:
            print(f"  [FAIL] {remote_count} RemoteA2aAgent sub-agents (need 2+)")
            results.append(False)
    except ImportError:
        print("  [WARN] Cannot import RemoteA2aAgent for type checking")
        results.append(True)

    return results


def main():
    """Run all agent structure checks."""
    print("=" * 60)
    print("Part 2: Agent Structure Check")
    print("=" * 60 + "\n")

    all_results = []

    all_results.extend(check_customer_data_agent())
    all_results.extend(check_support_agent())
    all_results.extend(check_host_agent())

    # Summary
    passed = sum(all_results)
    total = len(all_results)

    print("\n" + "=" * 60)
    print(f"Agents: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("\n[PASS] All agent structure checks passed!")
    else:
        print(f"\n[WARN] {total - passed} check(s) failed. Review above.")

    return passed == total


# Support running as pytest
class TestAgents:
    """Pytest-compatible test class for agent structure."""

    def test_customer_data_agent_importable(self):
        """Customer Data Agent create_agent should be importable."""
        from customer_data_agent.agent import create_agent
        assert callable(create_agent)

    def test_support_agent_importable(self):
        """Support Agent create_agent should be importable."""
        from support_agent.agent import create_agent
        assert callable(create_agent)

    def test_host_agent_importable(self):
        """Host Agent create_agent should be importable."""
        from host_agent.agent import create_agent
        assert callable(create_agent)

    def test_customer_data_agent_creates(self):
        """Customer Data Agent should create an Agent instance."""
        from customer_data_agent.agent import create_agent
        from google.adk.agents import Agent
        agent = create_agent()
        assert isinstance(agent, Agent)

    def test_support_agent_creates(self):
        """Support Agent should create an Agent instance."""
        from support_agent.agent import create_agent
        from google.adk.agents import Agent
        agent = create_agent()
        assert isinstance(agent, Agent)

    def test_host_agent_creates_sequential(self):
        """Host Agent should create a SequentialAgent instance."""
        from host_agent.agent import create_agent
        from google.adk.agents import SequentialAgent
        agent = create_agent()
        assert isinstance(agent, SequentialAgent)

    def test_host_agent_has_sub_agents(self):
        """Host Agent should have at least 2 sub-agents."""
        from host_agent.agent import create_agent
        agent = create_agent()
        assert len(agent.sub_agents) >= 2


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
