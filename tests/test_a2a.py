"""
Test harness for Part 3 & 4: A2A Integration

Verifies A2A-specific components:
  - AgentCards are properly defined
  - RemoteA2aAgent is used correctly
  - create_all_agents factory works
  - Agent card URLs are correctly configured

Usage:
    python -m pytest tests/test_a2a.py -v
    python -m tests.test_a2a
"""

import inspect
import sys
import os

# Add agents directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agents'))


def check_agent_cards():
    """Check that all AgentCard creation functions work."""
    print("AgentCard Definitions:")

    results = []

    card_functions = [
        ("create_customer_data_agent_card", "Customer Data Agent"),
        ("create_support_agent_card", "Support Agent"),
        ("create_host_agent_card", "Customer Support Host Agent"),
    ]

    for func_name, expected_name in card_functions:
        try:
            from create_agents import (
                create_customer_data_agent_card,
                create_support_agent_card,
                create_host_agent_card,
            )

            func = {
                "create_customer_data_agent_card": create_customer_data_agent_card,
                "create_support_agent_card": create_support_agent_card,
                "create_host_agent_card": create_host_agent_card,
            }[func_name]

            card = func()

            # Check card has required fields
            checks_passed = True

            if not hasattr(card, 'name') or not card.name:
                print(f"  [FAIL] {func_name}: missing name")
                checks_passed = False

            if not hasattr(card, 'url') or not card.url:
                print(f"  [FAIL] {func_name}: missing url")
                checks_passed = False

            if not hasattr(card, 'description') or not card.description:
                print(f"  [FAIL] {func_name}: missing description")
                checks_passed = False

            if not hasattr(card, 'skills') or not card.skills:
                print(f"  [FAIL] {func_name}: missing skills")
                checks_passed = False

            if checks_passed:
                print(f"  [PASS] {func_name} -> '{card.name}'")
                # Check skills have examples
                for skill in card.skills:
                    examples = getattr(skill, 'examples', []) or []
                    if len(examples) >= 2:
                        print(f"         Skill '{skill.name}' has {len(examples)} examples")
                    else:
                        print(f"         [WARN] Skill '{skill.name}' has only {len(examples)} examples")

            results.append(checks_passed)

        except NotImplementedError:
            print(f"  [FAIL] {func_name} not implemented yet")
            results.append(False)
        except ImportError as e:
            print(f"  [FAIL] Cannot import {func_name}: {e}")
            results.append(False)
        except Exception as e:
            print(f"  [FAIL] {func_name} raised error: {str(e)[:60]}")
            results.append(False)

    return results


def check_remote_a2a_usage():
    """Check that RemoteA2aAgent is used in host_agent."""
    print("\nRemoteA2aAgent Usage:")

    results = []

    # Check source code for RemoteA2aAgent usage
    try:
        agent_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'agents', 'host_agent', 'agent.py'
        )
        with open(agent_file, 'r') as f:
            source = f.read()

        # Check imports
        if 'RemoteA2aAgent' in source:
            print("  [PASS] RemoteA2aAgent is imported")
            results.append(True)
        else:
            print("  [FAIL] RemoteA2aAgent not imported in host_agent/agent.py")
            results.append(False)

        # Check AGENT_CARD_WELL_KNOWN_PATH usage
        if 'AGENT_CARD_WELL_KNOWN_PATH' in source:
            print("  [PASS] AGENT_CARD_WELL_KNOWN_PATH is used")
            results.append(True)
        else:
            print("  [FAIL] AGENT_CARD_WELL_KNOWN_PATH not used")
            results.append(False)

        # Check a2a_compat import
        if 'a2a_compat' in source:
            print("  [PASS] A2A compatibility patch is imported")
            results.append(True)
        else:
            print("  [FAIL] A2A compatibility patch not imported")
            results.append(False)

        # Check SequentialAgent
        if 'SequentialAgent' in source:
            print("  [PASS] SequentialAgent is used")
            results.append(True)
        else:
            print("  [FAIL] SequentialAgent not used")
            results.append(False)

    except FileNotFoundError:
        print("  [FAIL] host_agent/agent.py not found")
        results.extend([False, False, False, False])

    return results


def check_factory_function():
    """Check create_all_agents factory function."""
    print("\nFactory Function (create_all_agents):")

    results = []

    try:
        from create_agents import create_all_agents
        config = create_all_agents()

        # Check it returns a dict
        if isinstance(config, dict):
            print("  [PASS] create_all_agents() returns dict")
            results.append(True)
        else:
            print(f"  [FAIL] create_all_agents() returns {type(config).__name__}")
            results.append(False)
            return results

        # Check required keys
        required_keys = ['customer_data', 'support', 'host']
        for key in required_keys:
            if key in config:
                print(f"  [PASS] '{key}' key present")
                results.append(True)

                # Check inner structure
                inner = config[key]
                if 'agent' in inner and 'card' in inner and 'port' in inner:
                    print(f"         Has agent, card, port")
                else:
                    missing = [k for k in ['agent', 'card', 'port'] if k not in inner]
                    print(f"         [WARN] Missing keys: {missing}")
            else:
                print(f"  [FAIL] '{key}' key missing")
                results.append(False)

        # Check ports
        expected_ports = {'customer_data': 10020, 'support': 10021, 'host': 10022}
        for key, expected_port in expected_ports.items():
            if key in config and config[key].get('port') == expected_port:
                print(f"  [PASS] {key} port is {expected_port}")
                results.append(True)
            elif key in config:
                actual = config[key].get('port')
                print(f"  [WARN] {key} port is {actual}, expected {expected_port}")
                results.append(True)

    except NotImplementedError:
        print("  [FAIL] create_all_agents() not implemented yet")
        results.append(False)
    except ImportError as e:
        print(f"  [FAIL] Cannot import create_all_agents: {e}")
        results.append(False)
    except Exception as e:
        print(f"  [FAIL] create_all_agents() raised error: {str(e)[:60]}")
        results.append(False)

    return results


def check_agent_card_urls():
    """Check that agent card URLs are correctly configured."""
    print("\nAgent Card URL Configuration:")

    results = []

    try:
        from shared.agents_config import (
            CUSTOMER_DATA_AGENT_URL,
            SUPPORT_AGENT_URL,
            HOST_AGENT_URL,
            CUSTOMER_DATA_AGENT_PORT,
            SUPPORT_AGENT_PORT,
            HOST_AGENT_PORT,
        )

        urls = [
            ("CUSTOMER_DATA_AGENT_URL", CUSTOMER_DATA_AGENT_URL, CUSTOMER_DATA_AGENT_PORT),
            ("SUPPORT_AGENT_URL", SUPPORT_AGENT_URL, SUPPORT_AGENT_PORT),
            ("HOST_AGENT_URL", HOST_AGENT_URL, HOST_AGENT_PORT),
        ]

        for name, url, port in urls:
            if f":{port}" in url:
                print(f"  [PASS] {name} = {url}")
                results.append(True)
            else:
                print(f"  [FAIL] {name} = {url} (expected port {port})")
                results.append(False)

    except ImportError as e:
        print(f"  [FAIL] Cannot import from agents_config: {e}")
        results.extend([False, False, False])

    return results


def main():
    """Run all A2A integration checks."""
    print("=" * 60)
    print("Part 3 & 4: A2A Integration Check")
    print("=" * 60 + "\n")

    all_results = []

    all_results.extend(check_agent_card_urls())
    all_results.extend(check_remote_a2a_usage())
    all_results.extend(check_agent_cards())
    all_results.extend(check_factory_function())

    # Summary
    passed = sum(all_results)
    total = len(all_results)

    print("\n" + "=" * 60)
    print(f"A2A Integration: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("\n[PASS] All A2A integration checks passed!")
    else:
        print(f"\n[WARN] {total - passed} check(s) failed. Review above.")

    return passed == total


# Support running as pytest
class TestA2A:
    """Pytest-compatible test class for A2A integration."""

    def test_agent_config_importable(self):
        """Agent config should be importable with correct URLs."""
        from shared.agents_config import (
            CUSTOMER_DATA_AGENT_URL,
            SUPPORT_AGENT_URL,
            HOST_AGENT_URL,
        )
        assert "10020" in CUSTOMER_DATA_AGENT_URL
        assert "10021" in SUPPORT_AGENT_URL
        assert "10022" in HOST_AGENT_URL

    def test_a2a_compat_importable(self):
        """A2A compatibility patch should be importable."""
        from shared import a2a_compat
        assert hasattr(a2a_compat, 'A2ACardResolver')

    def test_host_agent_uses_remote_a2a(self):
        """Host agent source should use RemoteA2aAgent."""
        agent_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'agents', 'host_agent', 'agent.py'
        )
        with open(agent_file, 'r') as f:
            source = f.read()
        assert 'RemoteA2aAgent' in source
        assert 'SequentialAgent' in source

    def test_agent_cards(self):
        """All three AgentCards build with name, url, description and skills with examples."""
        from create_agents import (
            create_customer_data_agent_card,
            create_support_agent_card,
            create_host_agent_card,
        )
        for fn in (create_customer_data_agent_card, create_support_agent_card, create_host_agent_card):
            card = fn()
            assert card.name and card.url and card.description and card.skills, fn.__name__
            assert all(skill.examples for skill in card.skills), fn.__name__

    def test_create_all_agents_importable(self):
        """create_all_agents should be importable."""
        from create_agents import create_all_agents
        assert callable(create_all_agents)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
