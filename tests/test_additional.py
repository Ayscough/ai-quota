from ai_quota.providers.kimi import parse_kimi
from ai_quota.providers.glm import parse_glm
from ai_quota.providers.claude import parse_claude
from ai_quota.providers.codex import parse_codex
from ai_quota.providers.openrouter import parse_openrouter
from ai_quota.providers.openai import parse_openai_costs
from ai_quota.providers.anthropic import parse_anthropic_costs
from ai_quota.providers.minimax import parse_minimax
from ai_quota.providers.copilot import parse_copilot
from ai_quota.providers.gemini import parse_gemini_quota


def test_kimi_parses_balance():
    result = parse_kimi({"data": {"available_balance": 12.5, "cash_balance": 10, "voucher_balance": 2}})
    assert result["status"] == "ok" and result["balance"] == 12.5


def test_glm_parses_balance_shapes():
    result = parse_glm({"code": 200, "data": {"balance": "8.2", "currency": "CNY"}})
    assert result["status"] == "ok" and result["balance"] == 8.2


def test_kimi_coding_quota_shape():
    result = parse_kimi({"subType": "basic", "usage": {"limit": 100, "remaining": 80, "resetTime": 123}})
    assert result["remaining"] == 80 and result["used_percent"] == 20


def test_glm_coding_quota_shape():
    result = parse_glm({"data": {"limits": [{"type": "CREDIT_LIMIT", "unit": 3, "percentage": 25}]}})
    assert result["windows"][0]["used_percent"] == 25


def test_claude_parses_quota():
    result = parse_claude({"five_hour": {"utilization": 35, "resets_at": "2026-08-30T22:00:00Z"}, "seven_day": {"utilization": 15}})
    assert result["status"] == "ok" and result["five_hour_used_percent"] == 35


def test_codex_parses_two_quota_windows():
    result = parse_codex({"plan_type": "plus", "rate_limit": {
        "primary_window": {"used_percent": 20, "reset_at": 123},
        "secondary_window": {"used_percent": 40, "reset_at": 456},
    }})
    assert result["status"] == "ok" and result["primary_used_percent"] == 20


def test_openrouter_parses_key_limit_and_usage():
    result = parse_openrouter({"data": {"limit": 100, "limit_remaining": 74.5,
                                          "usage_monthly": 25.5, "limit_reset": "monthly"}})
    assert result["status"] == "ok"
    assert result["limit_remaining"] == 74.5
    assert result["usage_monthly"] == 25.5


def test_openai_and_anthropic_cost_parsers_sum_buckets():
    assert parse_openai_costs({"data": [{"results": [{"amount": {"value": 1.25}}]},
                                      {"results": [{"amount": {"value": 2.0}}]}]})["cost"] == 3.25
    assert parse_anthropic_costs({"data": [{"amount": "125"}, {"amount": "200"}]})["cost"] == 3.25


def test_minimax_and_copilot_parse_remaining_quota():
    assert parse_minimax({"base_resp": {"status_code": 0}, "data": {"remain": 68, "total": 100}})["remaining_percent"] == 68
    assert parse_copilot({"quota_snapshots": [{"quota_id": "premium", "entitlement": 300, "used": 71}]})["remaining"] == 229


def test_gemini_parses_model_quota_fractions():
    result = parse_gemini_quota({"buckets": [{"modelId": "gemini", "remainingFraction": 0.68, "resetTime": "2026-08-31T00:00:00Z"}]})
    assert result["status"] == "ok" and result["windows"][0]["remaining_percent"] == 68
