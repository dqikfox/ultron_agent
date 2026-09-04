"""
Vercel serverless entry point for ULTRON Agent.
Exposes a lightweight FastAPI app for the Vercel @vercel/python runtime.
Heavy local dependencies (agent_core, voice, torch, etc.) are not available
on Vercel — this serves the REST API surface only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# app.py has a try/except that falls back to a minimal FastAPI app when
# simple_server (which needs agent_core/torch/etc.) is unavailable.
from app import app  # noqa: F401 — Vercel picks up `app`
