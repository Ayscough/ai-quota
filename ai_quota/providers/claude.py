from __future__ import annotations
import json, os
from pathlib import Path
from ..http import get_json


def parse_claude(payload: dict) -> dict:
    result = {"status": "ok"}
    for name, keys in (("five_hour", ("five_hour", "fiveHour")), ("seven_day", ("seven_day", "sevenDay"))):
        item = next((payload.get(k) for k in keys if payload.get(k) is not None), None)
        if item:
            result[f"{name}_used_percent"] = float(item.get("utilization", item.get("usage_pct", 0)))
            if item.get("resets_at"): result[f"{name}_resets_at"] = item["resets_at"]
    if len(result) == 1: raise RuntimeError("Claude usage information missing")
    result["plan"] = payload.get("plan_type") or payload.get("planType") or "unknown"
    return result


def _load_token(path: Path) -> str:
    if not path.exists(): raise RuntimeError(f"Claude credentials file not found: {path}")
    data = json.loads(path.read_text())
    token = ((data.get("claudeAiOauth") or {}).get("accessToken"))
    if not token: raise RuntimeError("Claude OAuth access token missing")
    return token


class ClaudeProvider:
    key, label = "claude", "Claude"
    def __init__(self, token=None, credentials_path=None, base_url=None):
        config_dir = Path(os.getenv("CLAUDE_CONFIG_DIR", "~/.claude")).expanduser()
        self.credentials_path = Path(credentials_path or config_dir / ".credentials.json").expanduser()
        self.token = token
        self.base_url = (base_url or os.getenv("CLAUDE_OAUTH_USAGE_URL") or "https://api.anthropic.com/api/oauth/usage").rstrip("/")
    def fetch(self, timeout=8.0):
        token = self.token or _load_token(self.credentials_path)
        headers = {"Authorization": f"Bearer {token}", "anthropic-beta": "oauth-2025-04-20", "Accept": "application/json"}
        return parse_claude(get_json(self.base_url, headers, timeout))
