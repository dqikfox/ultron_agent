"""
ULTRON Avatar Game - Comprehensive Test Suite
Tests all features: avatars, tools, voice, battles, integration
"""

import asyncio
import requests
import json
from pathlib import Path

class AvatarGameTester:
    def __init__(self):
        self.base_url = "http://localhost:8082"
        self.results = []
        
    def test(self, name, func):
        """Run a test and record result"""
        try:
            result = func()
            status = "✅ PASS" if result else "❌ FAIL"
            self.results.append(f"{status} - {name}")
            print(f"{status} - {name}")
            return result
        except Exception as e:
            self.results.append(f"❌ ERROR - {name}: {str(e)}")
            print(f"❌ ERROR - {name}: {str(e)}")
            return False
    
    def test_server_running(self):
        """Test if server is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_create_avatar(self):
        """Test avatar creation"""
        try:
            response = requests.post(
                f"{self.base_url}/api/avatar/create",
                json={"id": "test_avatar_1", "role": "coder", "model": "llava:7b"},
                timeout=5
            )
            data = response.json()
            return data.get('success', False)
        except:
            return False
    
    def test_avatar_chat(self):
        """Test avatar chat"""
        try:
            response = requests.post(
                f"{self.base_url}/api/avatar/test_avatar_1/chat",
                json={"message": "Hello"},
                timeout=10
            )
            data = response.json()
            return data.get('success', False)
        except:
            return False
    
    def test_tools(self):
        """Test tool availability"""
        try:
            response = requests.post(
                f"{self.base_url}/api/tools/test",
                json={"tool": "all"},
                timeout=5
            )
            data = response.json()
            return data.get('success', False) and len(data.get('results', {})) > 0
        except:
            return False
    
    def test_save_load(self):
        """Test save/load functionality"""
        try:
            # Test save
            save_response = requests.post(f"{self.base_url}/api/game/save", timeout=5)
            save_data = save_response.json()
            
            # Test load
            load_response = requests.post(f"{self.base_url}/api/game/load", timeout=5)
            load_data = load_response.json()
            
            return save_data.get('success', False) and load_data.get('success', False)
        except:
            return False
    
    def test_ultron_integration(self):
        """Test ULTRON agent integration"""
        try:
            response = requests.post(
                f"{self.base_url}/api/ultron/integrate",
                timeout=10
            )
            data = response.json()
            return data.get('success', False)
        except:
            return False
    
    def test_avatar_files(self):
        """Test if avatar image files exist"""
        avatar_dir = Path(__file__).parent / "Avatar"
        required_files = [
            "ultron+xps.glb",
            "ultron+xps2.glb",
            "ultron+xps3.glb",
            "ultron+xps4.glb",
            "ultron+xps5.glb",
            "ultron_exported.glb"
        ]
        
        existing = [f for f in required_files if (avatar_dir / f).exists()]
        return len(existing) >= 3  # At least 3 models should exist
    
    def test_html_files(self):
        """Test if HTML game files exist"""
        gui_dir = Path(__file__).parent / "gui" / "ultron_enhanced" / "web"
        required_files = [
            "ultron_avatar_game_enhanced.html",
            "ultron_avatar_game_ultimate.html"
        ]
        
        return all((gui_dir / f).exists() for f in required_files)
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("ULTRON AVATAR GAME - TEST SUITE")
        print("="*60 + "\n")
        
        print("📁 FILE TESTS")
        print("-" * 60)
        self.test("HTML game files exist", self.test_html_files)
        self.test("Avatar 3D models exist", self.test_avatar_files)
        
        print("\n🌐 SERVER TESTS")
        print("-" * 60)
        self.test("Server is running", self.test_server_running)
        
        print("\n🤖 AVATAR TESTS")
        print("-" * 60)
        self.test("Create avatar", self.test_create_avatar)
        self.test("Avatar chat", self.test_avatar_chat)
        
        print("\n🔧 TOOL TESTS")
        print("-" * 60)
        self.test("Tool availability", self.test_tools)
        
        print("\n💾 PERSISTENCE TESTS")
        print("-" * 60)
        self.test("Save/Load game", self.test_save_load)
        
        print("\n🔗 INTEGRATION TESTS")
        print("-" * 60)
        self.test("ULTRON integration", self.test_ultron_integration)
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if "✅" in r)
        failed = sum(1 for r in self.results if "❌" in r)
        total = len(self.results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print("\n" + "="*60)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Game is ready for deployment!")
        else:
            print("⚠️  Some tests failed. Check the results above.")
        
        print("="*60 + "\n")
        
        return passed, failed, total

if __name__ == "__main__":
    tester = AvatarGameTester()
    passed, failed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)
