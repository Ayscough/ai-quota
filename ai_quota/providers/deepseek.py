from __future__ import annotations

import os
from ..http import get_json


def parse_balance(payload: dict) -> dict:
    if payload.get("is_available") is False:
        raise RuntimeError("balance unavailable")
    infos = payload.get("balance_infos") or []
    if not infos:
        raise RuntimeError("balance information missing")
    info = next((x for x in infos if x.get("currency") == "CNY"), infos[0])
    total = float(info["total_balance"])
    return {
        "status": "ok", "balance": total,
        "available_balance": total,
        "currency": info.get("currency", "CNY"),
        "granted_balance": float(info.get("granted_balance", 0)),
        "topped_up_balance": float(info.get("topped_up_balance", 0)),
        "is_available": bool(payload.get("is_available", True)),
    }


class DeepSeekProvider:
    key = "deepseek"
    label = "DeepSeek"

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = (base_url or os.getenv("DEEPSEEK_API_URL") or "https://api.deepseek.com").rstrip("/")

    def fetch(self, timeout: float = 8.0) -> dict:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not configured")
        payload = get_json(f"{self.base_url}/user/balance", {
            "Accept": "application/json", "Authorization": f"Bearer {self.api_key}"
        }, timeout)
        return parse_balance(payload)
