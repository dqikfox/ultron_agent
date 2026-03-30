"""
Shared Ollama vision-model helper for ULTRON Agent tools.

Centralises the image-encoding + model-iteration logic that was previously
duplicated between ``tools/image_description_tool.py`` and
``tools/screenshot_analyzer_tool.py``.
"""

from __future__ import annotations

import base64
from typing import List, Optional

import requests

from utils.ultron_logger import log_info, log_error

# Default ordered list of vision models to try (most capable first).
DEFAULT_VISION_MODELS: List[str] = [
    "llava:7b",
    "qwen2.5vl:7b",
    "qwen2.5vl:3b",
]

_OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"


def analyze_image_with_ollama(
    image_path: str,
    prompt: str,
    *,
    models: Optional[List[str]] = None,
    timeout: int = 60,
    log_source: str = "ollama_vision",
) -> Optional[str]:
    """Analyse *image_path* with an Ollama vision model and return the result.

    The function encodes the image to base64 and tries each model in *models*
    in order, returning the first non-empty response.  Returns ``None`` when
    all models fail or are unavailable.

    Parameters
    ----------
    image_path:
        Filesystem path to the image to analyse.
    prompt:
        The text prompt to send to the vision model alongside the image.
    models:
        Ordered list of Ollama model names to attempt.  Defaults to
        :data:`DEFAULT_VISION_MODELS`.
    timeout:
        Per-request HTTP timeout in seconds.
    log_source:
        Label used in log messages (helps trace which tool called this helper).
    """
    if models is None:
        models = DEFAULT_VISION_MODELS

    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
    except OSError as exc:
        log_error(log_source, f"Failed to read image '{image_path}': {exc}")
        return None

    for model in models:
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False,
            }

            response = requests.post(
                _OLLAMA_GENERATE_URL,
                json=payload,
                timeout=timeout,
            )

            if response.status_code == 200:
                description = response.json().get("response", "")
                if description.strip():
                    log_info(log_source, f"Vision analysis completed with {model}")
                    return f"AI Vision Analysis ({model}):\n\n{description}"

        except Exception as model_error:
            log_error(log_source, f"Model {model} failed: {model_error}")
            continue

    return None
