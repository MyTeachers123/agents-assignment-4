"""
Comprehensive End-to-End Test Scenarios for A2A Multi-Agent System (GIVEN)

Tests all scenarios:
1. Task Allocation
2. Negotiation/Escalation
3. Multi-Step Coordination
4. Simple Queries
5. Complex Multi-Intent Queries

This script runs from the project root directory.
"""

import asyncio
import logging
import os
import re
import sys

# Add agents directory to Python path
agents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents')
sys.path.insert(0, agents_dir)

from run_agents import A2AClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


async def test_scenario(scenario_name: str, query: str, expected_capabilities: list):
    """Test a single scenario."""
    client = A2AClient()

    print("\n" + "="*80)
    print(f"SCENARIO: {scenario_name}")
    print("="*80)
    print(f"Query: {query}")
    print("-"*80)
    print("Expected Capabilities:")
    for cap in expected_capabilities:
        print(f"  - {cap}")
    print("-"*80)

    try:
        response = await client.send_message(
            "http://localhost:10022",  # Host Agent (Orchestrator)
            query
        )

        print("\nRESPONSE:")
        print("-"*80)
        print(response)
        print("-"*80)

        # Verify response quality (whole-word match: 'id' must not match 'provided')
        print("\nVERIFICATION:")
        substantial = len(response) > 50
        relevant = re.search(r"\b(customers?|tickets?|id)\b", response.lower()) is not None
        print(f"  [{'PASS' if substantial else 'FAIL'}] Response has substantial content")
        print(f"  [{'PASS' if relevant else 'FAIL'}] Response contains relevant keywords")

        print("\n" + "="*80)
        return substantial and relevant

    except Exception as e:
        print(f"\n[FAIL] ERROR: {str(e)}")
        print("="*80)
        return False


async def run_all_tests():
    """Run all test scenarios."""

    print("\n" + "="*80)
    print("COMPREHENSIVE A2A MULTI-AGENT SYSTEM TESTING")
    print("="*80 + "\n")

    results = []

    # ========================================================================
    # SCENARIO 1: Simple Query (Single Agent)
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Simple Query - Single Agent",
        query="Get customer information for ID 5",
        expected_capabilities=[
            "Single agent (Customer Data) handles request",
            "Direct MCP call to get customer data",
            "Returns customer details"
        ]
    ))

    await asyncio.sleep(2)

    # ========================================================================
    # SCENARIO 2: Task Allocation (Customer Tier-Based Routing)
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Task Allocation - Customer Tier Recognition",
        query="I need help with my account, customer ID 1. I'm John Doe.",
        expected_capabilities=[
            "Router fetches customer data to understand context",
            "Identifies customer status (active/disabled)",
            "Routes to appropriate support level",
            "Checks for existing tickets",
            "Provides personalized assistance"
        ]
    ))

    await asyncio.sleep(2)

    # ========================================================================
    # SCENARIO 3: Coordinated Query (Data + Support)
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Coordinated Query - Multi-Agent Collaboration",
        query="I'm customer 2 (Jane Smith) and I need help checking my ticket status and getting support",
        expected_capabilities=[
            "Customer Data Agent fetches customer info",
            "Customer Data Agent retrieves ticket history",
            "Support Agent provides guidance based on data",
            "Coordinated response with both data and support"
        ]
    ))

    await asyncio.sleep(2)

    # ========================================================================
    # SCENARIO 4: Complex Query (Multi-Step Coordination)
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Multi-Step Coordination - Complex Data Query",
        query="Show me all customers who have open high-priority tickets",
        expected_capabilities=[
            "Router decomposes task",
            "Filters tickets by status=open and priority=high",
            "Fetches customer details for each ticket",
            "Aggregates and formats results",
            "Returns comprehensive report"
        ]
    ))

    await asyncio.sleep(2)

    # ========================================================================
    # SCENARIO 5: Negotiation/Escalation (Multiple Intents)
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Negotiation/Escalation - Multiple Intents",
        query="I want to cancel my subscription but I'm also having billing issues. Customer ID 7.",
        expected_capabilities=[
            "Detects multiple intents (cancellation + billing)",
            "Router coordinates between agents",
            "Fetches customer billing context",
            "Support agent addresses both concerns",
            "Escalation awareness for urgent issues"
        ]
    ))

    await asyncio.sleep(2)

    # ========================================================================
    # SCENARIO 6: Urgency Detection & Escalation
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Urgency Detection - Immediate Escalation",
        query="URGENT! I've been charged twice for the same transaction! Customer ID 3. Please refund immediately!",
        expected_capabilities=[
            "Detects urgency keywords (URGENT, immediately)",
            "Identifies billing issue type",
            "Fetches customer record and existing tickets (no transaction data exists)",
            "Creates high-priority ticket",
            "Provides immediate escalation path",
            "Shows ticket ID for tracking"
        ]
    ))

    await asyncio.sleep(2)

    # ========================================================================
    # SCENARIO 7: Multi-Intent Parallel Tasks
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Multi-Intent - Parallel Task Execution",
        query="I'm customer 5 (Charlie Brown). Please show me my ticket history and also tell me how to reset my password",
        expected_capabilities=[
            "Identifies two distinct requests",
            "Fetches ticket history from data agent",
            "Provides password reset instructions from support",
            "Combines both responses coherently"
        ]
    ))

    await asyncio.sleep(2)

    # ========================================================================
    # SCENARIO 8: Cross-Agent Data Dependency
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Cross-Agent Dependency - Context Passing",
        query="I can't login. Can you check if I have any open tickets about this? I'm customer 1.",
        expected_capabilities=[
            "Fetches customer information",
            "Searches for login-related tickets",
            "Support agent uses ticket context for troubleshooting",
            "Provides solutions based on ticket history",
            "Creates new ticket if needed"
        ]
    ))

    await asyncio.sleep(2)

    # ========================================================================
    # SCENARIO 9: Data Aggregation & Analysis
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Data Aggregation - Statistical Analysis",
        query="Give me statistics on customer tickets - how many are open, in progress, and resolved?",
        expected_capabilities=[
            "Calls ticket statistics MCP tool",
            "Aggregates data across all tickets",
            "Provides breakdown by status",
            "May include priority distribution",
            "Formatted statistical report"
        ]
    ))

    await asyncio.sleep(2)

    # ========================================================================
    # SCENARIO 10: Customer Search & Support
    # ========================================================================
    results.append(await test_scenario(
        scenario_name="Customer Search - Ticket Resolution Flow",
        query="Find all tickets about password reset issues and help me understand the common solutions",
        expected_capabilities=[
            "Searches tickets by keyword (password reset)",
            "Analyzes common patterns",
            "Support agent provides standard solutions",
            "May identify customers needing follow-up"
        ]
    ))

    # ========================================================================
    # RESULTS SUMMARY
    # ========================================================================
    print("\n\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80 + "\n")

    passed = sum(results)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n[PASS] ALL TESTS PASSED! Multi-agent system is working end-to-end!")
    else:
        print(f"\n[WARN] {total - passed} test(s) failed. Review logs above.")

    print("\n" + "="*80 + "\n")
    return passed == total


async def verify_agent_availability():
    """Verify all agents are running."""
    print("\nVerifying agent availability...")
    print("-"*80)

    client = A2AClient()
    agents = [
        ("Customer Data Agent", "http://localhost:10020"),
        ("Support Agent", "http://localhost:10021"),
        ("Host Agent (Orchestrator)", "http://localhost:10022")
    ]

    all_available = True
    for name, url in agents:
        try:
            # Try to fetch agent card
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as http_client:
                response = await http_client.get(f"{url}/.well-known/agent-card.json")
                if response.status_code == 200:
                    print(f"  [OK] {name} is running at {url}")
                else:
                    print(f"  [FAIL] {name} returned status {response.status_code}")
                    all_available = False
        except Exception as e:
            print(f"  [FAIL] {name} is NOT available at {url}: {str(e)}")
            all_available = False

    print("-"*80)

    if not all_available:
        print("\n[ERROR] Not all agents are running!")
        print("Please start the agents first:")
        print("  From the project root directory:")
        print("  python run_agents.py --mode start")
        return False

    print("[OK] All agents are available!\n")
    return True


async def main():
    """Main test execution."""
    # Verify agents are running
    if not await verify_agent_availability():
        return False

    # Run all test scenarios
    return await run_all_tests()


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(main()) else 1)
