"""
Test Browser MCP Integration

Quick test to verify Browser MCP server is working with ULTRON Agent.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.browser_mcp_tool import BrowserMCPTool


async def test_browser_mcp():
    """Test Browser MCP functionality"""
    print("🌐 Testing Browser MCP Integration")
    print("=" * 50)
    
    # Initialize tool
    browser_tool = BrowserMCPTool()
    
    # Test 1: Check if tool matches browser commands
    test_commands = [
        "navigate to google.com",
        "click the search button", 
        "take a screenshot",
        "scrape this page",
        "fill the form with data"
    ]
    
    print("\n📝 Testing command matching:")
    for cmd in test_commands:
        matches = browser_tool.match(cmd)
        status = "✅" if matches else "❌"
        print(f"  {status} '{cmd}' -> {matches}")
    
    # Test 2: Check MCP server availability
    print("\n🔧 Testing MCP server:")
    try:
        # Check if npx is available
        result = subprocess.run(
            ["npx", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"  ✅ npx available: {result.stdout.strip()}")
            
            # Check if browser MCP package exists
            result = subprocess.run(
                ["npx", "-y", "@anthropic-ai/mcp-server-browser", "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ Browser MCP server package available")
            else:
                print("  ❌ Browser MCP server package not found")
                print(f"     Error: {result.stderr}")
                
        else:
            print("  ❌ npx not available")
            
    except Exception as e:
        print(f"  ❌ Error checking MCP server: {str(e)}")
    
    # Test 3: Test tool execution (without actually starting browser)
    print("\n🚀 Testing tool execution:")
    try:
        # Test with a simple command
        result = await browser_tool.execute("navigate to example.com")
        print(f"  ✅ Tool execution result: {result}")
        
    except Exception as e:
        print(f"  ❌ Tool execution failed: {str(e)}")
    
    # Test 4: Check Continue configuration
    print("\n⚙️  Checking Continue configuration:")
    continue_config = project_root / ".continue" / "config.yaml"
    
    if continue_config.exists():
        with open(continue_config, 'r') as f:
            config_content = f.read()
            
        if "mcp-server-browser" in config_content:
            print("  ✅ Browser MCP configured in Continue")
        else:
            print("  ❌ Browser MCP not found in Continue config")
    else:
        print("  ❌ Continue config file not found")
    
    print("\n" + "=" * 50)
    print("🎯 Browser MCP Integration Test Complete")
    
    # Cleanup
    await browser_tool.stop_mcp_server()


if __name__ == "__main__":
    asyncio.run(test_browser_mcp())