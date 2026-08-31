from __future__ import annotations

import json
import urllib.error
import urllib.request

urlopen = urllib.request.urlopen


def get_json(url: str, headers: dict[str, str], timeout: float, opener=None) -> dict:
    request = urllib.request.Request(url, headers=headers)
    try:
        with (opener or urlopen)(request, timeout=timeout) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise RuntimeError("authentication failed") from exc
        raise RuntimeError(f"HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("network or timeout error") from exc
    try:
        value = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("invalid JSON response") from exc
    if not isinstance(value, dict):
        raise RuntimeError("unexpected JSON response")
    return value


def post_json(url: str, headers: dict[str, str], body: dict, timeout: float, opener=None) -> dict:
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={**headers, "Content-Type": "application/json"}, method="POST")
    try:
        with (opener or urlopen)(request, timeout=timeout) as response:
            value = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise RuntimeError("authentication failed") from exc
        raise RuntimeError(f"HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("network or timeout error") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("invalid JSON response") from exc
    if not isinstance(value, dict):
        raise RuntimeError("unexpected JSON response")
    return value
