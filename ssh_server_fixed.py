#!/usr/bin/env python3
"""SSH server with shell support for Android/Termux connections"""

import socket
import paramiko
import threading
import subprocess
import sys
import os
from pathlib import Path


class SSHServerHandler(paramiko.ServerInterface):
    """SSH server handler with PTY and shell support"""

    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return paramiko.OPEN_SUCCEEDED

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight):
        return paramiko.OPEN_SUCCEEDED

    def check_channel_exec_request(self, channel, command):
        self.event.set()
        return paramiko.OPEN_SUCCEEDED


def handle_client(client, addr, host_key):
    """Handle SSH client connection"""
    print("[+] Client connected: {}:{}".format(addr[0], addr[1]))

    transport = paramiko.Transport(client)
    transport.add_server_key(host_key)

    handler = SSHServerHandler()
    transport.start_server(server=handler)

    channel = transport.accept(20)
    if channel is None:
        print("[-] Channel accept timeout")
        return

    print("[+] Channel established")

    try:
        if sys.platform == 'win32':
            shell_cmd = 'cmd.exe'
        else:
            shell_cmd = '/bin/bash'

        process = subprocess.Popen(
            shell_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            bufsize=0
        )

        def read_from_shell():
            """Forward shell output to SSH channel"""
            try:
                while True:
                    data = process.stdout.read(1024)
                    if not data:
                        break
                    channel.send(data)
            except Exception as e:
                pass
            finally:
                channel.close()

        def write_to_shell():
            """Forward SSH input to shell"""
            try:
                while True:
                    data = channel.recv(1024)
                    if not data:
                        break
                    process.stdin.write(data)
                    process.stdin.flush()
            except Exception as e:
                pass

        # Start bidirectional communication
        read_thread = threading.Thread(target=read_from_shell, daemon=True)
        write_thread = threading.Thread(target=write_to_shell, daemon=True)
        read_thread.start()
        write_thread.start()

        read_thread.join()
        write_thread.join()

    except Exception as e:
        print("[-] Error: {}".format(str(e)))
    finally:
        try:
            process.terminate()
        except:
            pass
        channel.close()
        transport.close()
        print("[-] Client disconnected: {}:{}".format(addr[0], addr[1]))


def main():
    """Start SSH server"""
    port = 2222

    key_path = Path.home() / '.ssh' / 'ultron_host_key'
    key_path.parent.mkdir(parents=True, exist_ok=True)

    if not key_path.exists():
        print("[*] Generating host key...")
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(str(key_path))
        print("[+] Host key generated")
    else:
        key = paramiko.RSAKey.from_private_key_file(str(key_path))
        print("[+] Host key loaded")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(5)

    print("")
    print("="*60)
    print("SSH Server Ready!")
    print("="*60)
    print("Listening on port: {}".format(port))
    print("")
    print("Connect from Termux:")
    print("  ssh -p 2222 anyuser@192.168.1.104")
    print("="*60)
    print("")

    try:
        while True:
            client, addr = sock.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(client, addr, key),
                daemon=True
            )
            thread.start()

    except KeyboardInterrupt:
        print("\n[*] Shutting down server...")
    finally:
        sock.close()


if __name__ == '__main__':
    main()
