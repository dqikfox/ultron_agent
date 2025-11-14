#!/usr/bin/env python3
"""SSH server with interactive shell - WORKING VERSION"""

import socket
import paramiko
import threading
import subprocess
import sys
from pathlib import Path
import time


class Handler(paramiko.ServerInterface):
    """SSH server interface implementation"""

    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        """Accept any username with password 'password'"""
        return (paramiko.AUTH_SUCCESSFUL
                if password == "password" else paramiko.AUTH_FAILED)

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_request(self, kind, chanid):
        """Accept session channel"""
        return (paramiko.OPEN_SUCCEEDED
                if kind == 'session'
                else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED)

    def check_channel_pty_request(self, channel, term, width, height,
                                   pixelwidth, pixelheight, modes):
        """Accept PTY request"""
        return paramiko.OPEN_SUCCEEDED

    def check_channel_shell_request(self, channel):
        """Accept shell request"""
        self.event.set()
        return paramiko.OPEN_SUCCEEDED


def forward_shell(channel, process):
    """Bidirectional I/O forwarding between SSH channel and shell"""

    def channel_to_shell():
        """SSH channel → shell stdin"""
        try:
            while True:
                data = channel.recv(4096)
                if not data:
                    try:
                        process.stdin.close()
                    except Exception:
                        pass
                    break
                try:
                    process.stdin.write(data)
                    process.stdin.flush()
                except (BrokenPipeError, IOError):
                    break
        except Exception as e:
            print(f"[!] Channel→Shell error: {e}")

    def shell_to_channel():
        """Shell stdout → SSH channel"""
        try:
            while process.poll() is None:
                try:
                    data = process.stdout.read(4096)
                    if data:
                        channel.send(data)
                except (BrokenPipeError, IOError):
                    break
                time.sleep(0.001)
            # Send any remaining output after process ends
            try:
                data = process.stdout.read()
                if data:
                    channel.send(data)
            except Exception:
                pass
        except Exception as e:
            print(f"[!] Shell→Channel error: {e}")
        finally:
            try:
                channel.close()
            except Exception:
                pass

    t1 = threading.Thread(target=channel_to_shell, daemon=True)
    t2 = threading.Thread(target=shell_to_channel, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def handle_client(client, addr, key):
    """Handle SSH client connection"""
    print(f"[+] Connection from {addr[0]}:{addr[1]}")

    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(key)
        transport.start_server(server=Handler())

        # Get channel
        channel = transport.accept(20)
        if not channel:
            print("[-] No channel accepted")
            return

        print("[+] Channel opened")

        # Spawn shell
        if sys.platform == 'win32':
            proc = subprocess.Popen(
                ['cmd.exe'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0
            )
        else:
            proc = subprocess.Popen(
                ['/bin/bash', '-i'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0
            )

        print("[+] Shell spawned")
        forward_shell(channel, proc)

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        try:
            transport.close()
        except Exception:
            pass
        print(f"[-] Disconnected: {addr[0]}:{addr[1]}")


def main():
    """Main SSH server loop"""
    port = 2222

    # Setup host key
    key_path = Path.home() / '.ssh' / 'ultron_host_key'
    key_path.parent.mkdir(parents=True, exist_ok=True)

    if not key_path.exists():
        print("[*] Generating host key...")
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(str(key_path))
    else:
        key = paramiko.RSAKey.from_private_key_file(str(key_path))

    # Setup socket
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(5)

    print(f"\n[*] SSH Server listening on 0.0.0.0:{port}")
    print("[*] Connect from Termux: ssh -p 2222 anyuser@192.168.1.104")
    print("[*] Password: password\n")

    try:
        while True:
            client, addr = sock.accept()
            t = threading.Thread(target=handle_client,
                                 args=(client, addr, key),
                                 daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        sock.close()


if __name__ == '__main__':
    main()
