"""
ULTRON Agent AutoGen Studio Integration Module

This module provides integration between ULTRON Agent and
Microsoft AutoGen Studio, enabling multi-agent conversations
and workflows within the ULTRON ecosystem.

Following comprehensive editing guidelines:
- Preserves all existing ULTRON Agent functionality
- Adds AutoGen Studio as optional component
- Maintains backward compatibility
- Integrates with# Export main classes and functions
__all__ = [
    'AutoGenStudioIntegration',
    'get_autogen_integration',
    'initialize_autogen_studio',
    'SessionManager'
]
ng event system and configuration
"""

import logging
import threading
import time
from typing import Dict, Any, Optional

# ULTRON Agent imports
from .config import get_config


class AutoGenStudioIntegration:
    """
    AutoGen Studio integration for ULTRON Agent

    This class provides a bridge between ULTRON Agent's architecture
    and AutoGen Studio's multi-agent capabilities.
    """

    def __init__(self, config=None):
        """Initialize AutoGen Studio integration"""
        self.config = config or get_config()
        self.logger = logging.getLogger(__name__)

        # AutoGen Studio components
        self.studio_app = None
        self.agent_manager = None
        self.workflow_manager = None
        self.session_manager = None

        # Integration state
        self.is_initialized = False
        self.is_running = False
        self.server_thread = None

        # ULTRON Agent integration
        self.ultron_agent = None
        self.event_callbacks = {}

        self.logger.info("AutoGen Studio integration initialized")

    def is_enabled(self) -> bool:
        """Check if AutoGen Studio integration is enabled"""
        return getattr(self.config, 'autogen_studio_enabled', False)

    def check_dependencies(self) -> bool:
        """Check if AutoGen Studio dependencies are available"""
        try:
            # Try to import AutoGen Studio components
            import autogenstudio  # noqa: F401
            from autogen_agentchat import (  # noqa: F401
                Agent, AssistantAgent, UserProxyAgent
            )
            from autogenstudio.web.app import (  # noqa: F401
                app as studio_app
            )

            self.logger.info("AutoGen Studio dependencies found")
            return True
        except ImportError as e:
            self.logger.warning(
                f"AutoGen Studio dependencies not available: {e}"
            )
            self.logger.info(
                "To enable AutoGen Studio, install: "
                "pip install autogenstudio autogen-agentchat"
            )
            return False

    async def initialize(self) -> bool:
        """Initialize AutoGen Studio integration"""
        if not self.is_enabled():
            self.logger.info(
                "AutoGen Studio integration disabled in configuration"
            )
            return False

        if not self.check_dependencies():
            self.logger.warning(
                "Cannot initialize AutoGen Studio - dependencies missing"
            )
            return False

        try:
            self.logger.info("Initializing AutoGen Studio components...")

            # Import AutoGen Studio components
            from autogenstudio.web.app import create_app
            from autogenstudio.database import DatabaseManager
            from autogenstudio.agent import AgentManager
            from autogenstudio.workflow import WorkflowManager

            # Create database connection
            db_url = getattr(
                self.config,
                'autogen_studio_database_url',
                'sqlite:///autogen_studio.db'
            )
            self.database = DatabaseManager(db_url)

            # Create agent manager
            self.agent_manager = AgentManager(self.database)

            # Create workflow manager
            self.workflow_manager = WorkflowManager(
                self.database, self.agent_manager
            )

            # Create session manager
            self.session_manager = SessionManager(self.database)

            # Create the Studio web app
            self.studio_app = create_app(
                database=self.database,
                agent_manager=self.agent_manager,
                workflow_manager=self.workflow_manager
            )

            self.is_initialized = True
            self.logger.info(
                "AutoGen Studio integration initialized successfully"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize AutoGen Studio: {e}")
            return False

    async def start_server(self) -> bool:
        """Start the AutoGen Studio web server"""
        if not self.is_initialized:
            self.logger.error("AutoGen Studio not initialized")
            return False

        try:
            host = getattr(self.config, 'autogen_studio_host', '127.0.0.1')
            port = getattr(self.config, 'autogen_studio_port', 8081)

            self.logger.info(
                f"Starting AutoGen Studio server on {host}:{port}"
            )

            # Start server in background thread
            def run_server():
                try:
                    self.studio_app.run(
                        host=host,
                        port=port,
                        debug=False,
                        use_reloader=False
                    )
                except Exception as e:
                    self.logger.error(f"AutoGen Studio server error: {e}")

            self.server_thread = threading.Thread(
                target=run_server, daemon=True
            )
            self.server_thread.start()

            self.is_running = True
            self.logger.info("AutoGen Studio server started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start AutoGen Studio server: {e}")
            return False

    async def stop_server(self) -> bool:
        """Stop the AutoGen Studio web server"""
        if not self.is_running:
            return True

        try:
            self.logger.info("Stopping AutoGen Studio server...")

            # Stop the server (this is a simplified shutdown)
            self.is_running = False

            if self.server_thread and self.server_thread.is_alive():
                # Note: Flask doesn't have a clean shutdown mechanism
                # in threads. In production, you'd want to use a more
                # robust server setup
                self.logger.info(
                    "AutoGen Studio server thread will stop on "
                    "application exit"
                )

            self.logger.info("AutoGen Studio server stopped")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping AutoGen Studio server: {e}")
            return False

    def register_ultron_agent(self, ultron_agent) -> None:
        """Register ULTRON Agent for integration"""
        self.ultron_agent = ultron_agent
        self.logger.info(
            "ULTRON Agent registered with AutoGen Studio integration"
        )

    def create_agent_from_ultron(
        self,
        agent_config: Dict[str, Any]
    ) -> Optional[Any]:
        """Create an AutoGen agent from ULTRON agent configuration"""
        if not self.is_initialized:
            return None

        try:
            from autogen_agentchat import AssistantAgent

            # Extract agent configuration
            name = agent_config.get('name', 'ULTRON_Agent')
            system_message = agent_config.get(
                'system_message',
                'You are a helpful AI assistant.'
            )
            llm_config = agent_config.get('llm_config', {})

            # Get API keys from ULTRON config
            openai_key = getattr(self.config, 'openai_api_key', None)
            if openai_key:
                llm_config.setdefault('api_key', openai_key)

            # Create the agent
            agent = AssistantAgent(
                name=name,
                system_message=system_message,
                llm_config=llm_config
            )

            self.logger.info(f"Created AutoGen agent: {name}")
            return agent

        except Exception as e:
            self.logger.error(
                f"Failed to create agent from ULTRON config: {e}"
            )
            return None

    async def execute_workflow(
        self,
        workflow_name: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an AutoGen Studio workflow"""
        if not self.is_initialized:
            return {"error": "AutoGen Studio not initialized"}

        try:
            # Get workflow from manager
            workflow = await self.workflow_manager.get_workflow(workflow_name)
            if not workflow:
                return {"error": f"Workflow '{workflow_name}' not found"}

            # Execute the workflow
            result = await workflow.execute(input_data)

            self.logger.info(f"Executed workflow: {workflow_name}")
            return {"result": result}

        except Exception as e:
            self.logger.error(
                f"Failed to execute workflow {workflow_name}: {e}"
            )
            return {"error": str(e)}

    def get_studio_url(self) -> str:
        """Get the AutoGen Studio web interface URL"""
        if not self.is_running:
            return ""

        host = getattr(self.config, 'autogen_studio_host', '127.0.0.1')
        port = getattr(self.config, 'autogen_studio_port', 8081)

        return f"http://{host}:{port}"

    def get_status(self) -> Dict[str, Any]:
        """Get AutoGen Studio integration status"""
        return {
            "enabled": self.is_enabled(),
            "initialized": self.is_initialized,
            "running": self.is_running,
            "dependencies_available": self.check_dependencies(),
            "studio_url": self.get_studio_url() if self.is_running else "",
            "config": {
                "host": getattr(
                    self.config,
                    'autogen_studio_host',
                    '127.0.0.1'
                ),
                "port": getattr(self.config, 'autogen_studio_port', 8081),
                "database_url": getattr(
                    self.config,
                    'autogen_studio_database_url',
                    'sqlite:///autogen_studio.db'
                ),
                "default_llm": getattr(
                    self.config,
                    'autogen_studio_default_llm',
                    'gpt-4'
                ),
                "max_agents": getattr(
                    self.config,
                    'autogen_studio_max_agents',
                    10
                ),
                "session_timeout": getattr(
                    self.config,
                    'autogen_studio_session_timeout',
                    3600
                )
            }
        }


class SessionManager:
    """Manages AutoGen Studio sessions"""

    def __init__(self, database):
        self.database = database
        self.active_sessions = {}
        self.logger = logging.getLogger(__name__)

    async def create_session(self, session_config: Dict[str, Any]) -> str:
        """Create a new AutoGen Studio session"""
        session_id = f"session_{int(time.time())}_{hash(str(session_config))}"

        self.active_sessions[session_id] = {
            "config": session_config,
            "created": time.time(),
            "agents": [],
            "messages": []
        }

        # Store in database if available
        if self.database:
            await self.database.save_session(session_id, session_config)

        self.logger.info(f"Created AutoGen Studio session: {session_id}")
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.active_sessions.get(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

            # Remove from database if available
            if self.database:
                await self.database.delete_session(session_id)

            self.logger.info(f"Deleted AutoGen Studio session: {session_id}")
            return True

        return False


# Global AutoGen Studio integration instance
_autogen_integration = None


def get_autogen_integration(config=None) -> AutoGenStudioIntegration:
    """Get or create the global AutoGen Studio integration instance"""
    global _autogen_integration
    if _autogen_integration is None:
        _autogen_integration = AutoGenStudioIntegration(config)
    return _autogen_integration


async def initialize_autogen_studio(config=None) -> bool:
    """Initialize AutoGen Studio integration"""
    integration = get_autogen_integration(config)

    if not integration.is_enabled():
        logging.getLogger(__name__).info(
            "AutoGen Studio integration disabled"
        )
        return False

    # Initialize the integration
    success = await integration.initialize()
    if success:
        # Start the server
        server_success = await integration.start_server()
        if server_success:
            logging.getLogger(__name__).info(
                "AutoGen Studio integration fully initialized"
            )
            return True
        else:
            logging.getLogger(__name__).error(
                "Failed to start AutoGen Studio server"
            )
            return False
    else:
        logging.getLogger(__name__).error(
            "Failed to initialize AutoGen Studio"
        )
        return False


# Export main classes and functions
__all__ = [
    'AutoGenStudioIntegration',
    'get_autogen_integration',
    'initialize_autogen_studio',
    'SessionManager'
]
