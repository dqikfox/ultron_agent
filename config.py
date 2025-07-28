import os
import json
import logging
import uuid
from cryptography.fernet import Fernet

class Config:
    def __init__(self, path: str = "ultron_config.json"):
        self.data = {}
        self.load_config(path)
        logging.info("Configuration loaded and logging initialized.")

    def load_config(self, path: str):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.data = json.load(f)
        else:
            logging.error(f"Configuration file {path} not found.")
            raise FileNotFoundError(f"Configuration file {path} not found.")

    def decrypt_keys(self, vault_key: str):
        fernet = Fernet(vault_key.encode())
        with open("keys.txt", "r") as f:
            encrypted_keys = f.read().strip().split('=')[1]
            decrypted_keys = fernet.decrypt(encrypted_keys.encode()).decode()
            for line in decrypted_keys.splitlines():
                key, value = line.split('=')
                self.data[key] = value
        logging.info("API keys decrypted and loaded into configuration.")