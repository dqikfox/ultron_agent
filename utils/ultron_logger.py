"""Minimal Logger"""

def log_info(component, message):
    print(f"[INFO] {component}: {message}")

def log_error(component, message):
    print(f"[ERROR] {component}: {message}")