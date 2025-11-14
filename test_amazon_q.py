#!/usr/bin/env python3
"""
Simple Amazon Q Auto-Run Test
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    """Simple test function"""
    print("[AMAZON Q] Auto-Run Test Starting...")
    
    try:
        # Test Amazon Q integration tool
        from tools.amazon_q_integration_tool import AmazonQIntegrationTool
        
        tool = AmazonQIntegrationTool()
        print("[SUCCESS] Amazon Q Integration Tool loaded")
        print(f"Tool Name: {tool.name}")
        
        # Test help command
        help_result = tool.execute("help")
        print(f"[HELP] {help_result}")
        
        # Test startup info
        startup_result = tool.execute("startup")
        print(f"[STARTUP] {startup_result}")
        
        # Test Tor search tool
        print("[TEST] Testing Tor search tool...")
        try:
            from tools.tor_search_tool import TorSearchTool
            tor_tool = TorSearchTool()
            print("[SUCCESS] Tor search tool loaded")
        except Exception as e:
            print(f"[WARNING] Tor tool issue: {e}")
        
        # Test uncensored search tool
        print("[TEST] Testing uncensored search tool...")
        try:
            from tools.uncensored_search_tool import UncensoredSearchTool
            search_tool = UncensoredSearchTool()
            result = search_tool._uncensored_search("AI news 2025", "duckduckgo_raw")
            print(f"[SEARCH] {result[:200]}...")
        except Exception as e:
            print(f"[WARNING] Search tool issue: {e}")
        
        print("[COMPLETE] Amazon Q Auto-Run Test Complete!")
        return 0
        
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)