from __future__ import annotations

import argparse
from datetime import datetime

from .config import load_config, provider_config
from .core import collect, collect_results, render_json, render_text
from .providers import AnthropicProvider, ClaudeProvider, CodexProvider, CopilotProvider, DeepSeekProvider, GeminiCLIProvider, GeminiProvider, GLMProvider, KimiProvider, MiMoProvider, MiniMaxCodingPlanProvider, MiniMaxProvider, OpenAIProvider, OpenRouterProvider, QwenProvider, SiliconFlowProvider


def build_providers(config: dict, only: str | None = None) -> list[object]:
    specs = {
        "deepseek": lambda: DeepSeekProvider(provider_config(config, "deepseek", "api_key", "DEEPSEEK_API_KEY")),
        "mimo": lambda: MiMoProvider(
            api_key=provider_config(config, "mimo", "api_key", "MIMO_API_KEY"),
            cookie=provider_config(config, "mimo", "cookie", "MIMO_COOKIE"),
        ),
        "kimi": lambda: KimiProvider(provider_config(config, "kimi", "api_key", "MOONSHOT_API_KEY")),
        "glm": lambda: GLMProvider(provider_config(config, "glm", "api_key", "GLM_API_KEY")),
        "claude": ClaudeProvider,
        "codex": lambda: CodexProvider(),
        "openrouter": lambda: OpenRouterProvider(provider_config(config, "openrouter", "api_key", "OPENROUTER_API_KEY")),
        "openai": lambda: OpenAIProvider(provider_config(config, "openai", "admin_key", "OPENAI_ADMIN_KEY"), provider_config(config, "openai", "org_id", "OPENAI_ORG_ID")),
        "anthropic": lambda: AnthropicProvider(provider_config(config, "anthropic", "admin_key", "ANTHROPIC_ADMIN_KEY")),
        "gemini": GeminiProvider,
        "minimax": MiniMaxProvider,
        "qwen": QwenProvider,
        "siliconflow": SiliconFlowProvider,
        "minimax_coding_plan": MiniMaxCodingPlanProvider,
        "github_copilot": CopilotProvider,
        "gemini_cli": GeminiCLIProvider,
    }
    names = [only] if only else list(specs)
    result = []
    for name in names:
        if name not in specs:
            raise ValueError(f"unknown provider: {name}")
        try:
            result.append(specs[name]())
        except Exception as exc:
            result.append(_FailedProvider(name, str(exc)))
    return result


class _FailedProvider:
    def __init__(self, key: str, error: str):
        self.key, self.error = key, error
    def fetch(self, timeout: float = 8.0):
        raise RuntimeError(self.error)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ai-quota", description="Query AI provider quotas")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--only", choices=["deepseek", "mimo", "kimi", "glm", "claude", "codex", "openrouter", "openai", "anthropic", "gemini", "gemini_cli", "minimax", "minimax_coding_plan", "qwen", "siliconflow", "github_copilot"], help="query one provider")
    parser.add_argument("--timeout", type=float, default=8.0, help="per-provider timeout in seconds")
    parser.add_argument("--config", help="config TOML path")
    args = parser.parse_args(argv)
    try:
        data = collect(build_providers(load_config(args.config), args.only), max(0.1, args.timeout))
    except Exception as exc:
        data = {"error": {"status": "error", "error": str(exc)}}
    print(render_json(data) if args.json else render_text(data, datetime.now().astimezone().strftime("%H:%M")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
