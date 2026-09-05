"""Hermes plugin for the ai-quota CLI."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


_ONLY_CHOICES = {
    "deepseek", "mimo", "kimi", "glm", "claude", "codex", "openrouter",
    "openai", "anthropic", "gemini", "gemini_cli", "minimax",
    "minimax_coding_plan", "qwen", "siliconflow", "github_copilot",
}
_PROVIDER_MAP = {
    "openai-codex": "codex",
    "anthropic": "anthropic",
    "kimi-coding": "kimi",
    "kimi-coding-cn": "kimi",
    "zai": "glm",
    "xiaomi": "mimo",
    "minimax": "minimax",
    "minimax-cn": "minimax",
    "openrouter": "openrouter",
    "deepseek": "deepseek",
}
_ENV_BY_PROVIDER = {
    "deepseek": ("DEEPSEEK_API_KEY",),
    "mimo": ("MIMO_API_KEY", "MIMO_COOKIE"),
    "kimi": ("KIMI_API_KEY", "MOONSHOT_API_KEY", "KIMI_CN_API_KEY"),
    "glm": ("GLM_API_KEY", "ZAI_API_KEY"),
    "claude": ("CLAUDE_CODE_OAUTH_TOKEN",),
    "codex": ("OPENAI_API_KEY", "CODEX_AUTH_FILE"),
    "openrouter": ("OPENROUTER_API_KEY",),
    "openai": ("OPENAI_ADMIN_KEY", "OPENAI_ORG_ID"),
    "anthropic": ("ANTHROPIC_ADMIN_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "gemini_cli": ("GEMINI_OAUTH_FILE",),
    "minimax": ("MINIMAX_API_KEY", "MINIMAX_CODING_API_KEY"),
    "qwen": ("DASHSCOPE_API_KEY",),
    "siliconflow": ("SILICONFLOW_API_KEY",),
    "github_copilot": ("GITHUB_COPILOT_TOKEN", "GH_TOKEN"),
}


def _hermes_home() -> Path:
    return Path(os.getenv("HERMES_HOME", "~/.hermes")).expanduser()


def _current_provider() -> str | None:
    """Read the active Hermes provider without importing Hermes internals."""
    path = _hermes_home() / "config.yaml"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    in_model = False
    for line in lines:
        if line.startswith("model:"):
            in_model = True
            continue
        if in_model and line and not line[0].isspace():
            break
        if in_model and line.strip().startswith("provider:"):
            return line.split(":", 1)[1].strip().strip("\"'") or None
    return None


def _config_paths() -> list[Path]:
    paths = []
    configured = os.getenv("AI_QUOTA_CONFIG")
    if configured:
        paths.append(Path(configured).expanduser())
    paths.extend([
        Path.cwd() / "config.toml",
        Path("~/.config/ai-quota/config.toml").expanduser(),
    ])
    return list(dict.fromkeys(paths))


def _configured(provider: str) -> bool:
    if any(os.getenv(name, "").strip() for name in _ENV_BY_PROVIDER.get(provider, ())):
        return True
    try:
        import tomllib
        for path in _config_paths():
            if path.exists():
                section = tomllib.loads(path.read_text(encoding="utf-8")).get(provider, {})
                if isinstance(section, dict) and any(str(value).strip() for value in section.values()):
                    return True
    except (OSError, ValueError, TypeError):
        return False
    if provider == "codex":
        return bool(os.getenv("CODEX_AUTH_FILE") or (Path("~/.codex/auth.json").expanduser()).exists()
                    or (_hermes_home() / "auth.json").exists())
    if provider == "claude":
        return (Path(os.getenv("CLAUDE_CONFIG_DIR", "~/.claude")).expanduser()
                / ".credentials.json").exists()
    return False


def _command(args: list[str]) -> list[str]:
    executable = shutil.which("ai-quota")
    if executable:
        return [executable, *args]
    return [sys.executable, "-m", "ai_quota", *args]


def _query(args: list[str]) -> dict:
    env = os.environ.copy()
    plugin_root = Path(__file__).resolve().parent
    env["PYTHONPATH"] = str(plugin_root) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        result = subprocess.run(
            _command(args),
            cwd=Path.cwd(),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        return {"error": {"status": "error", "error": "ai-quota is not installed"}}
    except subprocess.TimeoutExpired:
        return {"error": {"status": "error", "error": "ai-quota timed out"}}
    output = (result.stdout or result.stderr).strip()
    if not output:
        return {"error": {"status": "error", "error": f"ai-quota exited with code {result.returncode}"}}
    try:
        payload = json.loads(output)
        return payload if isinstance(payload, dict) else {"error": {"status": "error", "error": "invalid JSON"}}
    except json.JSONDecodeError:
        return {"error": {"status": "error", "error": output}}


def _visible(payload: dict, current: str | None) -> dict:
    current_key = _PROVIDER_MAP.get(current or "")
    result = {}
    for key, item in payload.items():
        if not isinstance(item, dict):
            continue
        if item.get("status") == "ok" or key == current_key or _configured(key):
            result[key] = item
    if current_key and current_key in payload and current_key not in result:
        result[current_key] = payload[current_key]
    return result


def _bar(remaining: float, width: int = 12) -> str:
    remaining = max(0.0, min(100.0, remaining))
    filled = round(width * remaining / 100)
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def _windows(item: dict) -> list[tuple[str, float]]:
    windows = []
    for label, field in (
        ("5h", "five_hour_used_percent"),
        ("7d", "seven_day_used_percent"),
        ("5h", "primary_used_percent"),
        ("7d", "secondary_used_percent"),
        ("quota", "used_percent"),
    ):
        if field in item:
            windows.append((label, 100.0 - float(item[field])))
    for index, window in enumerate(item.get("windows", []), 1):
        if isinstance(window, dict) and "used_percent" in window:
            windows.append((f"w{index}", 100.0 - float(window["used_percent"])))
    if "remaining_percent" in item:
        windows.append(("quota", float(item["remaining_percent"])))
    return windows


def _render(payload: dict, current: str | None = None) -> str:
    current_key = _PROVIDER_MAP.get(current or "")
    visible = _visible(payload, current)
    ordered = sorted(visible.items(), key=lambda pair: (pair[0] != current_key, pair[0]))
    lines = ["AI Quota", "────────────────────────"]
    for key, item in ordered:
        label = key.replace("_", " ").title()
        marker = " *" if key == current_key else "  "
        if item.get("status") != "ok":
            lines.append(f"{marker}{label:<15}ERROR: {item.get('error', 'unknown error')}")
            continue
        windows = _windows(item)
        if windows:
            values = "  ".join(f"{name} {_bar(rem)} {rem:.0f}%" for name, rem in windows)
            lines.append(f"{marker}{label:<15}{values} remaining")
        elif "balance" in item:
            lines.append(f"{marker}{label:<15}{item['balance']:.2f} {item.get('currency', '')}".rstrip())
        else:
            lines.append(f"{marker}{label:<15}ok")
    lines += ["────────────────────────", f"* current: {current or 'unknown'}"]
    return "\n".join(lines)


def _args_from_raw(raw_args: str) -> tuple[list[str] | None, str | None]:
    parser = argparse.ArgumentParser(prog="/quota", add_help=False)
    parser.add_argument("--only", choices=sorted(_ONLY_CHOICES))
    parser.add_argument("--timeout", type=float, default=8.0)
    try:
        parsed = parser.parse_args(shlex.split(raw_args))
    except (ValueError, SystemExit):
        return None, "Usage: /quota [--only PROVIDER] [--timeout SECONDS]"
    if parsed.timeout <= 0:
        return None, "Usage: /quota [--only PROVIDER] [--timeout SECONDS]"
    command = ["--json", "--timeout", str(parsed.timeout)]
    if parsed.only:
        command.extend(["--only", parsed.only])
    return command, None


def get_ai_quota(args: dict, **kwargs) -> str:
    """Return configured provider quotas as JSON."""
    command = ["--json", "--timeout", str(args.get("timeout", 8.0))]
    only = args.get("only")
    if only:
        if only not in _ONLY_CHOICES:
            return json.dumps({"error": f"unknown provider: {only}"})
        command.extend(["--only", only])
    return json.dumps(_query(command), ensure_ascii=False, indent=2)


def register(ctx):
    schema = {
        "name": "get_ai_quota",
        "description": "Query configured AI provider balances and coding-plan quotas. Return JSON.",
        "parameters": {
            "type": "object",
            "properties": {
                "only": {"type": "string", "enum": sorted(_ONLY_CHOICES), "description": "Optional provider name."},
                "timeout": {"type": "number", "description": "Per-provider timeout in seconds (default 8)."},
            },
            "additionalProperties": False,
        },
    }
    ctx.register_tool(name="get_ai_quota", toolset="ai_quota", schema=schema, handler=get_ai_quota)

    def handle_quota(raw_args: str) -> str:
        command, error = _args_from_raw(raw_args)
        if error:
            return error
        assert command is not None
        payload = _query(command)
        return _render(payload, _current_provider())

    ctx.register_command(
        "quota",
        handler=handle_quota,
        description="Show current and configured AI provider quotas",
        args_hint="[--only PROVIDER] [--timeout SECONDS]",
    )
