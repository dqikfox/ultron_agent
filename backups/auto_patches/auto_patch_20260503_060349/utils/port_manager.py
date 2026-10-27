#!/usr/bin/env python3
"""
Port Management Utility for ULTRON Agent
Ensures unique ports are used to avoid conflicts
"""

import socket
import random
from typing import Optional, Set

class PortManager:
    """Manages port allocation to avoid conflicts"""

    # Known used ports (update as needed)
    RESERVED_PORTS = {
        80, 443,  # HTTP/HTTPS
        22, 23,   # SSH/Telnet
        25, 587,  # SMTP
        53,       # DNS
        110, 995, # POP3
        143, 993, # IMAP
        21,       # FTP
        3306,     # MySQL
        5432,     # PostgreSQL
        6379,     # Redis
        27017,    # MongoDB
        8080,     # Common web port
        3000,     # React/Node dev
        5000,     # Flask default
        8000,     # FastAPI/Django
        11434,    # Ollama
        5001,     # Current ULTRON mobile interface
    }

    @staticmethod
    def is_port_available(port: int, host: str = 'localhost') -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # 0 means connection successful (port in use)
        except:
            return False

    @staticmethod
    def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> Optional[int]:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            if port not in PortManager.RESERVED_PORTS and PortManager.is_port_available(port):
                return port
        return None

    @staticmethod
    def get_random_available_port(min_port: int = 8000, max_port: int = 9000) -> Optional[int]:
        """Get a random available port in the specified range"""
        available_ports = []
        for port in range(min_port, max_port + 1):
            if port not in PortManager.RESERVED_PORTS and PortManager.is_port_available(port):
                available_ports.append(port)

        if available_ports:
            return random.choice(available_ports)
        return None

    @staticmethod
    def get_currently_used_ports() -> Set[int]:
        """Get currently used ports on the system"""
        used_ports = set()
        try:
            # This is a simplified check - in production you'd use more robust methods
            import subprocess
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            port = int(parts[1].split(':')[-1])
                            used_ports.add(port)
                        except (ValueError, IndexError):
                            continue
        except:
            pass
        return used_ports

# Port assignments for ULTRON components
ULTRON_PORTS = {
    'mobile_web_interface': 5001,  # Currently in use
    'pokedex_gui': 8080,           # Reserved for Pokédex GUI
    'ollama': 11434,               # Ollama service
    'api_server': 8000,           # Main API server
    'web_gui': 3000,               # Web GUI
}

def get_next_available_port(service_name: str, preferred_port: Optional[int] = None) -> int:
    """Get the next available port for a service"""
    if preferred_port and PortManager.is_port_available(preferred_port):
        return preferred_port

    # Try service-specific preferred ranges
    ranges = {
        'web_interface': (5000, 5100),
        'api_server': (8000, 8100),
        'gui': (3000, 3100),
        'tool_server': (9000, 9100),
    }

    service_type = service_name.split('_')[-1]  # Get last part (interface, server, gui)
    if service_type in ranges:
        min_port, max_port = ranges[service_type]
        available = PortManager.find_available_port(min_port)
        if available and available <= max_port:
            return available

    # Fallback to general range
    available = PortManager.find_available_port(8000)
    if available:
        return available

    # Last resort
    return PortManager.get_random_available_port(10000, 20000) or 8081

if __name__ == "__main__":
    # Test the port manager
    print("🔍 Checking port availability...")

    # Check current ports
    used_ports = PortManager.get_currently_used_ports()
    print(f"📊 Currently used ports: {sorted(list(used_ports)[:10])}...")  # Show first 10

    # Test port finding
    test_ports = [3000, 5000, 8000, 8080, 9000]
    for port in test_ports:
        available = PortManager.is_port_available(port)
        status = "✅ Available" if available else "❌ In use"
        print(f"Port {port}: {status}")

    # Find new ports
    print("\n🔄 Finding available ports...")
    for service in ['mobile_web_interface', 'pokedex_gui', 'api_server', 'tool_server']:
        port = get_next_available_port(service)
        print(f"{service}: {port}")
