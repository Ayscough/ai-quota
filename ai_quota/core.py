from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FutureTimeout
from datetime import datetime
from typing import Iterable


def collect(providers: Iterable[object], timeout: float = 8.0) -> dict:
    providers = list(providers)
    result = {}
    pool = ThreadPoolExecutor(max_workers=max(1, len(providers)))
    futures = {pool.submit(p.fetch, timeout): p for p in providers}
    try:
        for future in as_completed(futures, timeout=max(0.0, timeout)):
            provider = futures[future]
            try:
                result[provider.key] = future.result()
            except Exception as exc:
                result[provider.key] = {"status": "error", "error": str(exc)}
    except FutureTimeout:
        pass
    finally:
        for future, provider in futures.items():
            if provider.key not in result:
                future.cancel()
                result[provider.key] = {"status": "error", "error": "timeout"}
        pool.shutdown(wait=False, cancel_futures=True)
    return {p.key: result.get(p.key, {"status": "error", "error": "no result"}) for p in providers}


def collect_results(providers: Iterable[object], timeout: float = 8.0) -> dict:
    return collect(providers, timeout)


def render_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


def render_text(data: dict, updated: str | None = None) -> str:
    lines = ["AI Quota", "────────────────"]
    labels = {"deepseek": "DeepSeek", "mimo": "MiMo"}
    for key, item in data.items():
        label = labels.get(key, key.title())
        if item.get("status") != "ok":
            value = f"ERROR: {item.get('error', 'unknown error')}"
        elif key == "deepseek":
            value = f"¥{item['balance']:.2f}"
        elif key == "mimo" and "remaining_percent" in item:
            value = f"{item['remaining_percent']}%"
        elif "five_hour_used_percent" in item:
            value = f"5h {item['five_hour_used_percent']:.0f}%"
        elif "primary_used_percent" in item:
            value = f"5h {item['primary_used_percent']:.0f}%"
        elif "used_percent" in item:
            value = f"{item['used_percent']:.0f}%"
        elif item.get("windows"):
            value = " / ".join(f"{w['used_percent']:.0f}%" for w in item["windows"])
        elif "balance" in item:
            value = f"{item['balance']:.2f} {item.get('currency', '')}".rstrip()
        elif "cost" in item:
            value = f"cost {item['cost']:.2f} {item.get('currency', '')}".rstrip()
        elif item.get("status") == "unsupported":
            value = "UNSUPPORTED"
        else:
            value = "ok"
        lines.append(f"{label:<12}{value}")
    lines += ["────────────────", f"updated {updated or datetime.now().astimezone().strftime('%H:%M')}"]
    return "\n".join(lines)
