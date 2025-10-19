"""Utility to verify API connectivity for key Ultron Agent integrations.

Usage:
    python scripts/api_sanity_check.py [service ...]

When run without arguments, all supported services are checked.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from typing import Callable, Dict, Iterable, Tuple

import requests

Result = Tuple[str, Dict[str, object]]

TIMEOUT = 10


def _status(result: str, **details: object) -> Result:
    return result, details


def _sanitize(text: str) -> str:
    if not text:
        return text

    patterns = (
        (r"sk-[A-Za-z0-9_-]+", "sk-***"),
        (r"sk_[A-Za-z0-9_-]+", "sk_***"),
        (r"nvapi-[A-Za-z0-9_-]+", "nvapi-***"),
        (r"ghp_[A-Za-z0-9]+", "ghp_***"),
    )

    sanitized = text
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized)

    return sanitized


def check_openai() -> Result:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _status("skipped", reason="OPENAI_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return _status("error", detail=str(exc))

    if response.status_code == 200:
        payload = response.json()
        return _status("ok", models=len(payload.get("data", [])))

    return _status(
        "fail",
        http_status=response.status_code,
        detail=_sanitize(response.text[:200]),
    )


def check_anthropic() -> Result:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _status("skipped", reason="ANTHROPIC_API_KEY not set")

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    try:
        response = requests.get(
            "https://api.anthropic.com/v1/models",
            headers=headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return _status("error", detail=str(exc))

    if response.status_code == 200:
        payload = response.json()
        return _status("ok", models=len(payload.get("data", [])))

    return _status(
        "fail",
        http_status=response.status_code,
        detail=_sanitize(response.text[:200]),
    )


def check_elevenlabs() -> Result:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return _status("skipped", reason="ELEVENLABS_API_KEY not set")

    headers = {
        "xi-api-key": api_key,
    }

    try:
        response = requests.get(
            "https://api.elevenlabs.io/v1/user",
            headers=headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return _status("error", detail=str(exc))

    if response.status_code == 200:
        payload = response.json()
        return _status("ok", user_id=payload.get("user", {}).get("id"))

    return _status(
        "fail",
        http_status=response.status_code,
        detail=_sanitize(response.text[:200]),
    )


def check_nvidia() -> Result:
    api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("NVIDIA_NIM_API_KEY")
    if not api_key:
        return _status(
            "skipped",
            reason="NVIDIA_API_KEY / NVIDIA_NIM_API_KEY not set",
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.get(
            "https://integrate.api.nvidia.com/v1/models",
            headers=headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return _status("error", detail=str(exc))

    if response.status_code == 200:
        payload = response.json()
        return _status("ok", models=len(payload.get("data", [])))

    return _status(
        "fail",
        http_status=response.status_code,
        detail=_sanitize(response.text[:200]),
    )


def check_groq() -> Result:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _status("skipped", reason="GROQ_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers=headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        return _status("error", detail=str(exc))

    if response.status_code == 200:
        payload = response.json()
        return _status("ok", models=len(payload.get("data", [])))

    return _status(
        "fail",
        http_status=response.status_code,
        detail=_sanitize(response.text[:200]),
    )


SERVICES: Dict[str, Callable[[], Result]] = {
    "openai": check_openai,
    "anthropic": check_anthropic,
    "elevenlabs": check_elevenlabs,
    "nvidia": check_nvidia,
    "groq": check_groq,
}


def run_checks(selected: Iterable[str]) -> Dict[str, Result]:
    results: Dict[str, Result] = {}
    for name in selected:
        checker = SERVICES.get(name)
        if not checker:
            results[name] = _status("unknown", detail="service not supported")
            continue

        results[name] = checker()

    return results


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="API connectivity sanity check",
    )
    parser.add_argument(
        "services",
        nargs="*",
        default=sorted(SERVICES.keys()),
        help="Services to check (default: all supported)",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)
    selected_services = args.services

    results = run_checks(selected_services)

    for name in selected_services:
        status, details = results.get(name, ("unknown", {}))
        detail_str = (
            ", ".join(f"{k}={v}" for k, v in details.items())
            if details
            else ""
        )
        if detail_str:
            print(f"{name}: {status} ({detail_str})")
        else:
            print(f"{name}: {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
