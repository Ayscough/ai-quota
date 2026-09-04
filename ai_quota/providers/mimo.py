from __future__ import annotations

import os
from urllib.parse import unquote
from ..http import get_json


def _percent(item: dict) -> int:
    used, limit = float(item.get("used", 0)), float(item.get("limit", 0))
    return max(0, min(100, round(100 - used / limit * 100))) if limit else 0


def normalize_cookie(cookie: str) -> str:
    """Normalize a Cookie header copied from browser developer tools."""
    value = cookie.strip()
    if value.lower().startswith("cookie:"):
        value = value.split(":", 1)[1].strip()
    parts = []
    for part in value.split(";"):
        if "=" not in part:
            continue
        name, item = (piece.strip() for piece in part.split("=", 1))
        if len(item) >= 2 and item.startswith('"') and item.endswith('"'):
            item = item[1:-1]
        parts.append(f"{name}={unquote(item)}")
    return "; ".join(parts)


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

    def __init__(self, api_key: str | None = None, cookie: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.getenv("MIMO_API_KEY")
        self.cookie = normalize_cookie(cookie or os.getenv("MIMO_COOKIE") or "")
        self.base_url = (base_url or os.getenv("MIMO_API_URL") or "https://platform.xiaomimimo.com/api/v1").rstrip("/")
        if not self.base_url.startswith("https://"):
            raise ValueError("MIMO_API_URL must use HTTPS")

    def fetch(self, timeout: float = 8.0) -> dict:
        if not self.api_key and not self.cookie:
            raise RuntimeError("MIMO_API_KEY or MIMO_COOKIE not configured")
        headers = {"Accept": "application/json, text/plain, */*",
                   "Origin": "https://platform.xiaomimimo.com",
                   "Referer": "https://platform.xiaomimimo.com/#/console/balance"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["api-key"] = self.api_key
        else:
            headers["Cookie"] = self.cookie or ""
        balance = get_json(f"{self.base_url}/balance", headers, timeout)
        try:
            usage = get_json(f"{self.base_url}/tokenPlan/usage", headers, timeout)
        except Exception:
            usage = None
        return parse_mimo(balance, usage)
