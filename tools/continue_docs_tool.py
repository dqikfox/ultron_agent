"""
ULTRON Agent - Continue Documentation Integration Tool
Integrates Continue's documentation awareness for better code understanding.
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from utils.ultron_logger import log_info, log_error


class ContinueDocsTool:
    """Continue documentation integration for enhanced code awareness"""
    
    name = "continue_docs"
    description = "Access Continue documentation and codebase awareness"
    
    def __init__(self):
        self.docs_config = self._load_docs_config()
        self.continue_api = "http://localhost:65432"  # Continue extension API
    
    def match(self, command: str) -> bool:
        """Match documentation-related commands"""
        keywords = ["docs", "documentation", "help", "guide", "how to", "explain"]
        return any(keyword in command.lower() for keyword in keywords)
    
    def execute(self, command: str, **kwargs) -> str:
        """Execute documentation queries"""
        try:
            cmd_lower = command.lower()
            
            if "continue" in cmd_lower and "docs" in cmd_lower:
                return self._get_continue_docs(command)
            elif "codebase" in cmd_lower:
                return self._get_codebase_info(command)
            elif "help" in cmd_lower or "how to" in cmd_lower:
                return self._get_help_info(command)
            else:
                return self._search_documentation(command)
                
        except Exception as e:
            log_error("continue_docs", f"Documentation query failed: {str(e)}")
            return f"Documentation error: {str(e)}"
    
    def _load_docs_config(self) -> Dict:
        """Load documentation configuration"""
        try:
            docs_file = Path(".continue/docs.yaml")
            if docs_file.exists():
                import yaml
                with open(docs_file, 'r') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            log_error("continue_docs", f"Failed to load docs config: {str(e)}")
        
        return {
            "title": "ULTRON Agent Documentation",
            "startUrl": "file://./README.md",
            "rootUrl": "file://./"
        }
    
    def _get_continue_docs(self, query: str) -> str:
        """Get Continue documentation"""
        try:
            # Extract topic from query
            topic = self._extract_topic(query)
            
            # Continue docs URLs
            docs_urls = {
                "mcp": "https://docs.continue.dev/guides/model-context-protocol",
                "context": "https://docs.continue.dev/guides/codebase-documentation-awareness",
                "models": "https://docs.continue.dev/reference/model-providers",
                "config": "https://docs.continue.dev/reference/config",
                "providers": "https://docs.continue.dev/reference/context-providers"
            }
            
            if topic in docs_urls:
                return f"Continue Documentation - {topic.upper()}:\n{docs_urls[topic]}\n\nFor local access, use Continue extension's @docs context provider."
            else:
                return f"Continue Documentation Topics:\n" + "\n".join([f"- {k}: {v}" for k, v in docs_urls.items()])
                
        except Exception as e:
            return f"Continue docs error: {str(e)}"
    
    def _get_codebase_info(self, query: str) -> str:
        """Get codebase information using Continue's awareness"""
        try:
            # Key ULTRON Agent components
            components = {
                "agent_core.py": "Main integration hub - initializes all systems",
                "brain.py": "AI reasoning engine with Ollama integration", 
                "voice_manager.py": "Multi-engine voice system with ElevenLabs",
                "gui/ultron_enhanced/web/": "Primary GUI interface",
                "tools/": "Modular tool plugins with dynamic discovery",
                "utils/": "Event system, logging, and utilities",
                ".continue/config.yaml": "Continue extension configuration"
            }
            
            result = "ULTRON Agent Codebase Overview:\n\n"
            for component, description in components.items():
                result += f"📁 {component}\n   {description}\n\n"
            
            result += "Use Continue's @codebase context provider for detailed code analysis."
            return result
            
        except Exception as e:
            return f"Codebase info error: {str(e)}"
    
    def _get_help_info(self, query: str) -> str:
        """Get help information"""
        help_topics = {
            "voice": "Use voice commands with 'hey ultron' prefix. Voice system supports ElevenLabs TTS/STT.",
            "commands": "Natural language commands: 'open chrome', 'take screenshot', 'search for cars'",
            "mcp": "MCP servers configured: GitHub, PostgreSQL, Browser, Memory, Filesystem",
            "tools": "Available tools in tools/ directory - dynamically loaded by agent_core.py",
            "gui": "Primary GUI at localhost:8080 - Enhanced ULTRON Pokédex interface",
            "config": "Configuration in ultron_config.json - API keys via environment variables"
        }
        
        topic = self._extract_topic(query)
        if topic in help_topics:
            return f"Help - {topic.upper()}:\n{help_topics[topic]}"
        else:
            result = "ULTRON Agent Help Topics:\n\n"
            for topic, info in help_topics.items():
                result += f"🔹 {topic}: {info}\n\n"
            return result
    
    def _search_documentation(self, query: str) -> str:
        """Search through documentation"""
        try:
            # Search key documentation files
            doc_files = [
                "README.md",
                "DOCUMENTATION_HUB.md", 
                ".github/copilot-instructions.md",
                "MCP_INTEGRATION_GUIDE.md"
            ]
            
            results = []
            search_terms = self._extract_search_terms(query)
            
            for doc_file in doc_files:
                doc_path = Path(doc_file)
                if doc_path.exists():
                    try:
                        content = doc_path.read_text(encoding='utf-8')
                        if any(term.lower() in content.lower() for term in search_terms):
                            results.append(f"📄 {doc_file}: Contains information about {', '.join(search_terms)}")
                    except Exception:
                        continue
            
            if results:
                return "Documentation Search Results:\n" + "\n".join(results)
            else:
                return f"No documentation found for: {', '.join(search_terms)}"
                
        except Exception as e:
            return f"Documentation search error: {str(e)}"
    
    def _extract_topic(self, query: str) -> str:
        """Extract main topic from query"""
        topics = ["mcp", "context", "models", "config", "providers", "voice", "commands", "tools", "gui"]
        for topic in topics:
            if topic in query.lower():
                return topic
        return "general"
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query"""
        # Remove common words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "how", "what", "where"}
        words = [w.lower() for w in query.split() if w.lower() not in stop_words and len(w) > 2]
        return words[:5]  # Limit to 5 terms
    
    @staticmethod
    def schema():
        return {
            "name": "continue_docs",
            "description": "Access Continue documentation and codebase awareness",
            "parameters": {
                "command": {"type": "string", "description": "Documentation query"}
            }
        }