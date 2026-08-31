from __future__ import annotations

import os
from ..http import get_json


def parse_copilot(payload: dict) -> dict:
    snapshots = payload.get("quota_snapshots") or payload.get("quotas") or []
    if not snapshots:
        raise RuntimeError("GitHub Copilot quota information missing")
    item = snapshots[0]
    total = float(item.get("entitlement", item.get("limit", 0)))
    used = float(item.get("used", item.get("consumed", 0)))
    return {"status": "ok", "kind": "subscription", "plan": payload.get("plan") or payload.get("plan_type"),
            "quota_name": item.get("quota_id") or item.get("name", "premium_requests"),
            "used": used, "limit": total, "remaining": total - used,
            "used_percent": round(used / total * 100, 2) if total else 0}


class CopilotProvider:
    key, label = "github_copilot", "GitHub Copilot"

    def __init__(self, token=None, base_url=None):
        self.token = token or os.getenv("GITHUB_COPILOT_TOKEN") or os.getenv("GITHUB_TOKEN")
        self.base_url = (base_url or os.getenv("GITHUB_COPILOT_API_URL") or "https://api.github.com").rstrip("/")

    def fetch(self, timeout=8.0):
        if not self.token:
            raise RuntimeError("GITHUB_COPILOT_TOKEN not configured")
        return parse_copilot(get_json(f"{self.base_url}/copilot_internal/user", {
            "Authorization": f"Bearer {self.token}", "Accept": "application/json",
            "X-GitHub-Api-Version": "2022-11-28"
        }, timeout))