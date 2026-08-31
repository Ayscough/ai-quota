from __future__ import annotations

import json
import os
from pathlib import Path
from ..http import post_json


def parse_gemini_quota(payload: dict) -> dict:
    buckets = payload.get("buckets") or payload.get("quotaBuckets") or []
    if not buckets:
        raise RuntimeError("Gemini CLI quota information missing")
    windows = []
    for item in buckets:
        fraction = item.get("remainingFraction", item.get("remaining_percent", 0))
        if float(fraction) <= 1:
            fraction = float(fraction) * 100
        windows.append({"name": item.get("modelId", item.get("model", "model")),
                        "remaining_percent": round(float(fraction), 2),
                        "used_percent": round(100 - float(fraction), 2),
                        **({"reset_at": item["resetTime"]} if item.get("resetTime") else {})})
    return {"status": "ok", "kind": "subscription", "windows": windows}


def _load_credentials(path: Path) -> tuple[str, str | None]:
    if not path.exists():
        raise RuntimeError(f"Gemini OAuth file not found: {path}")
    data = json.loads(path.read_text())
    token = data.get("access_token") or data.get("accessToken") or (data.get("token") or {}).get("access_token")
    if not token:
        raise RuntimeError("Gemini OAuth access token missing")
    return token, data.get("projectId") or data.get("project_id")


class GeminiCLIProvider:
    key, label = "gemini_cli", "Gemini CLI"

    def __init__(self, credentials_path=None, quota_url=None):
        self.credentials_path = Path(credentials_path or os.getenv("GEMINI_OAUTH_FILE", "~/.gemini/oauth_creds.json")).expanduser()
        self.quota_url = quota_url or os.getenv("GEMINI_QUOTA_URL") or "https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota"

    def fetch(self, timeout=8.0):
        token, project = _load_credentials(self.credentials_path)
        payload = {"project": project} if project else {}
        return parse_gemini_quota(post_json(self.quota_url, {"Authorization": f"Bearer {token}"}, payload, timeout))