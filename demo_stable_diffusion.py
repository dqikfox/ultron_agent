#!/usr/bin/env python3
"""
ULTRON Stable Diffusion Integration Demo
Demonstrates how to use the enhanced image generation capabilities
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_text_commands():
    """Demo the text command interface"""
    print("🎨 ULTRON Stable Diffusion Demo")
    print("=" * 50)
    
    # Mock the tool for demonstration
    try:
        # Mock dependencies for demo
        sys.modules['PIL'] = type(sys)('PIL')
        sys.modules['PIL.Image'] = type(sys)('PIL.Image')
        
        from tools.image_generation_tool import ImageGenerationTool
        
        # Create tool instance
        class MockConfig:
            data = {}
        
        tool = ImageGenerationTool(MockConfig())
        
        print(f"✅ Loaded tool: {tool.name}")
        print(f"📝 Description: {tool.description}")
        print()
        
        # Demo commands
        demo_commands = [
            "generate image of a futuristic city at sunset",
            "create cyberpunk robot with neon lights width:1024 height:768",
            "stable diffusion realistic portrait of a woman steps:25 guidance:8.0",
            "make anime style character with blue hair",
            "draw fantasy dragon in a magical forest high quality"
        ]
        
        print("📋 DEMO COMMANDS:")
        print("-" * 30)
        
        for i, command in enumerate(demo_commands, 1):
            print(f"\n{i}. Command: \"{command}\"")
            
            # Test matching
            matches = tool.match(command)
            print(f"   🔍 Matches: {matches}")
            
            if matches:
                # Parse parameters
                params = tool.parse_parameters(command)
                
                print(f"   📝 Prompt: \"{params['prompt']}\"")
                print(f"   📐 Size: {params['width']}x{params['height']}")
                print(f"   ⚙️ Steps: {params['steps']}, Guidance: {params['guidance_scale']}")
                
                if params['negative_prompt'] != tool.default_params['negative_prompt']:
                    print(f"   ❌ Negative: \"{params['negative_prompt']}\"")
                
                # Simulate execution (without actual generation)
                print(f"   🎯 Status: Would generate {params['num_images']} image(s)")
            else:
                print(f"   ⚠️ Command not recognized as image generation")
        
        print("\n" + "=" * 50)
        print("💡 USAGE TIPS:")
        print("• Use natural language: 'generate image of...'")
        print("• Add parameters: 'width:1024 height:768 steps:30'")
        print("• Include style: 'cyberpunk style', 'realistic', 'anime'")
        print("• Quality hints: 'high quality', 'detailed', 'professional'")
        print("• Negative prompts: 'avoid: blurry, ugly'")
        
        print("\n🌐 BACKENDS:")
        print("• Colab Notebook (Recommended): Free GPU in the cloud")
        print("• Local Server: Your own hardware")
        print("• API Services: Third-party Stable Diffusion APIs")
        
        print("\n🎮 INTERFACES:")
        print("• Text Commands: Natural language in ULTRON chat")
        print("• GUI Studio: Advanced interface with controls")
        print("• Web Interface: Browser-based generation")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_api_usage():
    """Demo API usage example"""
    print("\n🌐 API USAGE EXAMPLE:")
    print("-" * 30)
    
    api_example = '''
# Example: Using the Colab notebook API
import requests

# Colab endpoint (get from notebook output)
endpoint = "https://abc123.ngrok.io"

# Generate image
response = requests.post(f"{endpoint}/generate", json={
    "prompt": "A futuristic AI robot assistant",
    "negative_prompt": "ugly, blurry, poor quality",
    "width": 768,
    "height": 768,
    "steps": 25,
    "guidance_scale": 7.5,
    "num_images": 1
})

if response.status_code == 200:
    result = response.json()
    if result["success"]:
        print(f"Generated {result['count']} images!")
        
        # Save the first image
        import base64
        img_data = base64.b64decode(result["images"][0]["base64"])
        with open("generated_image.png", "wb") as f:
            f.write(img_data)
else:
    print(f"Error: {response.status_code}")
'''
    
    print(api_example)

def demo_colab_setup():
    """Demo Colab setup instructions"""
    print("\n📓 COLAB SETUP GUIDE:")
    print("-" * 30)
    
    setup_steps = [
        "1. Open Google Colab (colab.research.google.com)",
        "2. Upload stable_diffusion_colab.ipynb",
        "3. Set Runtime > Change runtime type > GPU",
        "4. Run all cells (Ctrl+F9)",
        "5. Wait for model loading (5-10 minutes first time)",
        "6. Copy the ngrok URL from the output",
        "7. In ULTRON GUI: Settings > Add Colab Endpoint",
        "8. Paste the URL and click Add",
        "9. Start generating images!"
    ]
    
    for step in setup_steps:
        print(f"   {step}")
    
    print("\n💡 Colab Tips:")
    print("• Use GPU runtime for best performance")
    print("• Keep the notebook active to avoid disconnection")  
    print("• Free tier gives ~12 hours of GPU time")
    print("• Colab Pro offers longer sessions and better GPUs")

def main():
    """Run the demo"""
    try:
        success = demo_text_commands()
        
        if success:
            demo_api_usage()
            demo_colab_setup()
            
            print("\n🎉 DEMO COMPLETE!")
            print("Ready to generate amazing images with ULTRON Agent!")
            
            # Show file locations
            print(f"\n📁 FILES CREATED:")
            files = [
                "stable_diffusion_colab.ipynb - Colab notebook",
                "stable_diffusion_gui.py - Advanced GUI interface", 
                "tools/image_generation_tool.py - Enhanced tool",
                "STABLE_DIFFUSION_GUIDE.md - Complete documentation"
            ]
            
            for file_info in files:
                file_path = file_info.split(' - ')[0]
                if (project_root / file_path).exists():
                    print(f"   ✅ {file_info}")
                else:
                    print(f"   ❌ {file_info}")
            
            return True
        else:
            print("❌ Demo failed")
            return False
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)