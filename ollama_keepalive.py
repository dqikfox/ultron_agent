#!/usr/bin/env python3
"""
Ollama Keep-Alive Script for ULTRON Agent 2
Prevents Ollama models from going offline due to inactivity
"""

import time
import requests
import json
import sys
import threading
from datetime import datetime
import logging

#!/usr/bin/env python3
"""
Ollama Keep-Alive Script for ULTRON Agent 2
Prevents Ollama models from going offline due to inactivity
"""

import time
import requests
import json
import sys
import threading
from datetime import datetime
import logging

class OllamaKeepAlive:
    def __init__(self, model_url, timeout=60):
        self.model_url = model_url
        self.timeout = timeout
        self.last_request_time = None
        self.keepalive_thread = None

    def start(self):
        if not self.keepalive_thread:
            self.keepalive_thread = threading.Thread(target=self.run_keepalive)
            self.keepalive_thread.daemon = True
            self.keepalive_thread.start()

    def stop(self):
        if self.keepalive_thread:
            self.keepalive_thread.join()
            self.keepalive_thread = None

    def run_keepalive(self):
        while True:
            try:
                response = requests.get(self.model_url, timeout=self.timeout)
                if response.status_code == 200:
                    self.last_request_time = datetime.now()
                else:
                    logging.error(f"Model request failed: {response.status_code} - ollama_keepalive.py:54")
            except Exception as e:
                logging.error(f"Error in keepalive loop: {e} - ollama_keepalive.py:56")
            time.sleep(self.timeout)

    def get_last_request_time(self):
        return self.last_request_time
```

Please note that I've added a constructor `__init__` to the `OllamaKeepAlive` class, which takes the model URL and timeout as arguments. The `start` method starts a background thread that runs the `run_keepalive` method, while the `stop` method stops the keepalive thread if it's running. The `run_keepalive` method sends a GET request to the model URL every `timeout` seconds and updates the `last_request_time` attribute accordingly. If the model response fails, an error is logged, and the thread sleeps for the next iteration.
        Args:
            model_name: Name of the model to keep alive
            host: Ollama server host
            port: Ollama server port
            interval: Keep-alive interval in seconds (default 240s = 4 minutes)
        """
        self.model_name = model_name
        self.host = host
        self.port = port
        self.interval = interval
        self.base_url = f"http://{host}:{port}"
        self.running = False
        self.thread = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ollama_keepalive.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def check_ollama_status(self):
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
            return False

    def ping_model(self):
        """Send a minimal request to keep the model loaded"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": "ping",
                "stream": False,
                "options": {
                    "max_tokens": 1,
                    "temperature": 0.0
                }
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                self.logger.info(f"✅ Keep-alive ping successful for {self.model_name}")
                return True
            else:
                self.logger.warning(f"⚠️  Keep-alive ping failed: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Keep-alive ping error: {e}")
            return False

    def get_model_status(self):
        """Get current status of the model"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model["name"] == self.model_name:
                        return {
                            "name": model["name"],
                            "size": model.get("size", "Unknown"),
                            "modified": model.get("modified_at", "Unknown")
                        }
            return None
        except Exception as e:
            self.logger.error(f"Error getting model status: {e}")
            return None

    def keep_alive_loop(self):
        """Main keep-alive loop"""
        self.logger.info(f"🤖 Starting Ollama Keep-Alive for {self.model_name}")
        self.logger.info(f"⏱️  Ping interval: {self.interval} seconds")

        while self.running:
            if not self.check_ollama_status():
                self.logger.warning("⚠️  Ollama server not responding, retrying in 30 seconds...")
                time.sleep(30)
                continue

            # Get model status
            model_status = self.get_model_status()
            if model_status:
                self.logger.info(f"📊 Model status: {model_status['name']} ({model_status['size']})")

            # Send keep-alive ping
            success = self.ping_model()

            if not success:
                self.logger.warning(f"⚠️  Model {self.model_name} may not be loaded, attempting to load...")
                # Try a simple generation to load the model
                self.ping_model()

            # Wait for next interval
            time.sleep(self.interval)

    def start(self):
        """Start the keep-alive service"""
        if self.running:
            self.logger.warning("Keep-alive service already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self.keep_alive_loop, daemon=True)
        self.thread.start()
        self.logger.info("🚀 Keep-alive service started")

    def stop(self):
        """Stop the keep-alive service"""
        if not self.running:
            self.logger.warning("Keep-alive service not running")
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("🛑 Keep-alive service stopped")

    def status(self):
        """Get current service status"""
        ollama_status = "Online" if self.check_ollama_status() else "Offline"
        service_status = "Running" if self.running else "Stopped"

        status_info = {
            "service_status": service_status,
            "ollama_status": ollama_status,
            "model_name": self.model_name,
            "ping_interval": self.interval,
            "next_ping": f"in {self.interval} seconds" if self.running else "N/A"
        }

        return status_info


def main():
    """Main entry point for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Ollama Keep-Alive Service")
    parser.add_argument("--model", "-m", default="qwen2.5-coder:1.5b",
                       help="Model name to keep alive (memory optimized)")
    parser.add_argument("--host", default="localhost",
                       help="Ollama server host")
    parser.add_argument("--port", "-p", type=int, default=11434,
                       help="Ollama server port")
    parser.add_argument("--interval", "-i", type=int, default=240,
                       help="Keep-alive interval in seconds (default: 240)")
    parser.add_argument("--daemon", "-d", action="store_true",
                       help="Run as daemon (background)")

    args = parser.parse_args()

    # Create keep-alive service
    keepalive = OllamaKeepAlive(
        model_name=args.model,
        host=args.host,
        port=args.port,
        interval=args.interval
    )

    # Check initial status
    print(f"🔍 Checking Ollama status... - ollama_keepalive.py:238")
    if not keepalive.check_ollama_status():
        print("❌ Ollama server not responding. Make sure Ollama is running with 'ollama serve' - ollama_keepalive.py:240")
        sys.exit(1)

    model_status = keepalive.get_model_status()
    if model_status:
        print(f"✅ Model found: {model_status['name']} - ollama_keepalive.py:245")
    else:
        print(f"⚠️  Model {args.model} not found in Ollama. It will be loaded on first ping. - ollama_keepalive.py:247")

    # Start service
    keepalive.start()

    if args.daemon:
        print(f"🤖 Keepalive service running in background for {args.model} - ollama_keepalive.py:253")
        print(f"📋 Logs: ollama_keepalive.log - ollama_keepalive.py:254")
        print(f"🛑 Stop with Ctrl+C - ollama_keepalive.py:255")

        try:
            while True:
                time.sleep(60)  # Check every minute
                if not keepalive.running:
                    break
        except KeyboardInterrupt:
            print("\n🛑 Stopping keepalive service... - ollama_keepalive.py:263")
            keepalive.stop()
            sys.exit(0)
    else:
        print(f"🤖 Keepalive service started for {args.model} - ollama_keepalive.py:267")
        print(f"📊 Status check every {args.interval} seconds - ollama_keepalive.py:268")
        print(f"🛑 Press Ctrl+C to stop - ollama_keepalive.py:269")

        try:
            while keepalive.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping keepalive service... - ollama_keepalive.py:275")
            keepalive.stop()


if __name__ == "__main__":
    main()
