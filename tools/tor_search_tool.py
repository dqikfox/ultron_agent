"""
Tor Deep Web Search Tool for ULTRON Agent
Unrestricted research capabilities via Tor network
"""

import requests
import subprocess
import time
import os
from utils.ultron_logger import log_info, log_error, log_ai_decision

class TorSearchTool:
    """Tor-enabled deep web search for research purposes"""
    
    name = "tor_search_tool"
    description = "Unrestricted deep web search via Tor network for research"
    
    def __init__(self):
        self.tor_port = 9050
        self.control_port = 9051
        self.tor_process = None
        self.session = None
        self.is_tor_running = False
        self.tor_executable = None
        
    def match(self, command: str) -> bool:
        """Check if command matches Tor search functionality"""
        tor_keywords = [
            'tor search', 'deep web', 'onion search', 'darknet search',
            'uncensored search', 'anonymous search', 'tor browse'
        ]
        return any(keyword in command.lower() for keyword in tor_keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute Tor search operations"""
        try:
            if 'start tor' in command.lower():
                return self._start_tor()
            elif 'stop tor' in command.lower():
                return self._stop_tor()
            elif 'search' in command.lower():
                query = kwargs.get('query', command.replace('tor search', '').strip())
                return self._tor_search(query)
            elif 'browse' in command.lower():
                url = kwargs.get('url', '')
                return self._tor_browse(url)
            else:
                return "Available commands: start tor, stop tor, tor search <query>, tor browse <url>"
                
        except Exception as e:
            log_error("tor_search_tool", f"Tor operation failed: {str(e)}")
            return f"Tor error: {str(e)}"
    
    def _start_tor(self) -> str:
        """Start Tor service"""
        try:
            if self.is_tor_running:
                return "Tor is already running"
            
            # Check if Tor is installed (Windows paths)
            tor_paths = [
                'tor',
                'C:\\Program Files\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe',
                f'C:\\Users\\{os.getenv("USERNAME", "user")}\\Desktop\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe',
                'tor.exe'
            ]
            
            tor_executable = None
            for path in tor_paths:
                try:
                    subprocess.run([path, '--version'], capture_output=True, check=True, timeout=5)
                    tor_executable = path
                    break
                except:
                    continue
            
            if not tor_executable:
                return "Tor not found. Ensure Tor Browser is installed or tor.exe is in PATH"
            
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
                log_info("tor_search_tool", "Tor service started successfully")
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
    
    def _setup_session(self):
        """Setup requests session with Tor proxy"""
        self.session = requests.Session()
        self.session.proxies = {
            'http': f'socks5://127.0.0.1:{self.tor_port}',
            'https': f'socks5://127.0.0.1:{self.tor_port}'
        }
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        })
    
    def _test_tor_connection(self) -> bool:
        """Test if Tor connection is working"""
        try:
            test_session = requests.Session()
            test_session.proxies = {
                'http': f'socks5://127.0.0.1:{self.tor_port}',
                'https': f'socks5://127.0.0.1:{self.tor_port}'
            }
            
            # Test with Tor check service
            response = test_session.get('https://check.torproject.org/api/ip', timeout=30)
            data = response.json()
            return data.get('IsTor', False)
            
        except Exception:
            return False
    
    def _tor_search(self, query: str) -> str:
        """Search the deep web via Tor"""
        if not self.is_tor_running:
            return "Tor not running. Use 'start tor' first."
        
        if not query:
            return "Search query required"
        
        try:
            # Search engines accessible via Tor
            search_engines = [
                'https://duckduckgogg42ts72.onion/?q={}',
                'https://3g2upl4pq6kufc4m.onion/?q={}',
                'https://searx.be/search?q={}'
            ]
            
            results = []
            for engine_url in search_engines:
                try:
                    url = engine_url.format(query.replace(' ', '+'))
                    response = self.session.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        content = response.text
                        if 'results' in content.lower():
                            results.append(f"Results found via {engine_url.split('/')[2]}")
                        
                except Exception:
                    continue
            
            if results:
                log_ai_decision("tor_search_tool", f"Tor search completed: {query}", "tor_network", confidence_score=0.8)
                return f"Deep web search for '{query}' completed.\n" + "\n".join(results)
            else:
                return f"No results found for '{query}' via Tor network"
                
        except Exception as e:
            log_error("tor_search_tool", f"Tor search failed: {str(e)}")
            return f"Search failed: {str(e)}"
    
    def _tor_browse(self, url: str) -> str:
        """Browse a specific URL via Tor"""
        if not self.is_tor_running:
            return "Tor not running. Use 'start tor' first."
        
        if not url:
            return "URL required for browsing"
        
        try:
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                content_length = len(response.text)
                log_ai_decision("tor_search_tool", f"Tor browse: {url}", "tor_network", confidence_score=0.9)
                return f"Successfully accessed {url} via Tor\nContent length: {content_length} characters\nStatus: {response.status_code}"
            else:
                return f"Failed to access {url}. Status: {response.status_code}"
                
        except Exception as e:
            log_error("tor_search_tool", f"Tor browse failed: {str(e)}")
            return f"Browse failed: {str(e)}"
    
    def get_tor_status(self):
        """Get current Tor status"""
        return {
            'tor_running': self.is_tor_running,
            'tor_port': self.tor_port,
            'control_port': self.control_port,
            'session_active': self.session is not None
        }
    
    @staticmethod
    def schema():
        return {
            "name": "tor_search_tool",
            "description": "Unrestricted deep web search and browsing via Tor network",
            "parameters": {
                "command": {"type": "string", "description": "Tor operation"},
                "query": {"type": "string", "description": "Search query", "required": False},
                "url": {"type": "string", "description": "URL to browse", "required": False}
            }
        }