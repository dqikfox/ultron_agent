#!/usr/bin/env python3
"""
Simple SSH-like server for Android Termux connections
Allows secure shell access without requiring Windows SSH server installation
"""

import socket
import threading
import subprocess
import sys
from pathlib import Path

def handle_client(client_socket, address):
    """Handle incoming client connections"""
    print(f"✓ Client connected from {address}")

    try:
        while True:
            # Receive command from client
            data = client_socket.recv(1024).decode('utf-8', errors='ignore')

            if not data:
                break

            command = data.strip()
            print(f"→ Command: {command}")

            if command.lower() in ['exit', 'quit']:
                response = "Connection closed\n"
                client_socket.send(response.encode())
                break

            try:
                # Execute command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                output = result.stdout + result.stderr
                if not output:
                    output = "Command executed\n"

            except subprocess.TimeoutExpired:
                output = "ERROR: Command timed out\n"
            except Exception as e:
                output = f"ERROR: {str(e)}\n"

            # Send response back
            client_socket.send(output.encode())
            print(f"← Response sent ({len(output)} bytes)")

    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client_socket.close()
        print(f"✗ Client disconnected: {address}")

def start_server(port=2222):
    """Start the simple SSH server"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind(('0.0.0.0', port))
        server.listen(5)

        print(f"""
╔════════════════════════════════════════╗
║  🔐 Simple SSH Server Started           ║
╠════════════════════════════════════════╣
║  Port: {port}                              ║
║  Status: Listening...                   ║
║  Type: Command shell over TCP           ║
╚════════════════════════════════════════╝

To connect from Termux:
  ssh -p {port} <your-windows-ip>
  (You can also use: nc <your-windows-ip> {port})

Press Ctrl+C to stop the server
        """)

        while True:
            client_socket, address = server.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address)
            )
            client_thread.daemon = True
            client_thread.start()

    except KeyboardInterrupt:
        print("\n\n✗ Server shutting down...")
    except Exception as e:
        print(f"✗ Server error: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 2222
    start_server(port)
