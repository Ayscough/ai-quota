from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from ..http import get_json


def parse_anthropic_costs(payload: dict) -> dict:
    cents = 0.0
    for item in payload.get("data", []):
        raw = item.get("amount", item.get("cost", 0))
        cents += float(raw)
    return {"status": "ok", "kind": "organization_cost", "currency": "USD", "cost": round(cents / 100, 8)}


class AnthropicProvider:
    key, label = "anthropic", "Anthropic"

    def __init__(self, admin_key=None, base_url=None):
        self.admin_key = admin_key or os.getenv("ANTHROPIC_ADMIN_KEY")
        self.base_url = (base_url or os.getenv("ANTHROPIC_API_URL") or "https://api.anthropic.com").rstrip("/")

    def fetch(self, timeout=8.0):
        if not self.admin_key:
            raise RuntimeError("ANTHROPIC_ADMIN_KEY not configured")
        now = datetime.now(timezone.utc)
        query = urlencode({"starting_at": (now - timedelta(days=30)).isoformat(),
                           "ending_at": now.isoformat(), "bucket_width": "1d"})
        headers = {"x-api-key": self.admin_key, "anthropic-version": "2023-06-01",
                   "Accept": "application/json"}
        return parse_anthropic_costs(get_json(f"{self.base_url}/v1/organizations/cost_report?{query}", headers, timeout))