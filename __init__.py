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


def _command(args: list[str]) -> list[str]:
    executable = shutil.which("ai-quota")
    if executable:
        return [executable, *args]
    # The Git-installed plugin also contains the ai_quota package.
    return [sys.executable, "-m", "ai_quota", *args]


def _run(args: list[str]) -> str:
    env = os.environ.copy()
    plugin_root = str(Path(__file__).resolve().parent)
    env["PYTHONPATH"] = plugin_root + os.pathsep + env.get("PYTHONPATH", "")
    try:
        result = subprocess.run(
            _command(args),
            cwd=plugin_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except FileNotFoundError:
        return json.dumps({"error": "ai-quota is not installed; run the project installer"})
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "ai-quota timed out"})
    output = (result.stdout or result.stderr).strip()
    if not output:
        return json.dumps({"error": f"ai-quota exited with code {result.returncode}"})
    try:
        return json.dumps(json.loads(output), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return json.dumps({"error": output}, ensure_ascii=False)


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
    return _run(command)


def register(ctx):
    schema = {
        "name": "get_ai_quota",
        "description": "Query configured AI provider balances and coding-plan quotas. Return JSON.",
        "parameters": {
            "type": "object",
            "properties": {
                "only": {
                    "type": "string",
                    "enum": sorted(_ONLY_CHOICES),
                    "description": "Optional provider name; omit to query all configured providers.",
                },
                "timeout": {
                    "type": "number",
                    "description": "Per-provider timeout in seconds (default 8).",
                },
            },
            "additionalProperties": False,
        },
    }
    ctx.register_tool(
        name="get_ai_quota",
        toolset="ai_quota",
        schema=schema,
        handler=get_ai_quota,
    )

    def handle_quota(raw_args: str) -> str:
        command, error = _args_from_raw(raw_args)
        if error:
            return error
        assert command is not None
        return _run(command)

    ctx.register_command(
        "quota",
        handler=handle_quota,
        description="Show configured AI provider quotas",
        args_hint="[--only PROVIDER] [--timeout SECONDS]",
    )
