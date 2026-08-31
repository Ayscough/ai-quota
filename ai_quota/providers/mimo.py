from __future__ import annotations

import os
from ..http import get_json


def _percent(item: dict) -> int:
    used, limit = float(item.get("used", 0)), float(item.get("limit", 0))
    return max(0, min(100, round(100 - used / limit * 100))) if limit else 0


def parse_mimo(balance: dict, usage: dict | None = None) -> dict:
    if balance.get("code") not in (None, 0):
        raise RuntimeError(balance.get("message") or f"MiMo API code {balance['code']}")
    data = balance.get("data") or {}
    raw = data.get("balance", data.get("totalBalance"))
    if raw is None:
        raise RuntimeError("MiMo balance information missing")
    result = {"status": "ok", "balance": float(raw), "currency": data.get("currency", "CNY")}
    for source, target in (("cashBalance", "cash_balance"), ("giftBalance", "gift_balance")):
        if data.get(source) is not None:
            result[target] = float(data[source])
    if usage:
        items = ((usage.get("data") or {}).get("monthUsage") or {}).get("items") or []
        if items:
            item = items[0]
            result.update(remaining_percent=_percent(item), token_used=item.get("used", 0), token_limit=item.get("limit", 0))
    return result


class MiMoProvider:
    key = "mimo"
    label = "MiMo"

    def __init__(self, cookie: str | None = None, base_url: str | None = None):
        self.cookie = cookie or os.getenv("MIMO_COOKIE")
        self.base_url = (base_url or os.getenv("MIMO_API_URL") or "https://platform.xiaomimimo.com/api/v1").rstrip("/")
        if not self.base_url.startswith("https://"):
            raise ValueError("MIMO_API_URL must use HTTPS")

    def fetch(self, timeout: float = 8.0) -> dict:
        if not self.cookie:
            raise RuntimeError("MIMO_COOKIE not configured; paste a Cookie header")
        headers = {"Accept": "application/json, text/plain, */*", "Cookie": self.cookie,
                   "Origin": "https://platform.xiaomimimo.com",
                   "Referer": "https://platform.xiaomimimo.com/#/console/balance"}
        balance = get_json(f"{self.base_url}/balance", headers, timeout)
        try:
            usage = get_json(f"{self.base_url}/tokenPlan/usage", headers, timeout)
        except Exception:
            usage = None
        return parse_mimo(balance, usage)
