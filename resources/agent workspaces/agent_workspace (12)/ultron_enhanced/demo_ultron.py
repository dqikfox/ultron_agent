#!/usr/bin/env python3
"""
ULTRON AI - Comprehensive Feature Demo
Demonstrates all capabilities of the ULTRON AI system
"""

import asyncio
import time
import logging
from pathlib import Path
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("UltronDemo")

class UltronDemo:
    """Comprehensive demo of ULTRON AI capabilities"""
    
    def __init__(self):
        self.ultron = None
    
    async def initialize_ultron(self):
        """Initialize ULTRON for demo"""
        try:
            from ultron_main import UltronCore
            self.ultron = UltronCore()
            logger.info("ULTRON initialized for demo")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ULTRON: {e}")
            return False
    
    async def demo_voice_recognition(self):
        """Demo voice recognition capabilities"""
        logger.info("🎤 DEMO: Voice Recognition System")
        
        if not self.ultron.voice_processor:
            logger.warning("Voice processor not available")
            return
        
        try:
            # Test voice recognition
            logger.info("Testing voice recognition...")
            result = self.ultron.voice_processor.test_voice_recognition()
            
            if result:
                logger.info("✅ Voice recognition test passed")
            else:
                logger.warning("⚠️ Voice recognition test failed")
            
            # Show performance metrics
            metrics = self.ultron.voice_processor.get_performance_metrics()
            logger.info(f"Voice metrics: {json.dumps(metrics, indent=2)}")
            
            # Demo text-to-speech
            self.ultron.voice_processor.speak("Voice recognition system is working correctly.")
            
        except Exception as e:
            logger.error(f"Voice demo error: {e}")
    
    async def demo_vision_system(self):
        """Demo vision and OCR capabilities"""
        logger.info("👁️ DEMO: Vision and OCR System")
        
        if not self.ultron.vision_system:
            logger.warning("Vision system not available")
            return
        
        try:
            # Take a screenshot
            logger.info("Taking screenshot...")
            screenshot_path = await self.ultron.vision_system.take_screenshot()
            logger.info(f"Screenshot saved: {screenshot_path}")
            
            # Analyze the screen
            logger.info("Analyzing screen content...")
            analysis = await self.ultron.vision_system.analyze_screen()
            logger.info(f"Screen analysis: {json.dumps(analysis, indent=2)}")
            
            # Show performance metrics
            metrics = self.ultron.vision_system.get_performance_metrics()
            logger.info(f"Vision metrics: {json.dumps(metrics, indent=2)}")
            
        except Exception as e:
            logger.error(f"Vision demo error: {e}")
    
    async def demo_ai_conversation(self):
        """Demo AI conversation capabilities"""
        logger.info("🤖 DEMO: AI Conversation System")
        
        test_commands = [
            "What is the current time?",
            "Tell me about the weather",
            "What can you do?",
            "How are you today?",
            "Explain artificial intelligence"
        ]
        
        for command in test_commands:
            try:
                logger.info(f"Processing: '{command}'")
                
                # Process command
                await self.ultron._process_voice_command(command)
                
                # Small delay between commands
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"AI conversation error: {e}")
    
    async def demo_system_automation(self):
        """Demo system automation capabilities"""
        logger.info("⚙️ DEMO: System Automation")
        
        if not self.ultron.system_automation:
            logger.warning("System automation not available")
            return
        
        try:
            # Get system information
            system_info = self.ultron.system_automation.get_system_info()
            logger.info(f"System info: {json.dumps(system_info, indent=2)}")
            
            # List running processes (top 10)
            process_result = await self.ultron.system_automation.manage_process("list", "")
            if process_result.get("success"):
                processes = process_result.get("processes", [])[:10]
                logger.info(f"Top 10 processes: {json.dumps(processes, indent=2)}")
            
            # Get performance metrics
            perf_metrics = self.ultron.system_automation.get_performance_metrics()
            logger.info(f"Performance metrics: {json.dumps(perf_metrics, indent=2)}")
            
            # Get security status
            security_status = self.ultron.system_automation.get_security_status()
            logger.info(f"Security status: {json.dumps(security_status, indent=2)}")
            
        except Exception as e:
            logger.error(f"System automation demo error: {e}")
    
    async def demo_file_sorting(self):
        """Demo file sorting AI capabilities"""
        logger.info("📁 DEMO: AI File Sorting System")
        
        try:
            # Import file sorter
            from core.file_sorter import FileSorter
            
            file_sorter = FileSorter(self.ultron.config)
            
            # Create some test files for demonstration
            test_dir = Path("D:/ULTRON/test_files")
            test_dir.mkdir(exist_ok=True)
            
            test_files = [
                ("test_document.pdf", "PDF document content"),
                ("example_code.py", "def hello():\n    print('Hello World')"),
                ("image_file.jpg", "Binary image data"),
                ("data_file.csv", "name,age\nJohn,30\nJane,25"),
                ("config_file.txt", "[settings]\ntheme=dark\nvolume=50")
            ]
            
            # Create test files
            for filename, content in test_files:
                test_file = test_dir / filename
                if filename.endswith(('.jpg', '.png')):
                    # Create a simple image file
                    from PIL import Image as PILImage
                    img = PILImage.new('RGB', (100, 100), color='red')
                    img.save(test_file)
                else:
                    test_file.write_text(content)
            
            logger.info(f"Created test files in: {test_dir}")
            
            # Sort the test directory
            result = await file_sorter.sort_directory(test_dir)
            logger.info(f"File sorting result: {json.dumps(result, indent=2)}")
            
            # Get sorting statistics
            stats = file_sorter.get_statistics()
            logger.info(f"File sorting stats: {json.dumps(stats, indent=2)}")
            
            # Clean up test files
            import shutil
            shutil.rmtree(test_dir, ignore_errors=True)
            logger.info("Test files cleaned up")
            
        except Exception as e:
            logger.error(f"File sorting demo error: {e}")
    
    async def demo_web_interface(self):
        """Demo web interface capabilities"""
        logger.info("🌐 DEMO: Web Interface")
        
        if not self.ultron.web_server:
            logger.warning("Web server not available")
            return
        
        try:
            # Start web server
            await self.ultron.web_server.start()
            
            # Show server status
            status = self.ultron.web_server.get_server_status()
            logger.info(f"Web server status: {json.dumps(status, indent=2)}")
            
            logger.info(f"🌐 Web interface available at: http://localhost:{self.ultron.config.web_port}")
            logger.info("You can now test the Pokedex-style interface in your browser!")
            
            # Wait a bit for testing
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Web interface demo error: {e}")
    
    async def demo_performance_monitoring(self):
        """Demo performance monitoring capabilities"""
        logger.info("📊 DEMO: Performance Monitoring")
        
        try:
            # Get overall system status
            status = self.ultron.get_status()
            logger.info(f"ULTRON status: {json.dumps(status, indent=2)}")
            
            # Performance stress test
            logger.info("Running performance stress test...")
            
            start_time = time.time()
            
            # Simulate multiple operations
            tasks = [
                self.ultron._get_ai_response("What is 2+2?"),
                self.ultron._get_ai_response("Tell me a joke"),
                self.ultron._get_ai_response("What time is it?")
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            
            logger.info(f"Processed {len(tasks)} AI requests in {end_time - start_time:.2f} seconds")
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"Task {i+1} failed: {response}")
                else:
                    logger.info(f"Task {i+1} response: {response[:100]}...")
            
        except Exception as e:
            logger.error(f"Performance monitoring demo error: {e}")
    
    async def demo_security_features(self):
        """Demo security features"""
        logger.info("🔒 DEMO: Security Features")
        
        try:
            # Check admin privileges
            admin_status = self.ultron.system_automation.admin_privileges
            logger.info(f"Admin privileges: {admin_status}")
            
            # Show security status
            if self.ultron.system_automation:
                security_status = self.ultron.system_automation.get_security_status()
                logger.info(f"Security status: {json.dumps(security_status, indent=2)}")
            
            # Demo activity logging
            self.ultron.system_automation.log_activity("demo", "security_demo", "testing")
            logger.info("Activity logged successfully")
            
            # Show recent activity
            recent_activity = self.ultron.system_automation.activity_log[-5:]
            logger.info(f"Recent activity: {json.dumps(recent_activity, indent=2)}")
            
        except Exception as e:
            logger.error(f"Security demo error: {e}")
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demo of all features"""
        logger.info("🚀 Starting ULTRON AI Comprehensive Demo")
        logger.info("=" * 60)
        
        if not await self.initialize_ultron():
            logger.error("Failed to initialize ULTRON for demo")
            return
        
        demos = [
            ("System Information", self.demo_system_automation),
            ("Security Features", self.demo_security_features),
            ("AI Conversation", self.demo_ai_conversation),
            ("Vision System", self.demo_vision_system),
            ("Voice Recognition", self.demo_voice_recognition),
            ("File Sorting AI", self.demo_file_sorting),
            ("Performance Monitoring", self.demo_performance_monitoring),
            ("Web Interface", self.demo_web_interface)
        ]
        
        for demo_name, demo_func in demos:
            try:
                logger.info("\n" + "=" * 60)
                logger.info(f"Starting Demo: {demo_name}")
                logger.info("=" * 60)
                
                await demo_func()
                
                logger.info(f"✅ Demo completed: {demo_name}")
                
                # Small delay between demos
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Demo failed: {demo_name} - {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 ULTRON AI Comprehensive Demo Completed!")
        logger.info("=" * 60)
        
        # Final system status
        final_status = self.ultron.get_status()
        logger.info(f"Final system status: {json.dumps(final_status, indent=2)}")

async def main():
    """Main demo function"""
    try:
        demo = UltronDemo()
        await demo.run_comprehensive_demo()
        
    except KeyboardInterrupt:
        logger.info("Demo cancelled by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set event loop policy for Windows
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())
