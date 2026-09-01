from __future__ import annotations

import os
import tomllib
from pathlib import Path


def load_config(path: str | None = None) -> dict:
    if path or os.getenv("AI_QUOTA_CONFIG"):
        candidates = [Path(path or os.environ["AI_QUOTA_CONFIG"]).expanduser()]
    else:
        candidates = [Path.cwd() / "config.toml", Path("~/.config/ai-quota/config.toml").expanduser()]
    config_path = next((candidate for candidate in candidates if candidate.exists()), None)
    if config_path is None:
        return {}
    with config_path.open("rb") as fh:
        return tomllib.load(fh)


def provider_config(config: dict, name: str, field: str, env: str) -> str | None:
    return os.getenv(env) or ((config.get(name) or {}).get(field))
