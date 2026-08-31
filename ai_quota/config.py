from __future__ import annotations

import os
import tomllib
from pathlib import Path


def load_config(path: str | None = None) -> dict:
    config_path = Path(path or os.getenv("AI_QUOTA_CONFIG", "~/.config/ai-quota/config.toml")).expanduser()
    if not config_path.exists():
        return {}
    with config_path.open("rb") as fh:
        return tomllib.load(fh)


def provider_config(config: dict, name: str, field: str, env: str) -> str | None:
    return os.getenv(env) or ((config.get(name) or {}).get(field))
