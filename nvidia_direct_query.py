"""
Direct NVIDIA Model Query for ULTRON Project Improvements
Quick script to get immediate advice from NVIDIA models
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

from nvidia_nim_router import UltronNvidiaRouter

async def query_nvidia_for_ultron_advice():
    """Query NVIDIA models for specific ULTRON project advice"""
    
    print("🔴 QUERYING NVIDIA MODELS FOR ULTRON IMPROVEMENTS 🔴")
    print("=" * 60)
    
    # Initialize NVIDIA router
    nvidia_router = UltronNvidiaRouter()
    
    # Define improvement queries
    queries = {
        "accessibility": """
        ULTRON Agent is an AI automation assistant with voice control and accessibility features for disabled users.
        Current features: High-contrast GUI, voice wake word detection, PyAutoGUI automation, multi-modal AI.
        
        As an accessibility expert, suggest 5 specific improvements to make ULTRON more accessible:
        """,
        
        "gui_enhancements": """
        ULTRON Agent has a tkinter-based GUI with dark theme and accessibility features.
        Current: High contrast colors, voice integration, button feedback, scrollable text areas.
        
        As a GUI design expert, suggest 5 specific improvements for better user experience:
        """,
        
        "voice_optimization": """
        ULTRON Agent uses voice recognition with wake word detection and multiple TTS engines.
        Current: Enhanced voice, pyttsx3, OpenAI TTS fallback, noise filtering.
        
        As a voice technology expert, suggest 5 improvements for voice interaction:
        """,
        
        "automation_safety": """
        ULTRON Agent uses PyAutoGUI for screen automation with safety features.
        Current: Emergency stop, boundary checking, user confirmation prompts.
        
        As a safety engineer, suggest 5 improvements for safer automation:
        """,
        
        "ai_integration": """
        ULTRON Agent integrates NVIDIA NIM, Qwen2.5-Coder, and local models.
        Current: Hybrid routing, fallback systems, context management.
        
        As an AI systems architect, suggest 5 improvements for AI integration:
        """
    }
    
    # Query each area
    all_advice = {}
    
    for area, query in queries.items():
        print(f"\n🤖 Querying for {area.replace('_', ' ').title()}...")
        
        try:
            # Switch to best model for this type of query
            if area in ["accessibility", "gui_enhancements"]:
                nvidia_router.route_model("gpt-oss")
            elif area == "ai_integration":
                nvidia_router.route_model("llama")
            else:
                nvidia_router.route_model("gpt-oss")
            
            # Get response
            response = await nvidia_router.ask_nvidia_async(
                query,
                max_tokens=800,
                temperature=0.7
            )
            
            all_advice[area] = {
                "query": query[:100] + "...",
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "model": nvidia_router.current_model
            }
            
            print(f"✅ Received {len(response)} characters of advice")
            print(f"📋 Preview: {response[:150]}...")
            
        except Exception as e:
            print(f"❌ Error querying {area}: {e}")
            all_advice[area] = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Generate comprehensive report
    print("\n" + "=" * 60)
    print("🔴 COMPREHENSIVE ULTRON IMPROVEMENT ADVICE 🔴")
    print("=" * 60)
    
    report_lines = []
    report_lines.append("# ULTRON Agent Improvement Recommendations")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("Source: NVIDIA NIM AI Models\n")
    
    for area, advice in all_advice.items():
        report_lines.append(f"## {area.replace('_', ' ').title()}")
        report_lines.append("-" * 40)
        
        if "error" in advice:
            report_lines.append(f"❌ Error: {advice['error']}\n")
        else:
            report_lines.append(f"**Model:** {advice.get('model', 'Unknown')}")
            report_lines.append(f"**Generated:** {advice['timestamp'][:16]}")
            report_lines.append("")
            report_lines.append(advice['response'])
            report_lines.append("")
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"ultron_nvidia_advice_{timestamp}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"📄 Full report saved to: {report_file}")
    
    # Display priority recommendations
    print("\n" + "=" * 60)
    print("🎯 TOP PRIORITY RECOMMENDATIONS")
    print("=" * 60)
    
    priority_count = 1
    for area, advice in all_advice.items():
        if "error" not in advice:
            print(f"\n{priority_count}. {area.replace('_', ' ').title().upper()}")
            print("-" * 30)
            
            # Extract first few lines as priority summary
            lines = advice['response'].split('\n')
            for line in lines[:3]:
                if line.strip():
                    print(f"   • {line.strip()}")
            
            priority_count += 1
            
            if priority_count > 3:  # Show top 3 priorities
                break
    
    print("\n🔴 NVIDIA MODEL QUERY COMPLETE 🔴")
    return all_advice

async def test_quick_query():
    """Test a quick query to ensure system is working"""
    
    print("🔴 TESTING NVIDIA MODEL CONNECTIVITY 🔴")
    print("=" * 50)
    
    try:
        router = UltronNvidiaRouter()
        
        test_query = "Hello! Please confirm you're working and ready to help improve ULTRON Agent."
        
        response = await router.ask_nvidia_async(
            test_query,
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"✅ NVIDIA Model Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

async def main():
    """Main function"""
    
    print("🔴 ULTRON PROJECT NVIDIA ADVISOR 🔴")
    print("=" * 50)
    
    # Test connectivity first
    if await test_quick_query():
        print("\n✅ NVIDIA models are accessible!")
        print("Proceeding with comprehensive improvement query...\n")
        
        # Get comprehensive advice
        advice = await query_nvidia_for_ultron_advice()
        
        # Summary
        successful_queries = sum(1 for a in advice.values() if "error" not in a)
        total_queries = len(advice)
        
        print(f"\n🎯 Query Summary: {successful_queries}/{total_queries} successful")
        
        if successful_queries > 0:
            print("🎉 NVIDIA models provided valuable improvement advice!")
            print("Check the generated markdown report for detailed recommendations.")
        
    else:
        print("❌ NVIDIA model connectivity issues detected.")
        print("Please check your API key and network connection.")

if __name__ == "__main__":
    asyncio.run(main())
