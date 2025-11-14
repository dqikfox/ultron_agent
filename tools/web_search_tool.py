"""
ULTRON Agent - Enhanced Web Search Tool

Unified web search integration with multiple search engines,
result aggregation, caching, and natural language processing.

Supported Engines:
- DuckDuckGo (privacy-focused)
- Brave Search (independent index)
- SearX (meta-search)
- Google (via scraping, fallback)
"""

import requests
import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import re
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup

from tools.tool_interface import ToolInterface
from utils.ultron_logger import log_info, log_error, log_ai_decision
from diagnostics import diagnostic_wrapper, track_metric


class WebSearchTool(ToolInterface):
    """
    Unified web search tool with multi-engine support and intelligent result aggregation.

    Features:
    - Multi-engine search (DuckDuckGo, Brave, SearX)
    - Result caching and deduplication
    - Natural language query processing
    - Relevance scoring and ranking
    - Search result filtering
    """

    def __init__(self):
        self.cache_dir = Path("cache/web_search")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        # Search engine configurations
        self.engines = {
            "duckduckgo": {
                "name": "DuckDuckGo",
                "url": "https://html.duckduckgo.com/html/",
                "enabled": True,
                "weight": 1.0
            },
            "brave": {
                "name": "Brave Search",
                "url": "https://search.brave.com/search",
                "enabled": True,
                "weight": 0.9
            },
            "searx": {
                "name": "SearX",
                "url": "https://searx.be/search",
                "enabled": True,
                "weight": 0.8
            }
        }

        # Cache TTL: 1 hour
        self.cache_ttl = timedelta(hours=1)

        log_info("web_search", "Enhanced web search tool initialized")

    @property
    def name(self) -> str:
        return "Enhanced Web Search"

    @property
    def description(self) -> str:
        return "Multi-engine web search with intelligent result aggregation, caching, and natural language processing"

    def match(self, command: str) -> bool:
        """Check if command should trigger web search"""
        keywords = [
            "search web", "search for", "find online", "look up",
            "web search", "search internet", "google", "search",
            "find information", "research", "query web"
        ]
        return any(kw in command.lower() for kw in keywords)

    @diagnostic_wrapper("web_search", track_performance=True)
    def execute(self, command: str, **kwargs) -> str:
        """Execute web search operations"""
        log_info("web_search", f"Executing search: {command}")
        track_metric("web_search", "searches_performed", 1, "count")

        try:
            # Extract search query
            query = kwargs.get("query") or self._extract_query(command)

            if not query:
                return "❌ Please provide a search query"

            # Extract search parameters
            max_results = kwargs.get("max_results", 10)
            engines = kwargs.get("engines") or ["duckduckgo", "brave"]
            use_cache = kwargs.get("use_cache", True)

            # Check cache first
            if use_cache:
                cached_results = self._get_cached_results(query)
                if cached_results:
                    log_info("web_search", f"Returning cached results for: {query}")
                    return self._format_results(cached_results, from_cache=True)

            # Perform multi-engine search
            log_ai_decision("web_search", f"Searching for: {query}",
                          ai_model="multi_engine_search", confidence_score=0.95)

            all_results = []

            for engine_id in engines:
                if engine_id not in self.engines or not self.engines[engine_id]["enabled"]:
                    continue

                try:
                    results = self._search_engine(engine_id, query, max_results)
                    all_results.extend(results)
                    log_info("web_search", f"Got {len(results)} results from {engine_id}")
                except Exception as e:
                    log_error("web_search", f"Error searching {engine_id}: {e}")
                    continue

            # Deduplicate and rank results
            unique_results = self._deduplicate_results(all_results)
            ranked_results = self._rank_results(unique_results, query)

            # Limit results
            final_results = ranked_results[:max_results]

            # Cache results
            if use_cache:
                self._cache_results(query, final_results)

            # Track metrics
            track_metric("web_search", "results_found", len(final_results), "count")

            return self._format_results(final_results)

        except Exception as e:
            log_error("web_search", f"Search error: {e}", exception=e)
            return f"❌ Search error: {str(e)}"

    # ─────────────────────────────────────────────────────────────────────────
    # Search Engine Implementations
    # ─────────────────────────────────────────────────────────────────────────

    def _search_engine(self, engine_id: str, query: str, max_results: int) -> List[Dict]:
        """Search specific engine and return results"""
        if engine_id == "duckduckgo":
            return self._search_duckduckgo(query, max_results)
        elif engine_id == "brave":
            return self._search_brave(query, max_results)
        elif engine_id == "searx":
            return self._search_searx(query, max_results)
        else:
            return []

    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """Search DuckDuckGo"""
        try:
            params = {
                'q': query,
                'kl': 'us-en'
            }

            response = self.session.post(
                self.engines["duckduckgo"]["url"],
                data=params,
                timeout=10
            )

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            for result_div in soup.find_all('div', class_='result'):
                try:
                    title_elem = result_div.find('a', class_='result__a')
                    snippet_elem = result_div.find('a', class_='result__snippet')

                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "duckduckgo",
                        "weight": self.engines["duckduckgo"]["weight"]
                    })

                    if len(results) >= max_results:
                        break

                except Exception as e:
                    log_error("web_search", f"Error parsing DuckDuckGo result: {e}")
                    continue

            return results

        except Exception as e:
            log_error("web_search", f"DuckDuckGo search error: {e}", exception=e)
            return []

    def _search_brave(self, query: str, max_results: int) -> List[Dict]:
        """Search Brave Search"""
        try:
            params = {
                'q': query,
                'source': 'web'
            }

            response = self.session.get(
                self.engines["brave"]["url"],
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            # Brave uses different HTML structure
            for result_div in soup.find_all('div', class_='snippet'):
                try:
                    title_elem = result_div.find('span', class_='snippet-title')
                    url_elem = result_div.find('cite')
                    desc_elem = result_div.find('p', class_='snippet-description')

                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    url = url_elem.get_text(strip=True) if url_elem else ""
                    snippet = desc_elem.get_text(strip=True) if desc_elem else ""

                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "brave",
                        "weight": self.engines["brave"]["weight"]
                    })

                    if len(results) >= max_results:
                        break

                except Exception as e:
                    log_error("web_search", f"Error parsing Brave result: {e}")
                    continue

            return results

        except Exception as e:
            log_error("web_search", f"Brave search error: {e}", exception=e)
            return []

    def _search_searx(self, query: str, max_results: int) -> List[Dict]:
        """Search SearX meta-search engine"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'categories': 'general'
            }

            response = self.session.get(
                self.engines["searx"]["url"],
                params=params,
                timeout=15
            )

            if response.status_code != 200:
                return []

            data = response.json()
            results = []

            for item in data.get('results', []):
                try:
                    results.append({
                        "title": item.get('title', ''),
                        "url": item.get('url', ''),
                        "snippet": item.get('content', ''),
                        "source": "searx",
                        "weight": self.engines["searx"]["weight"]
                    })

                    if len(results) >= max_results:
                        break

                except Exception as e:
                    log_error("web_search", f"Error parsing SearX result: {e}")
                    continue

            return results

        except Exception as e:
            log_error("web_search", f"SearX search error: {e}", exception=e)
            return []

    # ─────────────────────────────────────────────────────────────────────────
    # Result Processing
    # ─────────────────────────────────────────────────────────────────────────

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on URL similarity"""
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get('url', '')

            # Normalize URL
            normalized = self._normalize_url(url)

            if normalized not in seen_urls:
                seen_urls.add(normalized)
                unique_results.append(result)

        return unique_results

    def _rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Rank results by relevance to query"""
        query_terms = set(query.lower().split())

        for result in results:
            # Calculate relevance score
            score = 0.0

            # Title relevance
            title_terms = set(result.get('title', '').lower().split())
            title_overlap = len(query_terms & title_terms)
            score += title_overlap * 2.0

            # Snippet relevance
            snippet_terms = set(result.get('snippet', '').lower().split())
            snippet_overlap = len(query_terms & snippet_terms)
            score += snippet_overlap * 1.0

            # Engine weight
            score *= result.get('weight', 1.0)

            # URL authority (simple heuristic)
            url = result.get('url', '')
            if any(domain in url for domain in ['wikipedia.org', '.gov', '.edu']):
                score *= 1.2

            result['relevance_score'] = score

        # Sort by relevance score
        return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication"""
        try:
            parsed = urlparse(url)
            # Remove www., query params, fragments
            normalized = f"{parsed.scheme}://{parsed.netloc.replace('www.', '')}{parsed.path}"
            return normalized.rstrip('/')
        except:
            return url

    # ─────────────────────────────────────────────────────────────────────────
    # Caching
    # ─────────────────────────────────────────────────────────────────────────

    def _get_cached_results(self, query: str) -> Optional[List[Dict]]:
        """Get cached search results if available and not expired"""
        cache_key = self._generate_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            data = json.loads(cache_file.read_text())

            # Check if cache is expired
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.cache_ttl:
                cache_file.unlink()  # Delete expired cache
                return None

            return data['results']

        except Exception as e:
            log_error("web_search", f"Error reading cache: {e}")
            return None

    def _cache_results(self, query: str, results: List[Dict]):
        """Cache search results"""
        cache_key = self._generate_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            data = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }

            cache_file.write_text(json.dumps(data, indent=2))
            log_info("web_search", f"Cached {len(results)} results for query: {query}")

        except Exception as e:
            log_error("web_search", f"Error caching results: {e}")

    def _generate_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

    # ─────────────────────────────────────────────────────────────────────────
    # Formatting
    # ─────────────────────────────────────────────────────────────────────────

    def _format_results(self, results: List[Dict], from_cache: bool = False) -> str:
        """Format search results for display"""
        if not results:
            return "ℹ️ No search results found"

        output = []

        # Header
        cache_indicator = " (from cache)" if from_cache else ""
        output.append(f"🔍 **Web Search Results{cache_indicator}**")
        output.append(f"Found {len(results)} results\n")

        # Results
        for i, result in enumerate(results, 1):
            output.append(f"**{i}. {result.get('title', 'No Title')}**")
            output.append(f"   🔗 {result.get('url', 'No URL')}")

            if result.get('snippet'):
                # Truncate long snippets
                snippet = result['snippet']
                if len(snippet) > 200:
                    snippet = snippet[:200] + "..."
                output.append(f"   💬 {snippet}")

            output.append(f"   📊 Source: {result.get('source', 'unknown')} | Relevance: {result.get('relevance_score', 0):.2f}")
            output.append("")

        return '\n'.join(output)

    def _extract_query(self, command: str) -> str:
        """Extract search query from command"""
        # Remove command keywords
        keywords = ['search', 'web', 'for', 'find', 'online', 'internet', 'google', 'look up']
        words = command.split()

        query_words = [w for w in words if w.lower() not in keywords]
        return ' '.join(query_words).strip()

    @classmethod
    def schema(cls) -> dict:
        """Return tool schema for API documentation"""
        return {
            "name": "web_search_tool",
            "description": "Multi-engine web search with intelligent result aggregation and caching",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The search command"
                    },
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    },
                    "engines": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Search engines to use (duckduckgo, brave, searx)",
                        "default": ["duckduckgo", "brave"]
                    },
                    "use_cache": {
                        "type": "boolean",
                        "description": "Whether to use cached results",
                        "default": True
                    }
                },
                "required": ["command"]
            }
        }
