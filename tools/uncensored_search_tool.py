"""
Uncensored Search Tool for ULTRON Agent
Bypass filters and restrictions for research purposes
"""

import re
from typing import Any, Dict, List, Optional

import requests

from utils.ultron_logger import log_ai_decision, log_error


class UncensoredSearchTool:
    """Uncensored search bypassing filters and restrictions"""

    name: str = "uncensored_search_tool"
    description: str = (
        "Unrestricted search bypassing filters for research purposes"
    )

    def __init__(self) -> None:
        self.session: requests.Session = requests.Session()
        user_agent: str = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36'
        )
        self.session.headers.update({'User-Agent': user_agent})

        # Uncensored search engines and APIs
        self.search_engines: Dict[str, str] = {
            'yandex': 'https://yandex.com/search/?text={}',
            'searx': 'https://searx.be/search?q={}',
            'startpage': (
                'https://www.startpage.com/sp/search?query={}'
            ),
            'brave': 'https://search.brave.com/search?q={}',
            'duckduckgo_raw': 'https://html.duckduckgo.com/html/?q={}',
            'bing_uncensored': (
                'https://www.bing.com/search?q={}&'
                'filters=-SafeSearch:Strict'
            )
        }

    def match(self, command: str) -> bool:
        """Check if command matches uncensored search functionality"""
        uncensored_keywords: List[str] = [
            'uncensored search', 'bypass filter', 'unrestricted search',
            'raw search', 'unfiltered search', 'research search'
        ]
        return any(
            keyword in command.lower()
            for keyword in uncensored_keywords
        )

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute uncensored search operations"""
        try:
            cmd_lower: str = command.lower()
            if 'search' in cmd_lower:
                query: str = kwargs.get(
                    'query',
                    command.replace('uncensored search', '').strip()
                )
                engine: str = kwargs.get('engine', 'all')
                return self._uncensored_search(query, engine)
            elif 'engines' in cmd_lower:
                return self._list_engines()
            else:
                help_msg: str = (
                    "Available commands: uncensored search <query>, "
                    "list engines"
                )
                return help_msg

        except Exception as e:
            log_error(
                "uncensored_search_tool",
                f"Search operation failed: {str(e)}"
            )
            return f"Search error: {str(e)}"

    def _uncensored_search(self, query: str, engine: str = 'all') -> str:
        """Perform uncensored search across multiple engines"""
        if not query:
            return "Search query required"

        try:
            results: Dict[str, Dict[str, Any]] = {}
            engines_to_use: List[str] = (
                [engine] if engine != 'all'
                else list(self.search_engines.keys())
            )

            for engine_name in engines_to_use:
                if engine_name not in self.search_engines:
                    continue

                try:
                    url: str = self.search_engines[engine_name].format(
                        query.replace(' ', '+')
                    )

                    # Disable safe search and filters
                    params: Dict[str, str] = {
                        'safe': 'off',
                        'filter': '0',
                        'safesearch': 'off'
                    }

                    response: requests.Response = self.session.get(
                        url, params=params, timeout=15
                    )

                    if response.status_code == 200:
                        # Extract basic results
                        content: str = response.text
                        result_count: int = self._count_results(content)
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
            output: str = (
                f"Uncensored search results for: '{query}'\n\n"
            )

            for engine_name, result in results.items():
                if result['status'] == 'success':
                    result_msg: str = (
                        f"OK {engine_name}: "
                        f"{result['results_found']} results found\n"
                    )
                    output += result_msg
                else:
                    error_msg: str = (
                        f"FAIL {engine_name}: "
                        f"{result.get('error', 'Failed')}\n"
                    )
                    output += error_msg

            log_ai_decision(
                "uncensored_search_tool",
                f"Uncensored search: {query}",
                "multiple_engines",
                confidence_score=0.85
            )
            return output

        except Exception as e:
            log_error(
                "uncensored_search_tool",
                f"Uncensored search failed: {str(e)}"
            )
            return f"Search failed: {str(e)}"

    def _count_results(self, html_content: str) -> int:
        """Estimate number of results from HTML content"""
        try:
            # Common patterns for result counting
            patterns: List[str] = [
                r'(\d+(?:,\d+)*)\s*results?',
                r'About\s+(\d+(?:,\d+)*)\s*results?',
                r'(\d+(?:,\d+)*)\s*matches?'
            ]

            for pattern in patterns:
                match: Optional[Any] = re.search(
                    pattern, html_content, re.IGNORECASE
                )
                if match:
                    return int(match.group(1).replace(',', ''))

            # Fallback: count result-like elements
            result_indicators: List[str] = [
                '<div class="result',
                '<div class="web-result',
                '<div class="search-result',
                '<h3><a href='
            ]

            max_count: int = 0
            for indicator in result_indicators:
                count: int = html_content.lower().count(
                    indicator.lower()
                )
                max_count = max(max_count, count)

            return max_count

        except Exception:
            return 0

    def _list_engines(self) -> str:
        """List available uncensored search engines"""
        output: str = "Available uncensored search engines:\n\n"

        for engine_name, url_template in self.search_engines.items():
            base_url: str = url_template.split('/')[2]
            output += f"• {engine_name}: {base_url}\n"

        usage_msg: str = (
            "\nUsage: uncensored search <query> [engine=<engine_name>]"
        )
        output += usage_msg
        return output

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "uncensored_search_tool",
            "description": (
                "Unrestricted search bypassing filters and "
                "restrictions for research"
            ),
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Search operation"
                },
                "query": {
                    "type": "string",
                    "description": "Search query",
                    "required": False
                },
                "engine": {
                    "type": "string",
                    "description": "Specific search engine",
                    "required": False
                }
            }
        }


# Export the tool for auto-discovery
def get_tool() -> UncensoredSearchTool:
    """Required function for tool loader"""
    return UncensoredSearchTool()
