import json
import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory

from ai_quota.core import collect, render_json, render_text
from ai_quota.providers.deepseek import parse_balance
from ai_quota.providers.mimo import parse_mimo
from ai_quota.config import load_config


class TestParsing(unittest.TestCase):
    def test_deepseek_parses_total_and_available_balances(self):
        result = parse_balance({"is_available": True, "balance_infos": [{
            "currency": "CNY", "total_balance": "32.41",
            "granted_balance": "2.00", "topped_up_balance": "30.41"
        }]})
        self.assertEqual(result["balance"], 32.41)
        self.assertEqual(result["available_balance"], 32.41)
        self.assertEqual(result["currency"], "CNY")

    def test_mimo_parses_balance_and_remaining_percent(self):
        result = parse_mimo(
            {"code": 0, "data": {"balance": "10.5", "currency": "CNY",
                                  "cashBalance": "8", "giftBalance": "2"}},
            {"code": 0, "data": {"monthUsage": {"items": [
                {"name": "standard", "used": 32, "limit": 100, "percent": 32}
            ]}}},
        )
        self.assertEqual(result["balance"], 10.5)
        self.assertEqual(result["remaining_percent"], 68)


class TestCore(unittest.TestCase):
    def test_project_config_is_loaded_when_present(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config.toml"
            path.write_text("[deepseek]\napi_key = 'local-test'\n")
            self.assertEqual(load_config(str(path))["deepseek"]["api_key"], "local-test")
            old_cwd = Path.cwd()
            try:
                import os
                os.chdir(directory)
                self.assertEqual(load_config()["deepseek"]["api_key"], "local-test")
            finally:
                os.chdir(old_cwd)

    def test_one_provider_failure_does_not_hide_other_provider(self):
        class Good:
            key = "good"
            label = "Good"
            def fetch(self, timeout):
                return {"status": "ok", "value": 1}

        class Bad:
            key = "bad"
            label = "Bad"
            def fetch(self, timeout):
                raise RuntimeError("authentication expired")

        result = collect([Good(), Bad()], timeout=0.1)
        self.assertEqual(result["good"]["status"], "ok")
        self.assertEqual(result["bad"]["status"], "error")
        self.assertIn("authentication expired", result["bad"]["error"])

    def test_json_is_valid(self):
        payload = {"deepseek": {"status": "ok", "balance": 1.2, "currency": "CNY"}}
        self.assertEqual(json.loads(render_json(payload)), payload)

    def test_text_contains_error_without_crashing(self):
        output = render_text({"deepseek": {"status": "error", "error": "timeout"}}, "20:58")
        self.assertIn("ERROR: timeout", output)

    def test_slow_provider_is_bounded(self):
        import time
        class Slow:
            key = "slow"
            def fetch(self, timeout):
                time.sleep(2)
        started = time.monotonic()
        result = collect([Slow()], timeout=0.05)
        self.assertLess(time.monotonic() - started, 1)
        self.assertEqual(result["slow"]["error"], "timeout")


if __name__ == "__main__":
    unittest.main()
