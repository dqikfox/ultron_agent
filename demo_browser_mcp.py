"""
Quick Browser MCP Demo
Demonstrates Browser MCP capabilities with ULTRON Agent
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.mcp_integration_tool import MCPIntegrationTool


def demo_browser_mcp():
    """Demo Browser MCP functionality"""
    print("=" * 70)
    print("🌐 Browser MCP Demo for ULTRON Agent")
    print("=" * 70)
    print()

    # Initialize MCP Integration
    mcp = MCPIntegrationTool()

    # Step 1: Show available servers
    print("📋 Step 1: Available MCP Servers")
    print("-" * 70)
    result = mcp.execute("list mcp servers")
    print(result)
    print()

    # Step 2: Start Browser MCP
    print("🚀 Step 2: Starting Browser MCP Server")
    print("-" * 70)
    print("⏳ Starting @browsermcp/mcp@latest via npx...")
    result = mcp.execute("start mcp browsermcp")
    print(result)
    print()

    # Step 3: Example browser commands
    print("💡 Step 3: Example Browser Commands You Can Use")
    print("-" * 70)
    examples = [
        "Navigate to https://example.com",
        "Click the login button",
        "Fill the search box with 'Python tutorials'",
        "Take a screenshot of the dashboard",
        "Extract all links from the page",
        "Get the page title and main content",
        "Scroll to the bottom of the page",
        "Submit the contact form",
    ]

    for i, cmd in enumerate(examples, 1):
        print(f"  {i}. {cmd}")
    print()

    # Step 4: Demo navigation (if server started)
    if "started successfully" in result.lower() or "already running" in result.lower():
        print("🌐 Step 4: Testing Browser Navigation")
        print("-" * 70)
        print("📍 Navigating to example.com...")
        nav_result = mcp.execute("browser navigate to https://example.com")
        print(nav_result)
        print()

        # Step 5: Stop server
        print("🛑 Step 5: Stopping Browser MCP Server")
        print("-" * 70)
        stop_result = mcp.execute("stop mcp browsermcp")
        print(stop_result)
    else:
        print("⚠️  Browser MCP server not started - skipping navigation test")
        print("   Check Node.js/npx installation")

    print()
    print("=" * 70)
    print("📚 Next Steps:")
    print("=" * 70)
    print("1. Read BROWSER_MCP_GUIDE.md for full documentation")
    print("2. Start ULTRON: .\\run.bat")
    print("3. Say: 'Start browser MCP and open github.com'")
    print("4. Visit: https://docs.browsermcp.io/ for API docs")
    print()
    print("🎯 Browser MCP is ready to use in ULTRON Agent!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        demo_browser_mcp()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
