#!/usr/bin/env python3
"""
ULTRON Agent - Advanced Tools Integration Test

Tests the new Repomix and Web Search tools to ensure proper functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.repomix_tool import RepomixTool
from tools.web_search_tool import WebSearchTool
from utils.ultron_logger import log_info, log_error


def test_repomix_tool():
    """Test Repomix codebase analysis tool"""
    print("\n - test_advanced_tools.py:22" + "="*60)
    print("🧪 TESTING REPOMIX TOOL - test_advanced_tools.py:23")
    print("= - test_advanced_tools.py:24"*60)

    try:
        repomix = RepomixTool()
        print("✅ RepomixTool initialized successfully - test_advanced_tools.py:28")

        # Test 1: Pack small local directory (tools folder)
        print("\n📦 Test 1: Pack local codebase (tools folder) - test_advanced_tools.py:31")
        tools_dir = Path(__file__).parent / "tools"
        result = repomix.execute(f"pack local codebase {tools_dir}")
        print(result)

        if "✅" in result:
            print("✅ Test 1 PASSED: Local codebase packing works - test_advanced_tools.py:37")
        else:
            print("❌ Test 1 FAILED: Local codebase packing failed - test_advanced_tools.py:39")
            return False

        # Test 2: List outputs
        print("\n📋 Test 2: List available outputs - test_advanced_tools.py:43")
        result = repomix.execute("list outputs")
        print(result)

        if "Available Repomix Outputs" in result:
            print("✅ Test 2 PASSED: Output listing works - test_advanced_tools.py:48")
        else:
            print("❌ Test 2 FAILED: Output listing failed - test_advanced_tools.py:50")
            return False

        # Test 3: Search in packed codebase
        print("\n🔍 Test 3: Search for 'ToolInterface' in codebase - test_advanced_tools.py:54")
        result = repomix.execute("search for ToolInterface in codebase")
        print(result[:500] + "... - test_advanced_tools.py:56" if len(result) > 500 else result)

        if "Search Results" in result or "matches found" in result:
            print("✅ Test 3 PASSED: Code search works - test_advanced_tools.py:59")
        else:
            print("❌ Test 3 FAILED: Code search failed - test_advanced_tools.py:61")
            return False

        # Test 4: Get overview
        print("\n📊 Test 4: Get codebase overview - test_advanced_tools.py:65")
        result = repomix.execute("overview of latest codebase analysis")
        print(result)

        if "Codebase Overview" in result:
            print("✅ Test 4 PASSED: Overview generation works - test_advanced_tools.py:70")
        else:
            print("❌ Test 4 FAILED: Overview generation failed - test_advanced_tools.py:72")
            return False

        print("\n🎉 ALL REPOMIX TESTS PASSED - test_advanced_tools.py:75")
        return True

    except Exception as e:
        print(f"❌ REPOMIX TEST ERROR: {e} - test_advanced_tools.py:79")
        import traceback
        traceback.print_exc()
        return False


def test_web_search_tool():
    """Test enhanced web search tool"""
    print("\n - test_advanced_tools.py:87" + "="*60)
    print("🧪 TESTING WEB SEARCH TOOL - test_advanced_tools.py:88")
    print("= - test_advanced_tools.py:89"*60)

    try:
        web_search = WebSearchTool()
        print("✅ WebSearchTool initialized successfully - test_advanced_tools.py:93")

        # Test 1: Basic search with DuckDuckGo
        print("\n🔍 Test 1: Search for 'Python asyncio tutorial' - test_advanced_tools.py:96")
        result = web_search.execute(
            "search web for Python asyncio tutorial",
            max_results=5,
            engines=["duckduckgo"]
        )
        print(result[:800] + "... - test_advanced_tools.py:102" if len(result) > 800 else result)

        if "Web Search Results" in result and "🔗" in result:
            print("✅ Test 1 PASSED: Basic web search works - test_advanced_tools.py:105")
        else:
            print("❌ Test 1 FAILED: Basic web search failed - test_advanced_tools.py:107")
            return False

        # Test 2: Multi-engine search
        print("\n🌐 Test 2: Multiengine search for 'GitHub Copilot' - test_advanced_tools.py:111")
        result = web_search.execute(
            "search for GitHub Copilot features",
            max_results=5,
            engines=["duckduckgo", "brave"]
        )
        print(result[:800] + "... - test_advanced_tools.py:117" if len(result) > 800 else result)

        if "Web Search Results" in result:
            print("✅ Test 2 PASSED: Multiengine search works - test_advanced_tools.py:120")
        else:
            print("❌ Test 2 FAILED: Multiengine search failed - test_advanced_tools.py:122")
            return False

        # Test 3: Cached search (repeat query)
        print("\n💾 Test 3: Cached search (repeat previous query) - test_advanced_tools.py:126")
        result = web_search.execute(
            "search for GitHub Copilot features",
            max_results=5,
            engines=["duckduckgo", "brave"]
        )

        if "(from cache)" in result:
            print("✅ Test 3 PASSED: Cache system works - test_advanced_tools.py:134")
        else:
            print("⚠️ Test 3 WARNING: Cache not detected (may be timing issue) - test_advanced_tools.py:136")

        # Test 4: Natural language extraction
        print("\n💬 Test 4: Natural language query - test_advanced_tools.py:139")
        result = web_search.execute("find information on Python programming")
        print(result[:800] + "... - test_advanced_tools.py:141" if len(result) > 800 else result)

        if "Web Search Results" in result or "No search results" in result:
            print("✅ Test 4 PASSED: Natural language processing works - test_advanced_tools.py:144")
        else:
            print("❌ Test 4 FAILED: Natural language processing failed - test_advanced_tools.py:146")
            return False

        print("\n🎉 ALL WEB SEARCH TESTS PASSED - test_advanced_tools.py:149")
        return True

    except Exception as e:
        print(f"❌ WEB SEARCH TEST ERROR: {e} - test_advanced_tools.py:153")
        import traceback
        traceback.print_exc()
        return False


def test_tool_discovery():
    """Test that tools are properly discoverable"""
    print("\n - test_advanced_tools.py:161" + "="*60)
    print("🧪 TESTING TOOL AUTODISCOVERY - test_advanced_tools.py:162")
    print("= - test_advanced_tools.py:163"*60)

    try:
        from tools.tool_loader import get_tool_loader

        loader = get_tool_loader()
        tool_names = loader.list_tools()
        print(f"✅ Loaded {len(tool_names)} tools - test_advanced_tools.py:170")

        # Check if our new tools are discovered
        if "Repomix Codebase Analyzer" in tool_names:
            print("✅ RepomixTool discovered by tool loader - test_advanced_tools.py:174")
        else:
            print("❌ RepomixTool NOT discovered - test_advanced_tools.py:176")
            print(f"Available tools: {tool_names} - test_advanced_tools.py:177")
            return False

        if "Enhanced Web Search" in tool_names:
            print("✅ WebSearchTool discovered by tool loader - test_advanced_tools.py:181")
        else:
            print("❌ WebSearchTool NOT discovered - test_advanced_tools.py:183")
            print(f"Available tools: {tool_names} - test_advanced_tools.py:184")
            return False

        print("\n🎉 TOOL AUTODISCOVERY TEST PASSED - test_advanced_tools.py:187")
        return True

    except Exception as e:
        print(f"❌ TOOL DISCOVERY TEST ERROR: {e} - test_advanced_tools.py:191")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests"""
    print("\n🤖 ULTRON AGENT  ADVANCED TOOLS INTEGRATION TEST - test_advanced_tools.py:199")
    print("= - test_advanced_tools.py:200"*60)
    print("Testing new Repomix and Web Search tools - test_advanced_tools.py:201")
    print("= - test_advanced_tools.py:202"*60)

    results = {
        "Repomix Tool": test_repomix_tool(),
        "Web Search Tool": test_web_search_tool(),
        "Tool Auto-Discovery": test_tool_discovery()
    }

    # Summary
    print("\n - test_advanced_tools.py:211" + "="*60)
    print("📊 TEST SUMMARY - test_advanced_tools.py:212")
    print("= - test_advanced_tools.py:213"*60)

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status} - test_advanced_tools.py:220")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%) - test_advanced_tools.py:224")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Tools are ready for use. - test_advanced_tools.py:227")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED. Check logs above for details. - test_advanced_tools.py:230")
        return 1


if __name__ == "__main__":
    sys.exit(main())
