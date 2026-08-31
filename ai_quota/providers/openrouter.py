from __future__ import annotations

import os
from ..http import get_json


def parse_openrouter(payload: dict) -> dict:
    data = payload.get("data") or payload
    if "limit_remaining" not in data and "total_credits" not in data:
        raise RuntimeError("OpenRouter key limit information missing")
    result = {"status": "ok", "kind": "api_key_limit", "currency": "USD"}
    for key in ("limit", "limit_remaining", "usage", "usage_daily", "usage_weekly", "usage_monthly", "byok_usage"):
        if data.get(key) is not None:
            result[key] = float(data[key])
    if data.get("limit_reset") is not None:
        result["limit_reset"] = data["limit_reset"]
    if data.get("is_free_tier") is not None:
        result["is_free_tier"] = bool(data["is_free_tier"])
    return result


class OpenRouterProvider:
    key, label = "openrouter", "OpenRouter"

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = (base_url or os.getenv("OPENROUTER_API_URL") or "https://openrouter.ai/api/v1").rstrip("/")

    def fetch(self, timeout=8.0):
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not configured")
        return parse_openrouter(get_json(f"{self.base_url}/key", {
            "Authorization": f"Bearer {self.api_key}", "Accept": "application/json"
        }, timeout))