"""Minimal Logger"""

def log_info(component, message):
    print(f"[INFO] {component}: {message}")

def log_error(component, message):
    print(f"[ERROR] {component}: {message}")

def log_ai_decision(component, message, ai_model=None, confidence_score=None):
    print(f"[AI] {component}: {message}")

# Compatibility
ultron_logger = type('Logger', (), {
    'info': lambda msg: print(f"[INFO] {msg}"),
    'error': lambda msg: print(f"[ERROR] {msg}")
})()