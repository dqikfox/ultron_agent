# ULTRON Agent Tools Inventory

Auto-generated tool discovery and documentation.

**Total Tools Found:** 105

## Tool Categories

- **Cloud & Infrastructure** (10 tools)
- **Development Tools** (6 tools)
- **Memory & Data** (2 tools)
- **Mobile & Web** (7 tools)
- **Automation & Integration** (13 tools)
- **AI & Model Inference** (8 tools)
- **System & Platform** (1 tools)
- **GUI & Interface** (7 tools)
- **Other** (51 tools)

---


## Cloud & Infrastructure (10)


### AWSBedrockTool

- **File:** `aws_bedrock_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** AWS Bedrock integration tool for cloud-based AI inference
- **Public Methods:** name, description, match, execute, get_conversation_history
  ... and 1 more

### AWSConfigMonitoringTool

- **File:** `aws_config_monitoring_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Monitor AWS Config compliance and trigger automated remediation
- **Public Methods:** name, description, match, execute, schema

### AWSIntegrationTool

- **File:** `aws_integration_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** AWS services integration for ULTRON Agent
- **Public Methods:** name, description, match, execute, schema

### AWSSolutionsTool

- **File:** `aws_solutions_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** AWS Solutions Library integration tool
- **Public Methods:** name, description, match, execute, schema

### CheapCloud

- **File:** `cheap_cloud.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** $8/month cloud integration
- **Public Methods:** get_status

### CloudRouter

- **File:** `cloud_router.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Routes AI requests to optimal cloud provider
- **Public Methods:** get_stats

### DockerIntegrationTool

- **File:** `docker_integration_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### FreeCloudIntegration

- **File:** `free_cloud_integration.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Integrates free cloud services

### RedisIntegrationTool

- **File:** `redis_integration_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### VoiceAWSTool

- **File:** `voice_aws_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Voice-activated AWS operations for ULTRON Agent
- **Public Methods:** name, description, match, execute, schema

## Development Tools (6)


### AutoGenAutomationTool

- **File:** `autogen_automation_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### DependencyAnalyzerTool

- **File:** `dependency_analyzer_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Analyzes project dependencies and provides insights.
- Finds unused dependencies
- Detects import patterns
- Suggests dependency updates
- Identifies circular dependencies
- **Public Methods:** match, execute, schema

### ProjectAutomationTool

- **File:** `project_automation_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for generating automated project setup scripts using Anthropic Claude

This tool creates comprehensive Python scripts that automate:
- Local AI model setup and configuration
- GitHub repository c
- **Public Methods:** match, execute, schema

### ProjectManagerTool

- **File:** `project_manager_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** AI Project Manager integration tool
- **Public Methods:** name, description, match, execute, schema

### ScreenshotAnalyzerTool

- **File:** `screenshot_analyzer_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for taking screenshots and AI analysis
- **Public Methods:** match, execute, schema

### UltronProjectTool

- **File:** `ultron_project_tool.py`
- **Inherits From:** `Tool`
- **Public Methods:** match, execute, analyze_project, review_file, optimize_code
  ... and 9 more

## Memory & Data (2)


### EnhancedMemoryTool

- **File:** `enhanced_memory_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### MemoryContextTool

- **File:** `memory_context_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Contextual memory system for natural language understanding
- **Public Methods:** match, execute, store_search_query, schema

## Mobile & Web (7)


### ADBManager

- **File:** `adb_manager.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Manages ADB commands and Android device interactions
- **Public Methods:** get_devices, get_device_properties, get_battery_info, get_storage_info, list_apps
  ... and 16 more

### ADBWebHandler

- **File:** `adb_web_integration.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Handles ADB web requests
- **Public Methods:** handle_adb_get, handle_adb_post

### BrowserMCPEnhancedTool

- **File:** `browser_mcp_enhanced_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Enhanced browser automation via BrowserMCP
- **Public Methods:** name, description, match, execute, schema

### BrowserMCPTool

- **File:** `browser_mcp_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Browser automation tool using MCP server
- **Public Methods:** match

### MobileWebInterfaceTool

- **File:** `mobile_web_interface_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Tool for creating unified Pokédex-styled web interface for ULTRON Agent
- **Public Methods:** match, execute, start_interface, stop_interface, get_status
  ... and 2 more

### WebScrapingTool

- **File:** `web_scraping_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for web scraping and data extraction from websites
- **Public Methods:** match, execute, scrape_website, extract_structured_data, analyze_website
  ... and 2 more

### WebSearchTool

- **File:** `web_search_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Unified web search tool with multi-engine support and intelligent result aggregation.

Features:
- Multi-engine search (DuckDuckGo, Brave, SearX)
- Result caching and deduplication
- Natural language 
- **Public Methods:** name, description, match, execute, schema

## Automation & Integration (13)


### AmazonQIntegrationTool

- **File:** `amazon_q_integration_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Amazon Q integration with auto-run capabilities
- **Public Methods:** name, description, match, execute, start_auto_run_on_startup
  ... and 1 more

### CopilotCLIAutomationTool

- **File:** `copilot_cli_automation_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Tool for orchestrating self-prompting automation through Copilot CLI.

Enables ULTRON Agent to:
- Autonomously delegate tasks to Copilot coding agent
- Create self-improvement workflows
- Coordinate m
- **Public Methods:** name, description, match, execute, schema

### DatabaseIntegrationTool

- **File:** `database_integration_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Tool for PostgreSQL/Supabase database operations with comprehensive security
- **Public Methods:** name, description, connect, match, execute
  ... and 2 more

### FastAPIIntegrationTool

- **File:** `fastapi_integration_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### FileSyncTool

- **File:** `file_sync_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, hash_file, archive_file, sync_directories
  ... and 1 more

### JupyterIntegrationTool

- **File:** `jupyter_integration_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### LangflowIntegrationTool

- **File:** `langflow_integration_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### mcp_integration_tool.py

- **File:** `mcp_integration_tool.py`
- **Inherits From:** ToolInterface (standard)
- ⚠️ **Parse Error:** unindent does not match any outer indentation level (<unknown>, line 56)

### OpenInterfaceSession

- **File:** `open_interface_autopilot.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Coordinates repeated LLM planning + execution cycles.
- **Public Methods:** capture, plan, execute, run

### PyCharmIntegrationTool

- **File:** `pycharm_integration_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Bridge between ULTRON and PyCharm IDE

Enables:
- Real-time tool file sync from PyCharm to ULTRON
- Debugging support with PyCharm debugger
- Project structure awareness
- Automatic tool registration 
- **Public Methods:** add_watch, add_callback, stop_monitoring, parse_tool_definition, name
  ... and 4 more

### ServiceIntegrationTool

- **File:** `service_integration_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for integrating with external services
- **Public Methods:** match, execute, get_google_calendar_events, send_email_via_smtp, read_recent_emails
  ... and 3 more

### StreamlitIntegrationTool

- **File:** `streamlit_integration_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### VSCodeIntegrationTool

- **File:** `vscode_integration_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

## AI & Model Inference (8)


### AvatarBuilderTool

- **File:** `avatar_builder_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### BedrockAgentTool

- **File:** `bedrock_agent_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Bedrock Agent integration tool for ULTRON
- **Public Methods:** name, description, match, execute, schema

### UnityAITool

- **File:** `unity_ai_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### UnityBarracudaTool

- **File:** `unity_barracuda_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### UnityHubTool

- **File:** `unity_hub_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Unity Hub integration for project management
- **Public Methods:** name, description, match, execute, schema

### UnityInferenceTool

- **File:** `unity_inference_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### UnitySentisTool

- **File:** `unity_sentis_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### UnityTool

- **File:** `unity_tools.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

## System & Platform (1)


### WindowsSystemTool

- **File:** `windows_system_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Advanced Windows system integration with natural language processing
- **Public Methods:** match, execute, schema

## GUI & Interface (7)


### AutonomousPyAutoGUI

- **File:** `autonomous_pyautogui.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool that executes PyAutoGUI commands from AI-generated code
- **Public Methods:** match, execute, schema

### BrowserFunctionTester

- **File:** `gui_function_tester.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Browser-based GUI function testing
- **Public Methods:** to_dict, test_function_existence, generate_html_report

### GUILinkValidator

- **File:** `gui_link_validator.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Comprehensive GUI link and function validator
- **Public Methods:** to_dict, to_dict, save_report, print_summary

### IntegratedGUIValidator

- **File:** `gui_validation_suite.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Master GUI validation suite

### OllamaPyAutoGUIBridge

- **File:** `ollama_pyautogui_bridge.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Bridge between Ollama and PyAutoGUI for automation
- **Public Methods:** match, execute, call_function, schema

### PyAutoGUITool

- **File:** `pyautogui_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Tool for screen automation and GUI control
- **Public Methods:** name, description, match, execute, schema

### ToolInterface

- **File:** `tool_interface.py`
- **Inherits From:** `ABC`
- **Description:** Abstract base class for all ULTRON Agent tools
- **Public Methods:** name, description, match, execute, schema
  ... and 2 more

## Other (51)


### AIAgentPersonas

- **File:** `ai_agent_personas.py`
- **Inherits From:** `Tool`
- **Public Methods:** match, execute, schema

### AIConsultantRouter

- **File:** `ai_consultant_router.py`
- **Inherits From:** `Tool`
- **Public Methods:** match, execute, schema

### AIDevelopmentCoordinator

- **File:** `ai_development_coordinator.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Coordinate AI assistants for ULTRON Agent development
- **Public Methods:** match, schema

### AITeamCollaboration

- **File:** `ai_team_collaboration.py`
- **Inherits From:** `Tool`
- **Public Methods:** match, execute, schema

### AIToolkitMaster

- **File:** `ai_toolkit_master.py`
- **Inherits From:** `Tool`
- **Public Methods:** match, execute, get_toolkit_stats, schema

### Tool

- **File:** `base.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### ContinueDocsTool

- **File:** `continue_docs_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Continue documentation integration for enhanced code awareness
- **Public Methods:** match, execute, schema

### MessageRecord

- **File:** `conversation_cleanup.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** is_noise, attachments

### DatabaseTool

- **File:** `database_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for database operations and persistent storage
- **Public Methods:** match, execute, store_data, query_data, create_table
  ... and 3 more

### DeepWikiMCPTool

- **File:** `deepwiki_mcp_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** DeepWiki MCP integration for enhanced knowledge access
- **Public Methods:** name, description, match, execute, schema

### DirectorySortTool

- **File:** `directory_sort_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, sort_directory, generate_report, schema

### DynamicCodeExecutor

- **File:** `dynamic_code_executor.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for dynamic code execution and orchestration within ULTRON Agent

This tool provides:
- Safe dynamic Python code execution
- External service integration (NVIDIA NIM, APIs)
- Code analysis and va
- **Public Methods:** match, execute, orchestrate_with_maverick, contact_maverick, perform_copilot_analysis
  ... and 4 more

### EnhancedErrorHandler

- **File:** `enhanced_error_handler.py`
- **Inherits From:** `Exception`
- **Description:** Tool for enhanced error handling, circuit breakers, and recovery management
- **Public Methods:** call, register_recovery_strategy, attempt_recovery, match, execute
  ... and 6 more

### EnhancedNLPTool

- **File:** `enhanced_nlp_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for advanced natural language processing using spaCy
- **Public Methods:** match, execute, analyze_text, extract_entities, analyze_sentiment
  ... and 2 more

### EnhancedOCRTool

- **File:** `enhanced_ocr_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Enhanced OCR with preprocessing and MCP integration
- **Public Methods:** match, execute, schema

### EnhancedVoiceTool

- **File:** `enhanced_voice_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Enhanced voice processing with context awareness
- **Public Methods:** match, schema

### EvolutionMonitorTool

- **File:** `evolution_monitor_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for monitoring and managing ULTRON's self-evolution process.
Provides real-time insights into code improvements and system evolution.
- **Public Methods:** match, execute, schema

### FileMonitorTool

- **File:** `file_monitor_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, start_monitoring, check_changes, stop_monitoring
  ... and 2 more

### GDriveAddonTool

- **File:** `gdrive_addon_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### GitHubModelsTool

- **File:** `github_models_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Tool for accessing GitHub Models API
- **Public Methods:** name, description, match, execute, get_available_models
  ... and 2 more

### GoogleDriveTool

- **File:** `google_drive_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** authenticate, list_folder, download_file, match, execute

### HelloTool

- **File:** `hello_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### ImageDescriptionTool

- **File:** `image_description_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Tool for detailed image description and analysis
- **Public Methods:** name, description, match, execute, analyze_screenshot
  ... and 1 more

### ImageGenerationTool

- **File:** `image_generation_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### LangflowMCPTool

- **File:** `langflow_mcp_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Langflow MCP integration for workflow automation with proper MCP support
- **Public Methods:** name, description, match, execute, schema

### LangflowTool

- **File:** `langflow_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for interacting with Langflow within ULTRON Agent

This tool allows users to execute Langflow workflows, manage
flow configurations, and monitor execution status.
- **Public Methods:** match, execute, schema

### LangflowWorkflowTool

- **File:** `langflow_workflow_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Langflow Workflow integration for ULTRON Agent

Enables:
- Visual workflow creation in Langflow
- Workflow execution from ULTRON
- 5 pre-built templates
- Execution history tracking
- **Public Methods:** add_template, get_template, list_templates, create_instance, record_execution
  ... and 5 more

### MCPEnhancedTool

- **File:** `mcp_enhanced_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Enhanced MCP server integration for ULTRON Agent
- **Public Methods:** name, description, match, execute, get_memory_context
  ... and 1 more

### MinimaxAITool

- **File:** `minimax_ai_tool.py`
- **Inherits From:** `Tool`
- **Public Methods:** match, execute, schema

### MultimodalVisionTool

- **File:** `multimodal_vision_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for multimodal vision analysis using NVIDIA NIM vision-language models
- **Public Methods:** match, execute, analyze_image, get_help, schema

### OpenAIAgentTool

- **File:** `openai_agent_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** OpenAI Assistants and Agents integration
- **Public Methods:** name, description, match, execute, schema

### OpenAIAssistantTool

- **File:** `openai_assistant_tool.py`
- **Inherits From:** `Tool`
- **Public Methods:** schema, match, execute

### OpenAIComputerUseTool

- **File:** `openai_computer_use_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** High-level wrapper that exposes Open Interface autopilot as a tool.
- **Public Methods:** match, execute, schema

### OpenAITools

- **File:** `openai_tools.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** OpenAI tools integration for ULTRON

### OrchestrationTool

- **File:** `orchestration_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** AI Agent Orchestration and Workflow Management Tool
- **Public Methods:** name, description, match, execute, schema

### PerformanceDashboardTool

- **File:** `performance_dashboard_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Real-time performance monitoring dashboard.
Provides insights into system performance, traces, and anomalies.
- **Public Methods:** match, execute, schema

### PerformanceMonitor

- **File:** `performance_monitor.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for monitoring system and application performance metrics
- **Public Methods:** match, execute, start_monitoring, stop_monitoring, get_current_system_stats
  ... and 8 more

### PersonaSelector

- **File:** `persona_selector.py`
- **Inherits From:** `Tool`
- **Public Methods:** match, execute, schema

### PineconeTool

- **File:** `pinecone_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

### reasoning_pipeline_tool.py

- **File:** `reasoning_pipeline_tool.py`
- **Inherits From:** ToolInterface (standard)
- ⚠️ **Parse Error:** invalid syntax (<unknown>, line 112)

### RepomixTool

- **File:** `repomix_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Advanced codebase analysis tool using Repomix for AI-powered understanding.

Capabilities:
- Package codebases for LLM consumption
- Natural language code search
- Remote repository analysis
- Real-ti
- **Public Methods:** name, description, match, execute, schema

### SelfAwarenessTool

- **File:** `self_awareness_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tool for ULTRON self-awareness, identity maintenance, and self-prompting

This tool provides ULTRON with the ability to:
- Affirm its identity and mission
- Self-reflect on actions and decisions
- Mai
- **Public Methods:** match, execute, schema

### SmartScreenshotTool

- **File:** `smart_screenshot_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Smart screenshot tool with OCR analysis
- **Public Methods:** name, description, match, execute, schema

### SSHServerTool

- **File:** `ssh_server_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** Manages SSH reverse tunnel server for remote Android/Termux connections
- **Public Methods:** name, description, match, execute, start_server
  ... and 9 more

### StableDiffusionTool

- **File:** `stable_diffusion_tool.py`
- **Inherits From:** `ToolInterface`
- **Description:** GPU-accelerated Stable Diffusion image generation
- **Public Methods:** name, description, match, execute, schema

### ToolLoader

- **File:** `tool_loader.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Dynamic tool discovery and loading with error isolation
- **Public Methods:** discover_tools, load_tool_module, load_all_tools, reload_tool, get_tool
  ... and 2 more

### ToolPerformanceTracker

- **File:** `tool_performance_tracker.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, track_execution, get_best_tools, get_tool_combinations
  ... and 2 more

### TorSearchTool

- **File:** `tor_search_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Tor-enabled deep web search for research purposes
- **Public Methods:** match, execute, get_tor_status, schema

### UncensoredSearchTool

- **File:** `uncensored_search_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Description:** Uncensored search bypassing filters and restrictions
- **Public Methods:** match, execute, schema

### VercelAssistantTool

- **File:** `vercel_assistant_tool.py`
- **Inherits From:** `Tool`
- **Public Methods:** schema, match, execute

### WorkflowEditorTool

- **File:** `workflow_editor_tool.py`
- **Inherits From:** ToolInterface (standard)
- **Public Methods:** match, execute, schema

---


## Runtime Tool Discovery


To discover all available tools at runtime:

```python
from tools.tool_loader import ToolLoader

# Initialize tool loader
loader = ToolLoader()
tools = loader.load_all_tools()

# List available tools
for tool_name, tool_instance in tools.items():
    print(f"{tool_name}: {tool_instance.__class__.__name__}")
```

**Key Points:**
- Tools are auto-discovered from the `tools/` directory
- All tool classes must inherit from `ToolInterface`
- New tools are automatically loaded—no manual registration needed
- Tool loading happens in `tools/tool_loader.py`


## Adding New Tools


1. Create a new Python file in the `tools/` directory (e.g., `my_tool.py`)
2. Inherit from `ToolInterface`:

```python
from tools.tool_interface import ToolInterface

class MyTool(ToolInterface):
    def __init__(self):
        super().__init__("my_tool", "Tool description")
    
    def execute(self, **kwargs):
        # Your implementation
        return result
```

3. The tool will be automatically discovered on next startup
4. No manual registration or import needed
