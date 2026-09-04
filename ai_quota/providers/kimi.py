from __future__ import annotations
import os
from ..http import get_json


def parse_kimi(payload: dict, currency: str = "USD") -> dict:
    data = payload.get("data") or payload
    # Official API returns available_balance/voucher_balance/cash_balance.
    if data.get("available_balance") is not None:
        result = {"status": "ok", "kind": "account_balance", "balance": float(data["available_balance"]),
                  "currency": currency, "available_balance": float(data["available_balance"]),
                  "voucher_balance": float(data.get("voucher_balance", 0)),
                  "cash_balance": float(data.get("cash_balance", 0))}
        return result
    usage = data.get("usage") or {}
    raw = usage.get("remaining", data.get("balance"))
    if raw is None:
        raise RuntimeError("Kimi balance/quota information missing")
    result = {"status": "ok", "balance": float(raw), "remaining": float(raw), "unit": "quota", "plan": data.get("subType") or data.get("plan")}
    if usage.get("limit") is not None:
        result["limit"] = float(usage["limit"])
        result["used_percent"] = round((1 - float(raw) / float(usage["limit"])) * 100, 2) if float(usage["limit"]) else 0
    if usage.get("resetTime"): result["reset_at"] = usage["resetTime"]
    return result


class KimiProvider:
    key, label = "kimi", "Kimi"
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY") or os.getenv("KIMI_API_KEY")
        self.coding = os.getenv("KIMI_CODING_PLAN", "").lower() in {"1", "true", "yes", "on"}
        self.base_url = (base_url or os.getenv("KIMI_API_URL") or ("https://api.kimi.com" if self.coding else "https://api.moonshot.cn/v1")).rstrip("/")
    def fetch(self, timeout=8.0):
        if not self.api_key: raise RuntimeError("MOONSHOT_API_KEY not configured")
        endpoint = "/coding/v1/usages" if self.coding else "/users/me/balance"
        currency = "CNY" if ".cn" in self.base_url else "USD"
        return parse_kimi(get_json(f"{self.base_url}{endpoint}", {"Authorization": f"Bearer {self.api_key}"}, timeout), currency)
