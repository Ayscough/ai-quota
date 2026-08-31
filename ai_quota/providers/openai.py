from __future__ import annotations

import os
import time
from urllib.parse import urlencode
from ..http import get_json


def parse_openai_costs(payload: dict) -> dict:
    total = 0.0
    for bucket in payload.get("data", []):
        for item in bucket.get("results", []):
            amount = item.get("amount", {})
            total += float(amount.get("value", 0))
    return {"status": "ok", "kind": "organization_cost", "currency": "USD", "cost": round(total, 8)}


class OpenAIProvider:
    key, label = "openai", "OpenAI"

    def __init__(self, admin_key=None, org_id=None, base_url=None):
        self.admin_key = admin_key or os.getenv("OPENAI_ADMIN_KEY")
        self.org_id = org_id or os.getenv("OPENAI_ORG_ID")
        self.base_url = (base_url or os.getenv("OPENAI_API_URL") or "https://api.openai.com/v1").rstrip("/")

    def fetch(self, timeout=8.0):
        if not self.admin_key:
            raise RuntimeError("OPENAI_ADMIN_KEY not configured")
        end = int(time.time())
        start = end - 30 * 86400
        query = urlencode({"start_time": start, "end_time": end, "bucket_width": "1d"})
        headers = {"Authorization": f"Bearer {self.admin_key}", "Accept": "application/json"}
        if self.org_id:
            headers["OpenAI-Organization"] = self.org_id
        return parse_openai_costs(get_json(f"{self.base_url}/organization/costs?{query}", headers, timeout))