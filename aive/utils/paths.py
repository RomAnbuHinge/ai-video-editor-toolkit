"""Windows-aware default paths for config and cache."""
from __future__ import annotations

import os
from pathlib import Path


def default_config_dir() -> Path:
    base = os.environ.get