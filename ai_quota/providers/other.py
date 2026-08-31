from __future__ import annotations

import os
from ..http import get_json


def parse_balance_payload(payload: dict, currency: str = "CNY") -> dict:
    data = payload.get("data") or payload
    raw = data.get("available_balance", data.get("balance", data.get("total_balance")))
    if raw is None:
        raise RuntimeError("balance field missing")
    return {"status": "ok", "kind": "account_balance", "balance": float(raw), "currency": data.get("currency", currency)}


class ConfiguredBalanceProvider:
    def __init__(self, key, label, api_key_env, url_env, default_url=None, currency="CNY"):
        self.key, self.label = key, label
        self.api_key = os.getenv(api_key_env)
        self.url = os.getenv(url_env) or default_url
        self.api_key_env, self.url_env, self.currency = api_key_env, url_env, currency

    def fetch(self, timeout=8.0):
        if not self.url:
            return {"status": "unsupported", "error": f"{self.label} has no stable public balance endpoint; configure {self.url_env}"}
        if not self.api_key:
            raise RuntimeError(f"{self.api_key_env} not configured")
        return parse_balance_payload(get_json(self.url, {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}, timeout), self.currency)


class GeminiProvider(ConfiguredBalanceProvider):
    def __init__(self):
        super().__init__("gemini", "Gemini", "GEMINI_API_KEY", "GEMINI_QUOTA_URL", currency="USD")


class MiniMaxProvider(ConfiguredBalanceProvider):
    def __init__(self):
        super().__init__("minimax", "MiniMax", "MINIMAX_API_KEY", "MINIMAX_BALANCE_URL")


class QwenProvider(ConfiguredBalanceProvider):
    def __init__(self):
        super().__init__("qwen", "Qwen", "DASHSCOPE_API_KEY", "QWEN_BALANCE_URL")


class SiliconFlowProvider(ConfiguredBalanceProvider):
    def __init__(self):
        super().__init__("siliconflow", "SiliconFlow", "SILICONFLOW_API_KEY", "SILICONFLOW_BALANCE_URL")
