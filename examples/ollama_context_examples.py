"""
Ollama Context System Usage Examples

Demonstrates how to use the new Ollama context provider with any model.
"""

import asyncio
from brain import UltronBrain
from memory import Memory


async def example_1_basic_usage():
    """Example 1: Basic usage with automatic context injection"""
    print("=" * 60)
    print("Example 1: Basic Usage with Any Ollama Model")
    print("=" * 60)
    
    # Create components
    config = {
        'ollama_base_url': 'http://localhost:11434',
        'llm_model': 'llama3.1',  # Works with ANY Ollama model
        'ollama_include_memory': True,
        'ollama_include_tools': True,
        'ollama_include_capabilities': True
    }
    
    memory = Memory()
    tools = {}
    
    # Create brain with context provider
    brain = UltronBrain(config, tools, memory)
    
    # Add some conversation to memory
    memory.add_to_short_term("User asked about the weather")
    memory.add_to_short_term("Assistant provided forecast")
    
    # Send query - context is automatically injected!
    response = await brain.direct_chat("What did we just discuss?")
    print(f"\nQuery: What did we just discuss?")
    print(f"Response: {response[:200]}...")
    
    print("\n✅ Context automatically includes conversation history!\n")


async def example_2_model_switching():
    """Example 2: Switching between different models"""
    print("=" * 60)
    print("Example 2: Using Different Models")
    print("=" * 60)
    
    config = {
        'ollama_base_url': 'http://localhost:11434',
        'ollama_include_memory': True,
        'ollama_include_tools': True
    }
    
    memory = Memory()
    tools = {}
    
    models = ['llama3.1', 'llava:7b', 'qwen3-coder:480b-cloud']
    
    for model in models:
        print(f"\nTesting model: {model}")
        config['llm_model'] = model
        
        brain = UltronBrain(config, tools, memory)
        
        # Get model info
        model_info = brain.get_model_info(model)
        print(f"  Capabilities: vision={model_info.get('supports_vision')}, "
              f"function_calling={model_info.get('supports_function_calling')}")
        
        # Each model receives the same context automatically!
        response = await brain.direct_chat("Hello, what are you?")
        print(f"  Response preview: {response[:100]}...")
    
    print("\n✅ Same context works with all models!\n")


async def example_3_with_tools():
    """Example 3: Using tools with context"""
    print("=" * 60)
    print("Example 3: Context with Tools")
    print("=" * 60)
    
    # Mock tool for demonstration
    class WebSearchTool:
        def match(self, command):
            return 'search' in command.lower()
        
        def execute(self, command):
            return "Search results..."
        
        def schema(self):
            return {
                'name': 'web_search',
                'description': 'Search the web for information',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string', 'description': 'Search query'}
                    },
                    'required': ['query']
                }
            }
    
    config = {
        'ollama_base_url': 'http://localhost:11434',
        'llm_model': 'llama3.1',
        'ollama_include_tools': True
    }
    
    memory = Memory()
    tools = {'websearch': WebSearchTool()}
    
    brain = UltronBrain(config, tools, memory)
    
    # Model receives information about available tools
    response = await brain.direct_chat("What tools do you have access to?")
    print(f"\nQuery: What tools do you have access to?")
    print(f"Response: {response[:300]}...")
    
    print("\n✅ Model is aware of available tools!\n")


async def example_4_context_stats():
    """Example 4: Monitoring context state"""
    print("=" * 60)
    print("Example 4: Context Statistics")
    print("=" * 60)
    
    config = {
        'ollama_base_url': 'http://localhost:11434',
        'llm_model': 'llama3.1',
        'ollama_include_memory': True,
        'ollama_include_tools': True
    }
    
    memory = Memory()
    memory.add_to_short_term("Item 1")
    memory.add_to_short_term("Item 2")
    memory.add_to_short_term("Item 3")
    
    tools = {
        'tool1': type('Tool', (), {'schema': lambda: {'name': 'tool1', 'description': 'Test'}})(),
        'tool2': type('Tool', (), {'schema': lambda: {'name': 'tool2', 'description': 'Test'}})()
    }
    
    brain = UltronBrain(config, tools, memory)
    
    # Get context statistics
    stats = brain.get_ollama_context_stats()
    
    print("\nContext Statistics:")
    print(f"  Memory available: {stats.get('memory_available')}")
    print(f"  Short-term items: {stats.get('short_term_memory_count')}")
    print(f"  Tools count: {stats.get('tools_count')}")
    print(f"  Sections enabled: {stats.get('context_sections_enabled')}")
    
    print("\n✅ Full visibility into context state!\n")


async def example_5_dynamic_updates():
    """Example 5: Dynamic context updates"""
    print("=" * 60)
    print("Example 5: Dynamic Context Updates")
    print("=" * 60)
    
    config = {
        'ollama_base_url': 'http://localhost:11434',
        'llm_model': 'llama3.1'
    }
    
    memory = Memory()
    tools = {}
    
    brain = UltronBrain(config, tools, memory)
    
    print("\nInitial state:")
    stats = brain.get_ollama_context_stats()
    print(f"  Tools: {stats.get('tools_count')}")
    
    # Add new tools dynamically
    new_tools = {
        'new_tool': type('Tool', (), {'schema': lambda: {'name': 'new_tool', 'description': 'New'}})()
    }
    
    brain.update_context_provider(tools=new_tools)
    
    print("\nAfter update:")
    stats = brain.get_ollama_context_stats()
    print(f"  Tools: {stats.get('tools_count')}")
    
    print("\n✅ Context updates automatically!\n")


async def example_6_model_selection():
    """Example 6: Automatic model selection for tasks"""
    print("=" * 60)
    print("Example 6: Smart Model Selection")
    print("=" * 60)
    
    config = {
        'ollama_base_url': 'http://localhost:11434'
    }
    
    brain = UltronBrain(config, {}, Memory())
    
    # Find best models for different tasks
    tasks = ['vision', 'coding', 'reasoning', 'general']
    
    print("\nRecommended models for tasks:")
    for task in tasks:
        best_model = brain.find_best_model_for_task(task)
        if best_model:
            print(f"  {task}: {best_model}")
        else:
            print(f"  {task}: No specific model found")
    
    print("\n✅ Automatic model selection based on capabilities!\n")


async def example_7_configuration():
    """Example 7: Configuration options"""
    print("=" * 60)
    print("Example 7: Configuration Control")
    print("=" * 60)
    
    # Minimal context
    config_minimal = {
        'ollama_base_url': 'http://localhost:11434',
        'llm_model': 'llama3.1',
        'ollama_include_memory': False,
        'ollama_include_tools': False,
        'ollama_include_capabilities': False
    }
    
    print("\nConfiguration 1: Minimal context")
    print("  Memory: OFF, Tools: OFF, Capabilities: OFF")
    
    # Full context
    config_full = {
        'ollama_base_url': 'http://localhost:11434',
        'llm_model': 'llama3.1',
        'ollama_include_memory': True,
        'ollama_include_tools': True,
        'ollama_include_capabilities': True,
        'ollama_max_memory_items': 20,
        'ollama_max_tool_schemas': 30
    }
    
    print("\nConfiguration 2: Full context")
    print("  Memory: ON (20 items), Tools: ON (30 schemas), Capabilities: ON")
    
    print("\n✅ Fine-grained control over context!\n")


async def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("OLLAMA CONTEXT SYSTEM - USAGE EXAMPLES")
    print("=" * 60 + "\n")
    
    try:
        # Note: These examples require Ollama to be running
        # If Ollama is not available, the examples will show errors
        # but demonstrate the API usage
        
        await example_1_basic_usage()
        await example_2_model_switching()
        await example_3_with_tools()
        await example_4_context_stats()
        await example_5_dynamic_updates()
        await example_6_model_selection()
        await example_7_configuration()
        
        print("\n" + "=" * 60)
        print("ALL EXAMPLES COMPLETED")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nNote: Examples require Ollama running at localhost:11434")
        print(f"Error: {e}")
        print("\nThe API examples above show how to use the system.")


if __name__ == '__main__':
    asyncio.run(main())
