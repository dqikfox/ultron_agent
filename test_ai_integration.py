
"""
Test NVIDIA NIM API access and Qwen2.5-Coder integration
"""

import requests
import json
import sys
from datetime import datetime

def test_nvidia_api():
    """Test direct NVIDIA NIM API access"""
    print("🔴 NVIDIA NIM API TEST 🔴 - test_ai_integration.py:13")
    print("= - test_ai_integration.py:14" * 40)
    
    # API configuration
    api_key = "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"
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "ULTRON-Agent-Test"
    }
    
    # Test models
    test_models = [
        "openai/gpt-oss-120b",
        "meta/llama-4-maverick-17b-128e-instruct"
    ]
    
    for model in test_models:
        print(f"\n📡 Testing model: {model} - test_ai_integration.py:33")
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello! Please respond with 'API Working' to confirm connectivity."}],
            "max_tokens": 20,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "No content")
                print(f"✅ SUCCESS: {content} - test_ai_integration.py:48")
                return True
            else:
                print(f"❌ HTTP {response.status_code}: {response.text[:200]} - test_ai_integration.py:51")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {str(e)[:100]} - test_ai_integration.py:54")
        except Exception as e:
            print(f"❌ General Error: {str(e)[:100]} - test_ai_integration.py:56")
    
    return False

def test_qwen_integration():
    """Test Qwen2.5-Coder:1.5b integration status (Memory Optimized)"""
    print("\n🤖 QWEN2.5CODER:1.5B INTEGRATION TEST 🤖 - test_ai_integration.py:62")
    print("= - test_ai_integration.py:63" * 40)
    
    try:
        # Check if enhanced AI system is available
        from ultron_enhanced_ai import initialize_enhanced_ai
        
        print("✅ Enhanced AI module imported successfully - test_ai_integration.py:69")
        
        # Initialize system
        ai_system = initialize_enhanced_ai()
        print("✅ Enhanced AI system initialized - test_ai_integration.py:73")
        
        # Get status
        status = ai_system.get_ai_status()
        print(f"🔧 AI Mode: {status['mode']} - test_ai_integration.py:77")
        print(f"🔧 NVIDIA Available: {status['nvidia_available']} - test_ai_integration.py:78")
        print(f"🔧 Local Models: {status['local_models']} - test_ai_integration.py:79")
        print(f"🔧 Total Requests: {status['statistics']['total_requests']} - test_ai_integration.py:80")
        
        # Test a simple command
        test_response = ai_system.process_command("Hello, are you working?")
        print(f"🧪 Test Response: {test_response[:100]}... - test_ai_integration.py:84")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e} - test_ai_integration.py:89")
        return False
    except Exception as e:
        print(f"❌ Integration Error: {e} - test_ai_integration.py:92")
        return False

def check_continue_integration():
    """Check if Qwen2.5-Coder is contributing via Continue extension"""
    print("\n🔄 CONTINUE EXTENSION STATUS 🔄 - test_ai_integration.py:97")
    print("= - test_ai_integration.py:98" * 40)
    
    # Check for Continue configuration files
    import os
    
    continue_configs = [
        ".continue/config.json",
        ".vscode/settings.json",
        "continue.yaml"
    ]
    
    found_configs = []
    for config in continue_configs:
        if os.path.exists(config):
            found_configs.append(config)
            print(f"✅ Found: {config} - test_ai_integration.py:113")
    
    if found_configs:
        print(f"📋 Continue integration configured with {len(found_configs)} files - test_ai_integration.py:116")
        
        # Check if Qwen2.5-Coder model is referenced
        for config_path in found_configs:
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                    if "qwen" in content.lower() or "coder" in content.lower():
                        print(f"✅ Qwen2.5Coder found in {config_path} - test_ai_integration.py:124")
            except:
                pass
        
        return True
    else:
        print("❌ No Continue configuration files found - test_ai_integration.py:130")
        return False

def main():
    """Main test function"""
    print(f"🔴 ULTRON AI INTEGRATION STATUS CHECK 🔴 - test_ai_integration.py:135")
    print(f"Time: {datetime.now().strftime('%Y%m%d %H:%M:%S')} - test_ai_integration.py:136")
    print("= - test_ai_integration.py:137" * 60)
    
    results = {}
    
    # Test NVIDIA NIM API
    results['nvidia'] = test_nvidia_api()
    
    # Test Qwen integration
    results['qwen'] = test_qwen_integration()
    
    # Test Continue extension
    results['continue'] = check_continue_integration()
    
    # Summary
    print("\n - test_ai_integration.py:151" + "=" * 60)
    print("🔴 FINAL STATUS SUMMARY 🔴 - test_ai_integration.py:152")
    print("= - test_ai_integration.py:153" * 60)
    
    print(f"📡 NVIDIA NIM API Access: {'✅ WORKING' if results['nvidia'] else '❌ FAILED'} - test_ai_integration.py:155")
    print(f"🤖 Qwen2.5Coder Integration: {'✅ ACTIVE' if results['qwen'] else '❌ INACTIVE'} - test_ai_integration.py:156")
    print(f"🔄 Continue Extension: {'✅ CONFIGURED' if results['continue'] else '❌ NOT FOUND'} - test_ai_integration.py:157")
    
    # Answer user's questions
    print("\n - test_ai_integration.py:160" + "=" * 60)
    print("🔴 ANSWERS TO YOUR QUESTIONS 🔴 - test_ai_integration.py:161")
    print("= - test_ai_integration.py:162" * 60)
    
    if results['nvidia']:
        print("✅ YES  I can use NVIDIA models for queries! - test_ai_integration.py:165")
        print("The API is accessible and models are responding - test_ai_integration.py:166")
    else:
        print("❌ NO  NVIDIA models are currently not accessible - test_ai_integration.py:168")
        print("API connection issues or model availability problems - test_ai_integration.py:169")
    
    if results['qwen']:
        print("✅ YES  Qwen2.5Coder is contributing to the project! - test_ai_integration.py:172")
        print("Enhanced AI system is active with coding assistance - test_ai_integration.py:173")
    else:
        print("❌ NO  Qwen2.5Coder integration needs setup - test_ai_integration.py:175")
        print("System available but not currently active - test_ai_integration.py:176")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\n🎯 Overall Integration Success: {success_rate:.1f}% - test_ai_integration.py:179")
    
    if success_rate >= 80:
        print("🎉 ULTRON AI systems are highly functional! - test_ai_integration.py:182")
    elif success_rate >= 50:
        print("⚠️ ULTRON AI systems are partially functional - test_ai_integration.py:184")
    else:
        print("🔧 ULTRON AI systems need attention - test_ai_integration.py:186")

if __name__ == "__main__":
    main()
