import json
from types import SimpleNamespace

from ai_quota.cli import collect_results, render_text
from ai_quota.providers.deepseek import DeepSeekProvider
from ai_quota.providers.mimo import MiMoProvider


class FakeResponse:
    def __init__(self, payload, status=200):
        self.status = status
        self.payload = payload
    def read(self):
        return json.dumps(self.payload).encode()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None


def response(payload, status=200):
    return FakeResponse(payload, status)


def test_deepseek_parses_balance(monkeypatch):
    monkeypatch.setattr("ai_quota.http.urlopen", lambda request, timeout: response({
        "is_available": True,
        "balance_infos": [{"currency": "CNY", "total_balance": "32.41", "granted_balance": "2.00", "topped_up_balance": "30.41"}],
    }))
    result = DeepSeekProvider(api_key="secret").fetch()
    assert result["status"] == "ok"
    assert result["balance"] == 32.41 and result["currency"] == "CNY"


def test_mimo_missing_cookie_is_graceful():
    result = collect_results([MiMoProvider(cookie="")])["mimo"]
    assert result["status"] == "error" and "cookie" in result["error"].lower()


def test_collection_continues_after_provider_failure():
    class Good:
        key = "good"
        def fetch(self, timeout=8): return {"status": "ok", "value": 1}
    class Bad:
        key = "bad"
        def fetch(self, timeout=8): raise RuntimeError("network down")
    results = collect_results([Good(), Bad()])
    assert results["good"]["status"] == "ok"
    assert results["bad"]["status"] == "error" and "network down" in results["bad"]["error"]


def test_json_and_text_rendering():
    data = {"deepseek": {"status": "ok", "balance": 32.41, "currency": "CNY"}}
    text = render_text(data, updated="20:58")
    assert "DeepSeek" in text and "32.41" in text and "20:58" in text
