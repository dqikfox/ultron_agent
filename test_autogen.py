"""
Test AutoGen Multi-Agent Automation
"""
import asyncio
import os

async def test_autogen_basic():
    """Test basic AutoGen setup"""
    print("\n[TEST] AutoGen Basic Setup")
    try:
        import autogen
        print("  [OK] AutoGen installed")
        
        # Test config
        config_list = [{
            "model": "gpt-4",
            "api_key": os.getenv("OPENAI_API_KEY", "test")
        }]
        
        llm_config = {"config_list": config_list, "timeout": 120}
        print("  [OK] Config created")
        return True
        
    except ImportError:
        print("  [FAIL] AutoGen not installed: pip install pyautogen")
        return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_autogen_agents():
    """Test AutoGen agent creation"""
    print("\n[TEST] AutoGen Agent Creation")
    try:
        import autogen
        
        config_list = [{
            "model": "gpt-4",
            "api_key": os.getenv("OPENAI_API_KEY", "test")
        }]
        
        # Create assistant
        assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config={"config_list": config_list}
        )
        print("  [OK] Assistant agent created")
        
        # Create user proxy
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1
        )
        print("  [OK] User proxy created")
        return True
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_autogen_conversation():
    """Test AutoGen conversation"""
    print("\n[TEST] AutoGen Conversation")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  [SKIP] OPENAI_API_KEY not set")
        return False
    
    try:
        import autogen
        
        config_list = [{"model": "gpt-4", "api_key": api_key}]
        
        assistant = autogen.AssistantAgent(
            name="assistant",
            llm_config={"config_list": config_list}
        )
        
        user_proxy = autogen.UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False
        )
        
        # Simple test conversation
        user_proxy.initiate_chat(
            assistant,
            message="What is 2+2? Reply with just the number."
        )
        
        print("  [OK] Conversation completed")
        return True
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_autogen_code_execution():
    """Test AutoGen code execution"""
    print("\n[TEST] AutoGen Code Execution")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("  [SKIP] OPENAI_API_KEY not set")
        return False
    
    try:
        import autogen
        
        config_list = [{"model": "gpt-4", "api_key": api_key}]
        
        assistant = autogen.AssistantAgent(
            name="coder",
            llm_config={"config_list": config_list}
        )
        
        executor = autogen.UserProxyAgent(
            name="executor",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config={"work_dir": "autogen_test", "use_docker": False}
        )
        
        executor.initiate_chat(
            assistant,
            message="Write Python code to calculate 10 factorial and print it."
        )
        
        print("  [OK] Code execution test completed")
        return True
        
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def main():
    print("=" * 60)
    print("AUTOGEN AUTOMATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Basic Setup", test_autogen_basic),
        ("Agent Creation", test_autogen_agents),
        ("Conversation", test_autogen_conversation),
        ("Code Execution", test_autogen_code_execution),
    ]
    
    results = []
    for name, test_func in tests:
        result = await test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "PASS" if result else "SKIP/FAIL"
        print(f"  [{status}] {name}")
    
    passed = sum(1 for _, r in results if r)
    print(f"\n{passed}/{len(results)} tests passed")

if __name__ == "__main__":
    asyncio.run(main())
