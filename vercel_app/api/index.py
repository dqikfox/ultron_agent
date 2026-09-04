"""Vercel serverless entry point — imports the self-contained FastAPI app."""
from api.app import app  # noqa: F401 — Vercel picks up `app`
