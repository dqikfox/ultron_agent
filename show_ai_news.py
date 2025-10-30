#!/usr/bin/env python3
"""
Display AI News Search Results
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("=== LATEST AI NEWS SEARCH RESULTS ===")
    print()
    
    try:
        from tools.uncensored_search_tool import UncensoredSearchTool
        
        # Initialize search tool
        search_tool = UncensoredSearchTool()
        
        # Execute search
        print("Searching for latest AI news...")
        result = search_tool._uncensored_search('AI news 2025 artificial intelligence breakthrough', 'all')
        
        print()
        print("RESULTS:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # Also try individual engines
        engines = ['yandex', 'brave', 'startpage']
        for engine in engines:
            try:
                print(f"\n[{engine.upper()}] Results:")
                engine_result = search_tool._uncensored_search(f'AI news 2025', engine)
                print(engine_result[:200] + "..." if len(engine_result) > 200 else engine_result)
            except Exception as e:
                print(f"[{engine.upper()}] Error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()