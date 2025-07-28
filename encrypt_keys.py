from cryptography.fernet import Fernet

def encrypt_keys():
    keys = """
OPENAI_API_KEY=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
OLLAMA_API_KEY=ollama-placeholder-key-1234567890
ELEVENLABS_API_KEY=sk_a99d3caeef2c2dc6e98567110d905e724af83375e5c29d9d
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impka2RkcmZsb2x1aGt5dHhka2toIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1ODYwNjksImV4cCI6MjA2NzE2MjA2OX0.nlMs2YRoC63AnpXTY9KuIFbebF_KjzgWXuxWcPBVX9A
GEMINI_API_KEY=AIzaSyAXRBP9DtXP8WzQLVjLs4uP8BSZKNJ5h7A
"""
    vault_key = "JvQ8ra7nE5gFwQhLD0xiTkUf23GSwABY"
    fernet = Fernet(vault_key.encode())
    encrypted = fernet.encrypt(keys.encode()).decode()
    with open("keys.txt", "w") as f:
        f.write(f"ENCRYPTED_KEYS={encrypted}")

if __name__ == "__main__":
    encrypt_keys()