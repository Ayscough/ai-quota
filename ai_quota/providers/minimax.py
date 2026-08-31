from __future__ import annotations

import os
from ..http import get_json


def parse_minimax(payload: dict) -> dict:
    base = payload.get("base_resp") or {}
    if base.get("status_code") not in (None, 0):
        raise RuntimeError(base.get("status_msg") or f"MiniMax code {base['status_code']}")
    data = payload.get("data") or payload
    remain = data.get("remaining_percent", data.get("remain_percent"))
    if remain is None and data.get("remain") is not None and data.get("total"):
        remain = float(data["remain"]) / float(data["total"]) * 100
    if remain is None:
        raise RuntimeError("MiniMax coding-plan quota information missing")
    result = {"status": "ok", "kind": "coding_plan", "remaining_percent": round(float(remain), 2)}
    for key in ("plan", "plan_name", "reset_at", "weekly_remaining_percent", "five_hour_remaining_percent"):
        if data.get(key) is not None:
            result[key] = data[key]
    return result


class MiniMaxCodingPlanProvider:
    key, label = "minimax_coding_plan", "MiniMax Plan"

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.getenv("MINIMAX_CODING_API_KEY")
        self.base_url = (base_url or os.getenv("MINIMAX_CODING_API_URL") or "https://api.minimaxi.com").rstrip("/")

    def fetch(self, timeout=8.0):
        if not self.api_key:
            raise RuntimeError("MINIMAX_CODING_API_KEY not configured")
        return parse_minimax(get_json(f"{self.base_url}/v1/token_plan/remains", {
            "Authorization": f"Bearer {self.api_key}", "Accept": "application/json"
        }, timeout))