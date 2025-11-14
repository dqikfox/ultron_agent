"""
Tor Deep Web Search Tool for ULTRON Agent
Unrestricted research capabilities via Tor network
"""

import os
import subprocess
import time
from typing import Any, Dict, List, Optional

import requests

from utils.ultron_logger import log_ai_decision, log_error, log_info


class TorSearchTool:
    """Tor-enabled deep web search for research purposes"""

    name: str = "tor_search_tool"
    description: str = (
        "Unrestricted deep web search via Tor network for research"
    )

    def __init__(self) -> None:
        self.tor_port: int = 9050
        self.control_port: int = 9051
        self.tor_process: Optional[subprocess.Popen] = None
        self.session: Optional[requests.Session] = None
        self.is_tor_running: bool = False
        self.tor_executable: Optional[str] = None

    def match(self, command: str) -> bool:
        """Check if command matches Tor search functionality"""
        tor_keywords: List[str] = [
            'tor search', 'deep web', 'onion search', 'darknet search',
            'uncensored search', 'anonymous search', 'tor browse'
        ]
        return any(
            keyword in command.lower() for keyword in tor_keywords
        )

    def execute(self, command: str, **kwargs: Any) -> str:
        """Execute Tor search operations"""
        try:
            cmd_lower: str = command.lower()
            if 'start tor' in cmd_lower:
                return self._start_tor()
            elif 'stop tor' in cmd_lower:
                return self._stop_tor()
            elif 'search' in cmd_lower:
                query: str = kwargs.get(
                    'query',
                    command.replace('tor search', '').strip()
                )
                return self._tor_search(query)
            elif 'browse' in cmd_lower:
                url: str = kwargs.get('url', '')
                return self._tor_browse(url)
            else:
                help_text: str = (
                    "Available commands: start tor, stop tor, "
                    "tor search <query>, tor browse <url>"
                )
                return help_text

        except Exception as e:
            log_error("tor_search_tool", f"Tor operation failed: {str(e)}")
            return f"Tor error: {str(e)}"

    def _start_tor(self) -> str:
        """Start Tor service"""
        try:
            if self.is_tor_running:
                return "Tor is already running"

            # Check if Tor is installed (Windows paths)
            username: str = os.getenv("USERNAME", "user")
            tor_browser_path: str = (
                'C:\\Program Files\\Tor Browser\\Browser\\TorBrowser\\Tor\\'
                'tor.exe'
            )
            tor_browser_alt: str = (
                f'C:\\Users\\{username}\\Desktop\\Tor Browser\\Browser\\'
                'TorBrowser\\Tor\\tor.exe'
            )
            tor_paths: List[str] = [
                'tor',
                tor_browser_path,
                tor_browser_alt,
                'tor.exe'
            ]

            tor_executable: Optional[str] = None
            for path in tor_paths:
                try:
                    subprocess.run(
                        [path, '--version'],
                        capture_output=True,
                        check=True,
                        timeout=5
                    )
                    tor_executable = path
                    break
                except Exception:
                    continue

            if not tor_executable:
                error_msg: str = (
                    "Tor not found. Ensure Tor Browser is installed "
                    "or tor.exe is in PATH"
                )
                return error_msg

            self.tor_executable = tor_executable

            # Start Tor process
            self.tor_process = subprocess.Popen([
                self.tor_executable,
                '--SocksPort', str(self.tor_port),
                '--ControlPort', str(self.control_port)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait for Tor to bootstrap
            time.sleep(10)

            # Test connection
            if self._test_tor_connection():
                self.is_tor_running = True
                self._setup_session()
                log_info(
                    "tor_search_tool", "Tor service started successfully"
                )
                return "Tor started successfully. Anonymous browsing enabled."
            else:
                return "Tor failed to start properly"

        except Exception as e:
            log_error("tor_search_tool", f"Failed to start Tor: {str(e)}")
            return f"Failed to start Tor: {str(e)}"

    def _stop_tor(self) -> str:
        """Stop Tor service"""
        try:
            if self.tor_process:
                self.tor_process.terminate()
                self.tor_process.wait()
                self.tor_process = None

            if self.session:
                self.session.close()
                self.session = None

            self.is_tor_running = False
            log_info("tor_search_tool", "Tor service stopped")
            return "Tor stopped successfully"

        except Exception as e:
            log_error("tor_search_tool", f"Failed to stop Tor: {str(e)}")
            return f"Failed to stop Tor: {str(e)}"

    def _setup_session(self) -> None:
        """Setup requests session with Tor proxy"""
        self.session = requests.Session()
        socks_url: str = f'socks5://127.0.0.1:{self.tor_port}'
        self.session.proxies = {
            'http': socks_url,
            'https': socks_url
        }
        user_agent: str = (
            'Mozilla/5.0 (Windows NT 10.0; rv:91.0) '
            'Gecko/20100101 Firefox/91.0'
        )
        self.session.headers.update({'User-Agent': user_agent})

    def _test_tor_connection(self) -> bool:
        """Test if Tor connection is working"""
        try:
            test_session: requests.Session = requests.Session()
            socks_url: str = f'socks5://127.0.0.1:{self.tor_port}'
            test_session.proxies = {
                'http': socks_url,
                'https': socks_url
            }

            # Test with Tor check service
            response: requests.Response = test_session.get(
                'https://check.torproject.org/api/ip', timeout=30
            )
            data: Dict[str, Any] = response.json()
            return data.get('IsTor', False)

        except Exception:
            return False

    def _tor_search(self, query: str) -> str:
        """Search the deep web via Tor"""
        if not self.is_tor_running or not self.session:
            return "Tor not running. Use 'start tor' first."

        if not query:
            return "Search query required"

        try:
            # Search engines accessible via Tor
            search_engines: List[str] = [
                'https://duckduckgogg42ts72.onion/?q={}',
                'https://3g2upl4pq6kufc4m.onion/?q={}',
                'https://searx.be/search?q={}'
            ]

            results: List[str] = []
            for engine_url in search_engines:
                try:
                    url: str = engine_url.format(
                        query.replace(' ', '+')
                    )
                    response: requests.Response = self.session.get(
                        url, timeout=30
                    )

                    if response.status_code == 200:
                        content: str = response.text
                        if 'results' in content.lower():
                            engine_name: str = engine_url.split('/')[2]
                            results.append(
                                f"Results found via {engine_name}"
                            )

                except Exception:
                    continue

            if results:
                log_ai_decision(
                    "tor_search_tool",
                    f"Tor search completed: {query}",
                    "tor_network",
                    confidence_score=0.8
                )
                result_str: str = "\n".join(results)
                return (
                    f"Deep web search for '{query}' completed.\n"
                    f"{result_str}"
                )
            else:
                return f"No results found for '{query}' via Tor network"

        except Exception as e:
            log_error("tor_search_tool", f"Tor search failed: {str(e)}")
            return f"Search failed: {str(e)}"

    def _tor_browse(self, url: str) -> str:
        """Browse a specific URL via Tor"""
        if not self.is_tor_running or not self.session:
            return "Tor not running. Use 'start tor' first."

        if not url:
            return "URL required for browsing"

        try:
            response: requests.Response = self.session.get(
                url, timeout=30
            )

            if response.status_code == 200:
                content_length: int = len(response.text)
                log_ai_decision(
                    "tor_search_tool",
                    f"Tor browse: {url}",
                    "tor_network",
                    confidence_score=0.9
                )
                return (
                    f"Successfully accessed {url} via Tor\n"
                    f"Content length: {content_length} characters\n"
                    f"Status: {response.status_code}"
                )
            else:
                return (
                    f"Failed to access {url}. "
                    f"Status: {response.status_code}"
                )

        except Exception as e:
            log_error("tor_search_tool", f"Tor browse failed: {str(e)}")
            return f"Browse failed: {str(e)}"

    def get_tor_status(self) -> Dict[str, Any]:
        """Get current Tor status"""
        return {
            'tor_running': self.is_tor_running,
            'tor_port': self.tor_port,
            'control_port': self.control_port,
            'session_active': self.session is not None
        }

    @staticmethod
    def schema() -> Dict[str, Any]:
        """Return tool metadata for OpenAI-compatible function calling"""
        return {
            "name": "tor_search_tool",
            "description": (
                "Unrestricted deep web search and browsing via Tor"
            ),
            "parameters": {
                "command": {
                    "type": "string",
                    "description": "Tor operation"
                },
                "query": {
                    "type": "string",
                    "description": "Search query",
                    "required": False
                },
                "url": {
                    "type": "string",
                    "description": "URL to browse",
                    "required": False
                }
            }
        }


# Export the tool for auto-discovery
def get_tool() -> TorSearchTool:
    """Required function for tool loader"""
    return TorSearchTool()
