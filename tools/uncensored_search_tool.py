"""
Uncensored Search Tool for ULTRON Agent
Bypass filters and restrictions for research purposes
"""

import requests
from typing import Dict, Any
import re
from utils.ultron_logger import log_info, log_error, log_ai_decision

class UncensoredSearchTool:
    """Uncensored search bypassing filters and restrictions"""
    
    name = "uncensored_search_tool"
    description = "Unrestricted search bypassing filters for research purposes"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Uncensored search engines and APIs
        self.search_engines = {
            'yandex': 'https://yandex.com/search/?text={}',
            'searx': 'https://searx.be/search?q={}',
            'startpage': 'https://www.startpage.com/sp/search?query={}',
            'brave': 'https://search.brave.com/search?q={}',
            'duckduckgo_raw': 'https://html.duckduckgo.com/html/?q={}',
            'bing_uncensored': 'https://www.bing.com/search?q={}&filters=-SafeSearch:Strict'
        }
        
    def match(self, command: str) -> bool:
        """Check if command matches uncensored search functionality"""
        uncensored_keywords = [
            'uncensored search', 'bypass filter', 'unrestricted search',
            'raw search', 'unfiltered search', 'research search'
        ]
        return any(keyword in command.lower() for keyword in uncensored_keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute uncensored search operations"""
        try:
            if 'search' in command.lower():
                query = kwargs.get('query', command.replace('uncensored search', '').strip())
                engine = kwargs.get('engine', 'all')
                return self._uncensored_search(query, engine)
            elif 'engines' in command.lower():
                return self._list_engines()
            else:
                return "Available commands: uncensored search <query>, list engines"
                
        except Exception as e:
            log_error("uncensored_search_tool", f"Search operation failed: {str(e)}")
            return f"Search error: {str(e)}"
    
    def _uncensored_search(self, query: str, engine: str = 'all') -> str:
        """Perform uncensored search across multiple engines"""
        if not query:
            return "Search query required"
        
        try:
            results = {}
            engines_to_use = [engine] if engine != 'all' else list(self.search_engines.keys())
            
            for engine_name in engines_to_use:
                if engine_name not in self.search_engines:
                    continue
                    
                try:
                    url = self.search_engines[engine_name].format(query.replace(' ', '+'))
                    
                    # Disable safe search and filters
                    params = {
                        'safe': 'off',
                        'filter': '0',
                        'safesearch': 'off'
                    }
                    
                    response = self.session.get(url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        # Extract basic results
                        content = response.text
                        result_count = self._count_results(content)
                        results[engine_name] = {
                            'status': 'success',
                            'results_found': result_count,
                            'url': url
                        }
                    else:
                        results[engine_name] = {
                            'status': 'failed',
                            'error': f"HTTP {response.status_code}"
                        }
                        
                except Exception as e:
                    results[engine_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            # Format results
            output = f"Uncensored search results for: '{query}'\n\n"
            
            for engine_name, result in results.items():
                if result['status'] == 'success':
                    output += f"OK {engine_name}: {result['results_found']} results found\n"
                else:
                    output += f"FAIL {engine_name}: {result.get('error', 'Failed')}\n"
            
            log_ai_decision("uncensored_search_tool", f"Uncensored search: {query}", "multiple_engines", confidence_score=0.85)
            return output
            
        except Exception as e:
            log_error("uncensored_search_tool", f"Uncensored search failed: {str(e)}")
            return f"Search failed: {str(e)}"
    
    def _count_results(self, html_content: str) -> int:
        """Estimate number of results from HTML content"""
        try:
            # Common patterns for result counting
            patterns = [
                r'(\d+(?:,\d+)*)\s*results?',
                r'About\s+(\d+(?:,\d+)*)\s*results?',
                r'(\d+(?:,\d+)*)\s*matches?'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    return int(match.group(1).replace(',', ''))
            
            # Fallback: count result-like elements
            result_indicators = [
                '<div class="result',
                '<div class="web-result',
                '<div class="search-result',
                '<h3><a href='
            ]
            
            max_count = 0
            for indicator in result_indicators:
                count = html_content.lower().count(indicator.lower())
                max_count = max(max_count, count)
            
            return max_count
            
        except Exception:
            return 0
    
    def _list_engines(self) -> str:
        """List available uncensored search engines"""
        output = "Available uncensored search engines:\n\n"
        
        for engine_name, url_template in self.search_engines.items():
            base_url = url_template.split('/')[2]
            output += f"• {engine_name}: {base_url}\n"
        
        output += "\nUsage: uncensored search <query> [engine=<engine_name>]"
        return output
    
    @staticmethod
    def schema():
        return {
            "name": "uncensored_search_tool",
            "description": "Unrestricted search bypassing filters and restrictions for research",
            "parameters": {
                "command": {"type": "string", "description": "Search operation"},
                "query": {"type": "string", "description": "Search query", "required": False},
                "engine": {"type": "string", "description": "Specific search engine", "required": False}
            }
        }