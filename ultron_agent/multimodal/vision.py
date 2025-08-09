from __future__ import annotations

"""
Minimal vision stubs for Phase 1 using Pillow only (optional OpenCV in later phases).
"""
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
    Image = None


def load_image(path: str | Path):
    if not PIL_AVAILABLE:
        return None
    try:
        return Image.open(path)
    except Exception:
        return None