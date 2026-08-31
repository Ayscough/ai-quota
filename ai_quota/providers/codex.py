from __future__ import annotations
import json, os
from pathlib import Path
from ..http import get_json


def parse_codex(payload: dict) -> dict:
    rate = payload.get("rate_limit") or {}
    result = {"status": "ok"}
    for name, key in (("primary", "primary_window"), ("secondary", "secondary_window")):
        window = rate.get(key) or {}
        if window:
            result[f"{name}_used_percent"] = float(window.get("used_percent", 0))
            if window.get("reset_at") is not None: result[f"{name}_reset_at"] = window["reset_at"]
    if payload.get("plan_type"): result["plan"] = payload["plan_type"]
    if not rate: raise RuntimeError("Codex quota information missing")
    return result


def _load_auth(path: Path) -> tuple[str, str | None]:
    if not path.exists(): raise RuntimeError(f"Codex auth file not found: {path}")
    data = json.loads(path.read_text())
    if data.get("OPENAI_API_KEY"): return data["OPENAI_API_KEY"], None
    tokens = data.get("tokens") or {}
    token = tokens.get("access_token")
    if not token: raise RuntimeError("Codex access token missing")
    return token, tokens.get("account_id")


class CodexProvider:
    key, label = "codex", "Codex"
    def __init__(self, auth_path=None, base_url=None):
        self.auth_path = Path(auth_path or os.getenv("CODEX_AUTH_FILE", "~/.codex/auth.json")).expanduser()
        self.base_url = (base_url or os.getenv("CODEX_API_URL") or "https://chatgpt.com/backend-api").rstrip("/")
    def fetch(self, timeout=8.0):
        token, account_id = _load_auth(self.auth_path)
        headers = {"Authorization": f"Bearer {token}", "User-Agent": "codex-cli", "Accept": "application/json"}
        if account_id: headers["ChatGPT-Account-Id"] = account_id
        return parse_codex(get_json(f"{self.base_url}/wham/usage", headers, timeout))
