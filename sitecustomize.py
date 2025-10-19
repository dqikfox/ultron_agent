"""Environment alias bootstrap for ULTRON Agent.

This module is imported automatically by Python (via sitecustomize) and
ensures alternate Windows environment variable names are mapped to the
names expected by the codebase.
"""

from __future__ import annotations

import os
from typing import Dict, Iterable

# Map canonical environment variables to fallback aliases that may already
# exist on the host system. Values are copied only when the canonical name
# is unset to avoid clobbering explicit configuration.
_ENV_ALIAS_MAP: Dict[str, Iterable[str]] = {
    "LOGFLARE_LOGGER_BACKEND_API_KEY": ("LOGGER_BACKEND_API_KEY",),
}

for canonical_name, aliases in _ENV_ALIAS_MAP.items():
    if os.getenv(canonical_name):
        continue

    for alias in aliases:
        alias_value = os.getenv(alias)
        if alias_value:
            os.environ[canonical_name] = alias_value
            break
