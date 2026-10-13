"""
Test harness for Part 1: McpToolset Configuration

Verifies that McpToolset factory functions are properly structured:
  - Toolset factories return McpToolset instances
  - Connection params use correct SSE URL
  - tool_filter lists are non-empty and contain valid tool names
  - Customer data toolset includes core tools
  - Support toolset excludes admin/destructive tools

Usage:
    python -m pytest tests/test_mcp_toolset.py -v
    python -m tests.test_mcp_toolset
"""

import inspect
import sys
import os

# Add agents directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agents'))


# All 15 tools available on the MCP server
ALL_MCP_TOOL_NAMES = [
    "get_customer", "list_customers", "add_customer", "update_customer",
    "disable_customer", "activate_customer",
    "get_ticket", "list_tickets", "create_ticket", "update_ticket_status",
    "update_ticket_priority", "delete_ticket",
    "get_ticket_stats", "get_customer_stats", "search_tickets",
]

# Tools that the support agent should NOT have access to
ADMIN_TOOLS = ["disable_customer", "activate_customer", "delete_ticket",
               "add_customer", "update_customer"]

# Core tools the customer data toolset must include
CUSTOMER_DATA_CORE_TOOLS = [
    "get_customer", "list_customers", "get_ticket", "list_tickets",
    "create_ticket", "get_ticket_stats", "get_customer_stats",
]


def check_imports():
    """Check that McpToolset factories are importable."""
    try:
        from shared.mcp_toolset import create_customer_data_toolset, create_support_toolset
        print("  [PASS] Toolset factories importable")
        return True
    except ImportError as e:
        print(f"  [FAIL] Cannot import toolset factories: {e}")
        return False


def check_customer_data_toolset():
    """Check Customer Data Toolset structure."""
    try:
        from shared.mcp_toolset import create_customer_data_toolset
        from google.adk.tools.mcp_tool import McpToolset
    except ImportError as e:
        print(f"  [FAIL] Import error: {e}")
        return False

    try:
        toolset = create_customer_data_toolset()
    except NotImplementedError:
        print("  [FAIL] create_customer_data_toolset() not implemented (raises NotImplementedError)")
        return False
    except Exception as e:
        print(f"  [FAIL] create_customer_data_toolset() raised: {str(e)[:80]}")
        return False

    if not isinstance(toolset, McpToolset):
        print(f"  [FAIL] Expected McpToolset, got {type(toolset).__name__}")
        return False
    print("  [PASS] Returns McpToolset instance")

    # Check tool_filter (google-adk 2.x stores it as the public `tool_filter`)
    tool_filter = getattr(toolset, 'tool_filter', getattr(toolset, '_tool_filter', None))
    if tool_filter is None:
        print("  [PASS] No tool_filter: all 15 MCP tools exposed (full access)")
    elif isinstance(tool_filter, list):
        if len(tool_filter) == 0:
            print("  [FAIL] tool_filter is empty")
            return False
        print(f"  [PASS] tool_filter has {len(tool_filter)} tools")

        # Verify core tools are included
        missing = [t for t in CUSTOMER_DATA_CORE_TOOLS if t not in tool_filter]
        if missing:
            print(f"  [WARN] Missing core tools: {', '.join(missing)}")
        else:
            print("  [PASS] All core customer data tools included")

        # Verify all filter names are valid MCP tool names
        invalid = [t for t in tool_filter if t not in ALL_MCP_TOOL_NAMES]
        if invalid:
            print(f"  [FAIL] Invalid tool names in filter: {', '.join(invalid)}")
            return False
        print("  [PASS] All tool names are valid")

    return True


def check_support_toolset():
    """Check Support Toolset structure."""
    try:
        from shared.mcp_toolset import create_support_toolset
        from google.adk.tools.mcp_tool import McpToolset
    except ImportError as e:
        print(f"  [FAIL] Import error: {e}")
        return False

    try:
        toolset = create_support_toolset()
    except NotImplementedError:
        print("  [FAIL] create_support_toolset() not implemented (raises NotImplementedError)")
        return False
    except Exception as e:
        print(f"  [FAIL] create_support_toolset() raised: {str(e)[:80]}")
        return False

    if not isinstance(toolset, McpToolset):
        print(f"  [FAIL] Expected McpToolset, got {type(toolset).__name__}")
        return False
    print("  [PASS] Returns McpToolset instance")

    # Check tool_filter (google-adk 2.x stores it as the public `tool_filter`)
    tool_filter = getattr(toolset, 'tool_filter', getattr(toolset, '_tool_filter', None))
    if tool_filter is None:
        print("  [FAIL] Support toolset has no tool_filter (admin tools would be exposed)")
        return False
    elif isinstance(tool_filter, list):
        if len(tool_filter) == 0:
            print("  [FAIL] tool_filter is empty")
            return False
        print(f"  [PASS] tool_filter has {len(tool_filter)} tools")

        # Verify admin tools are excluded
        included_admin = [t for t in ADMIN_TOOLS if t in tool_filter]
        if included_admin:
            print(f"  [FAIL] Admin tools should be excluded: {', '.join(included_admin)}")
            return False
        print("  [PASS] Admin/destructive tools excluded")

        # Verify all filter names are valid MCP tool names
        invalid = [t for t in tool_filter if t not in ALL_MCP_TOOL_NAMES]
        if invalid:
            print(f"  [FAIL] Invalid tool names in filter: {', '.join(invalid)}")
            return False
        print("  [PASS] All tool names are valid")

    return True


def check_sse_url():
    """Check that MCP_SSE_URL is correctly configured."""
    try:
        from shared.mcp_toolset import MCP_SSE_URL
        if "/sse" in MCP_SSE_URL:
            print(f"  [PASS] MCP_SSE_URL ends with /sse: {MCP_SSE_URL}")
            return True
        else:
            print(f"  [FAIL] MCP_SSE_URL missing /sse suffix: {MCP_SSE_URL}")
            return False
    except ImportError as e:
        print(f"  [FAIL] Cannot import MCP_SSE_URL: {e}")
        return False


def main():
    """Run all McpToolset checks."""
    print("=" * 60)
    print("Part 1: McpToolset Configuration Check")
    print("=" * 60)

    results = []

    print("\nCheck 1: Imports")
    results.append(check_imports())

    print("\nCheck 2: SSE URL Configuration")
    results.append(check_sse_url())

    print("\nCheck 3: Customer Data Toolset")
    results.append(check_customer_data_toolset())

    print("\nCheck 4: Support Toolset")
    results.append(check_support_toolset())

    # Summary
    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 60)
    print(f"McpToolset: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("\n[PASS] All McpToolset checks passed!")
    else:
        print(f"\n[WARN] {total - passed} check(s) failed. Review above.")

    return passed == total


# Support running as pytest
class TestMcpToolset:
    """Pytest-compatible test class for McpToolset configuration."""

    def test_imports(self):
        """Toolset factories should be importable."""
        from shared.mcp_toolset import create_customer_data_toolset, create_support_toolset
        assert callable(create_customer_data_toolset)
        assert callable(create_support_toolset)

    def test_sse_url(self):
        """MCP_SSE_URL should point to the SSE endpoint."""
        from shared.mcp_toolset import MCP_SSE_URL
        assert "/sse" in MCP_SSE_URL, f"MCP_SSE_URL missing /sse: {MCP_SSE_URL}"

    def test_customer_data_toolset_type(self):
        """Customer data toolset should return McpToolset."""
        from shared.mcp_toolset import create_customer_data_toolset
        from google.adk.tools.mcp_tool import McpToolset
        toolset = create_customer_data_toolset()
        assert isinstance(toolset, McpToolset)

    def test_support_toolset_type(self):
        """Support toolset should return McpToolset."""
        from shared.mcp_toolset import create_support_toolset
        from google.adk.tools.mcp_tool import McpToolset
        toolset = create_support_toolset()
        assert isinstance(toolset, McpToolset)

    def test_support_toolset_filter(self):
        """Support toolset must have a tool_filter that excludes admin tools."""
        from shared.mcp_toolset import create_support_toolset
        toolset = create_support_toolset()
        tool_filter = getattr(toolset, 'tool_filter', getattr(toolset, '_tool_filter', None))
        assert isinstance(tool_filter, list) and tool_filter, "support toolset needs a non-empty tool_filter list"
        assert not [t for t in ADMIN_TOOLS if t in tool_filter], "admin tools must be excluded"
        assert not [t for t in tool_filter if t not in ALL_MCP_TOOL_NAMES], "unknown tool names"

    def test_customer_data_toolset_filter(self):
        """Customer data toolset: no filter (all tools) or a list of valid tool names."""
        from shared.mcp_toolset import create_customer_data_toolset
        toolset = create_customer_data_toolset()
        tool_filter = getattr(toolset, 'tool_filter', getattr(toolset, '_tool_filter', None))
        if tool_filter is not None:
            assert isinstance(tool_filter, list) and tool_filter
            assert not [t for t in tool_filter if t not in ALL_MCP_TOOL_NAMES], "unknown tool names"

    def test_full_toolset_reference(self):
        """Full toolset (reference) should return McpToolset."""
        from shared.mcp_toolset import create_full_toolset
        from google.adk.tools.mcp_tool import McpToolset
        toolset = create_full_toolset()
        assert isinstance(toolset, McpToolset)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
