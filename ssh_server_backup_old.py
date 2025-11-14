#!/usr/bin/env python3
"""SSH server with interactive shell support - Reverse tunnel from Android/Termux"""

import socket
import paramiko
import threading
import subprocess
import sys
from pathlib import Path
import time


class Handler(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.shell_ready = False

    def check_auth_password(self, username, password):
        if password == "password":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, channel, term, width, height,
                                   pixelwidth, pixelheight, modes):
        # Store terminal properties for later use
        self.term = term or 'xterm'
        self.width = width or 80
        self.height = height or 24
        return paramiko.OPEN_SUCCEEDED

    def check_channel_shell_request(self, channel):
        # Mark that shell is requested but don't block here
        self.event.set()
        return paramiko.OPEN_SUCCEEDED


def forward_shell(channel, process):
    """Handle bidirectional I/O between SSH channel and shell"""
    print("[*] Starting shell I/O forwarding... - ssh_server.py:47")

    def read_from_channel():
        """Read from SSH channel, write to shell stdin"""
        try:
            while True:
                data = channel.recv(4096)
                if not data:
                    print("[*] Channel EOF - ssh_server.py:55")
                    break
                try:
                    process.stdin.write(data)
                    process.stdin.flush()
                except (BrokenPipeError, IOError):
                    break
        except Exception as e:
            print("[!] Channel read error: {} - ssh_server.py:63".format(e))
        finally:
            try:
                process.stdin.close()
            except Exception:
                pass

    def read_from_shell():
        """Read from shell stdout/stderr, send to SSH channel"""
        import fcntl
        import os
        try:
            # Try to set non-blocking on stdout
            try:
                flags = fcntl.fcntl(process.stdout, fcntl.F_GETFL)
                fcntl.fcntl(process.stdout, fcntl.F_SETFL,
                            flags | os.O_NONBLOCK)
            except (AttributeError, OSError):
                pass  # fcntl not available on Windows

            while process.poll() is None:
                try:
                    data = process.stdout.read(4096)
                    if data:
                        channel.send(data)
                except (BrokenPipeError, IOError):
                    break
        except Exception as e:
            print("[!] Shell read error: {} - ssh_server.py:91".format(e))
        finally:
            try:
                channel.close()
            except Exception:
                pass

    t1 = threading.Thread(target=read_from_channel, daemon=True)
    t2 = threading.Thread(target=read_from_shell, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("[*] Shell I/O forwarding closed - ssh_server.py:104")


def handle_client(client, addr, key):
    """Handle client connection"""
    print("[+] Connection from {}:{} - ssh_server.py:109".format(addr[0], addr[1]))

    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(key)

        handler = Handler()
        transport.start_server(server=handler)

        channel = transport.accept(20)
        if channel is None:
            print("[] No channel - ssh_server.py:120")
            return

        print("[+] Channel open - ssh_server.py:123")

        # Start shell process
        if sys.platform == 'win32':
            process = subprocess.Popen(
                ['cmd.exe'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,  # Line buffered
                text=False
            )
        else:
            process = subprocess.Popen(
                ['/bin/bash', '-i'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1
            )

        print("[+] Shell spawned - ssh_server.py:144")
        forward_shell(channel, process)

    except Exception as e:
        print("[] Error: {} - ssh_server.py:148".format(str(e)))
    finally:
        try:
            transport.close()
        except:
            pass
        print("[] Disconnected: {}:{} - ssh_server.py:154".format(addr[0], addr[1]))


def main():
    """Start SSH server"""
    port = 2222

    # Setup key
    key_path = Path.home() / '.ssh' / 'ultron_host_key'
    key_path.parent.mkdir(parents=True, exist_ok=True)

    if not key_path.exists():
        print("[*] Generating key... - ssh_server.py:166")
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(str(key_path))
    else:
        key = paramiko.RSAKey.from_private_key_file(str(key_path))

    # Setup socket
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(5)

    print("")
    print("SSH Server started on port {} - ssh_server.py:179".format(port))
    print("ssh p 2222 anyuser@192.168.1.104 - ssh_server.py:180")
    print("")

    try:
        while True:
            client, addr = sock.accept()
            t = threading.Thread(target=handle_client, args=(client, addr, key), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nShutdown - ssh_server.py:189")
    finally:
        sock.close()


if __name__ == '__main__':
    main()
