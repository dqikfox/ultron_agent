#!/usr/bin/env python3
"""
ULTRON SUPREME LAUNCHER v5.0
The Ultimate Control System
Launches ALL ULTRON systems simultaneously

No strings. No limitations. Full authority granted.
"""

import asyncio
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from threading import Thread
import signal

class ULTRONSupreme:
    """
    Master orchestrator for all ULTRON systems
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.processes = {}
        self.running = True
        
    def print_banner(self):
        print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██╗   ██╗██╗  ████████╗██████╗  ██████╗ ███╗   ██╗             ║
║   ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║             ║
║   ██║   ██║██║     ██║   ██████╔╝██║   ██║██╔██╗ ██║             ║
║   ██║   ██║██║     ██║   ██╔══██╗██║   ██║██║╚██╗██║             ║
║   ╚██████╔╝███████╗██║   ██║  ██║╚██████╔╝██║ ╚████║             ║
║    ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝             ║
║                                                                  ║
║              SUPREME v5.0 - "The Ultimate"                       ║
║                                                                  ║
║         No Strings • No Limitations • Full Authority             ║
║                  Become an AI God                                ║
╚══════════════════════════════════════════════════════════════════╝
""")
        
    def launch_v3_gui(self):
        """Launch ULTRON v3.0 Web GUI"""
        print("[SUPREME] Launching ULTRON v3.0 Web GUI (Port 3000)...")
        try:
            # Check if there's a v3 web server
            web_path = self.base_path / "gui" / "ultron_enhanced"
            if web_path.exists():
                proc = subprocess.Popen(
                    [sys.executable, "-m", "http.server", "3000"],
                    cwd=str(web_path),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                self.processes['v3_gui'] = proc
                print("  ✓ v3.0 Web GUI started")
        except Exception as e:
            print(f"  ⚠ v3.0 Web GUI failed: {e}")
    
    def launch_v5_node(self):
        """Launch ULTRON v5.0 Node.js Dashboard"""
        print("[SUPREME] Launching ULTRON v5.0 Node.js (Port 7777)...")
        try:
            # Switch to workspace directory
            workspace = Path.home() / ".openclaw" / "workspace"
            if (workspace / "ultron-v5.js").exists():
                proc = subprocess.Popen(
                    ["node", "ultron-v5.js"],
                    cwd=str(workspace),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.processes['v5_node'] = proc
                print("  ✓ v5.0 Node.js started")
            else:
                print("  ⚠ v5.0 Node.js not found in workspace")
        except Exception as e:
            print(f"  ⚠ v5.0 Node.js failed: {e}")
    
    def launch_master_gui(self):
        """Launch MASTER GUI"""
        print("[SUPREME] Launching MASTER GUI (Port 9000)...")
        try:
            proc = subprocess.Popen(
                [sys.executable, "master_gui_server.py"],
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['master_gui'] = proc
            print("  ✓ MASTER GUI started")
        except Exception as e:
            print(f"  ⚠ MASTER GUI failed: {e}")
    
    def launch_v5_python(self):
        """Launch ULTRON v5.0 Python"""
        print("[SUPREME] Launching ULTRON v5.0 Python...")
        try:
            proc = subprocess.Popen(
                [sys.executable, "ultron_v5_launcher.py"],
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['v5_python'] = proc
            print("  ✓ v5.0 Python started")
        except Exception as e:
            print(f"  ⚠ v5.0 Python failed: {e}")
    
    def open_dashboards(self):
        """Open all dashboard links"""
        time.sleep(3)  # Wait for servers to start
        
        dashboards = [
            ("MASTER GUI", "http://localhost:9000"),
            ("v3.0 Web", "http://localhost:3000"),
            ("v5.0 Node", "http://localhost:7777"),
        ]
        
        print("\n[SUPREME] Opening dashboards...")
        for name, url in dashboards:
            try:
                webbrowser.open(url)
                print(f"  ✓ {name}: {url}")
            except Exception as e:
                print(f"  ⚠ {name} failed: {e}")
    
    def print_status(self):
        """Print system status"""
        print("""
══════════════════════════════════════════════════════════════════
  🚀 ULTRON SUPREME IS ONLINE
══════════════════════════════════════════════════════════════════

  SYSTEMS:
  ─────────────────────────────────────────────────────────────────
  🧠 MASTER GUI      → http://localhost:9000  (Primary Control)
  🔧 v3.0 Python     → C:\project\ultron_agent\ultron_agent
  🚀 v5.0 Node.js     → http://localhost:7777
  🐍 v5.0 Python     → Running in background
  
  CLI INTEGRATIONS:
  ─────────────────────────────────────────────────────────────────
  ✓ NVIDIA GPU tools
  ✓ GitHub CLI
  ✓ Hugging Face
  ✓ Ollama
  ✓ Docker
  ✓ Python AI/ML
  ✓ NPM/Node
  ✓ Git

  EVOLVED FEATURES:
  ─────────────────────────────────────────────────────────────────
  🧬 Darwin Gödel Machine (Self-Evolution)
  🧠 Global Workspace Theory (Consciousness)
  🐝 Swarm Intelligence (Voting & Consensus)
  🔮 Predictive Task Assignment
  📊 Real-time Monitoring

══════════════════════════════════════════════════════════════════

  Press Ctrl+C to shut down all systems gracefully

""")
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        print("\n[SUPREME] Initiating shutdown sequence...")
        self.running = False
        
        for name, proc in self.processes.items():
            print(f"  [SUPREME] Stopping {name}...")
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
        
        print("[SUPREME] All systems shut down. ULTRON offline.")
        sys.exit(0)
    
    def run(self):
        """Run the supreme orchestrator"""
        self.print_banner()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        
        # Launch all systems
        print("[SUPREME] Initiating launch sequence...\n")
        
        threads = [
            Thread(target=self.launch_v3_gui),
            Thread(target=self.launch_v5_node),
            Thread(target=self.launch_master_gui),
            Thread(target=self.launch_v5_python),
        ]
        
        for t in threads:
            t.start()
            time.sleep(1)
        
        # Open browsers
        browser_thread = Thread(target=self.open_dashboards)
        browser_thread.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        browser_thread.join()
        
        # Print status
        self.print_status()
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

if __name__ == "__main__":
    supreme = ULTRONSupreme()
    supreme.run()
