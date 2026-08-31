from __future__ import annotations
import os
from ..http import get_json


def parse_glm(payload: dict) -> dict:
    data = payload.get("data") or payload
    limits = data.get("limits") or data.get("quota") or []
    if isinstance(limits, dict): limits = limits.get("limits", [])
    result = {"status": "ok", "plan": "coding_plan", "windows": []}
    for item in limits:
        if not isinstance(item, dict): continue
        kind = str(item.get("type", item.get("kind", "quota")))
        pct = item.get("percentage", item.get("percent", item.get("used_percent")))
        if pct is None: continue
        window = {"type": kind, "used_percent": float(pct)}
        if item.get("unit") is not None: window["unit"] = item["unit"]
        if item.get("resetTime") is not None: window["reset_at"] = item["resetTime"]
        result["windows"].append(window)
    if not result["windows"]:
        raw = data.get("balance", data.get("available_balance", data.get("total_balance")))
        if raw is None: raise RuntimeError("GLM quota information missing")
        result = {"status": "ok", "balance": float(raw), "currency": data.get("currency", "CNY")}
    return result


class GLMProvider:
    key, label = "glm", "GLM"
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.getenv("GLM_API_KEY") or os.getenv("ZHIPU_API_KEY") or os.getenv("ZAI_API_KEY")
        self.coding = os.getenv("GLM_CODING_PLAN", "").lower() in {"1", "true", "yes", "on"}
        default = "https://api.z.ai/api" if self.coding else "https://open.bigmodel.cn/api/paas/v4"
        self.base_url = (base_url or os.getenv("GLM_API_URL") or default).rstrip("/")
    def fetch(self, timeout=8.0):
        if not self.api_key: raise RuntimeError("GLM_API_KEY not configured")
        endpoint = "/monitor/usage/quota/limit" if self.coding else "/balance"
        return parse_glm(get_json(f"{self.base_url}{endpoint}", {"Authorization": f"Bearer {self.api_key}"}, timeout))
