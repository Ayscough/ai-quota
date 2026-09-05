from __future__ import annotations

import importlib.util
from pathlib import Path


PLUGIN = Path(__file__).parents[1] / "__init__.py"


def load_plugin():
    spec = importlib.util.spec_from_file_location("ai_quota_hermes_plugin", PLUGIN)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plugin_detects_current_hermes_provider(tmp_path, monkeypatch):
    plugin = load_plugin()
    (tmp_path / "config.yaml").write_text(
        "model:\n  default: gpt\n  provider: openai-codex\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    assert plugin._current_provider() == "openai-codex"


def test_plugin_renders_current_coding_plan_first():
    plugin = load_plugin()
    payload = {
        "codex": {
            "status": "ok",
            "primary_used_percent": 25,
            "secondary_used_percent": 60,
            "plan": "plus",
        },
        "kimi": {"status": "ok", "remaining_percent": 40},
    }
    rendered = plugin._render(payload, "openai-codex")
    assert rendered.index("Codex") < rendered.index("Kimi")
    assert "[█████████░░░] 75%" in rendered
    assert "[█████░░░░░░░] 40%" in rendered
    assert "* current: openai-codex" in rendered


def test_plugin_hides_unconfigured_provider(monkeypatch):
    plugin = load_plugin()
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(plugin, "_config_paths", lambda: [])
    payload = {
        "deepseek": {"status": "error", "error": "not configured"},
        "codex": {"status": "ok", "primary_used_percent": 10},
    }
    rendered = plugin._render(payload, "openai-codex")
    assert "Deepseek" not in rendered
    assert "Codex" in rendered
