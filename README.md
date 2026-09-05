<div align="center">

# ai-quota

Local-first CLI for checking AI API and coding-plan quotas.

[![Tests](https://github.com/Ayscough/ai-quota/actions/workflows/test.yml/badge.svg)](https://github.com/Ayscough/ai-quota/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/Ayscough/ai-quota)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)

[English](README.md) · [简体中文](README.zh-CN.md)

</div>

## Features

- Minimal terminal output
- Structured JSON output
- Independent provider failures
- Per-provider timeout control
- Environment-variable and TOML configuration
- Works directly from Hermes Agent through the terminal

## Install

```bash
git clone https://github.com/Ayscough/ai-quota.git
cd ai-quota
python3 -m venv .venv
.venv/bin/pip install -e .
ln -sf "$PWD/.venv/bin/ai-quota" "$HOME/.local/bin/ai-quota"
```

## Usage

```bash
ai-quota
ai-quota --json
ai-quota --only deepseek
ai-quota --timeout 5
```

Example:

```text
AI Quota
────────────────
DeepSeek    ¥32.41
MiMo        68%
────────────────
updated 20:58
```

## Supported providers

- DeepSeek
- Xiaomi MiMo
- Kimi / Moonshot
- Kimi Code
- GLM / Z.ai Coding Plan
- Claude Code
- Codex
- OpenRouter
- OpenAI Organization Usage/Costs
- Anthropic Usage & Cost
- MiniMax Coding Plan
- Gemini CLI
- GitHub Copilot

## Configuration

Environment variables:

```bash
export DEEPSEEK_API_KEY='...'
export MIMO_API_KEY='...'
export MIMO_COOKIE='...'
export KIMI_API_KEY='...'
export GLM_API_KEY='...'
export OPENROUTER_API_KEY='...'
export OPENAI_ADMIN_KEY='...'
export OPENAI_ORG_ID='...'
export ANTHROPIC_ADMIN_KEY='...'
export MINIMAX_CODING_API_KEY='...'
export GITHUB_COPILOT_TOKEN='...'
export GEMINI_OAUTH_FILE="$HOME/.gemini/oauth_creds.json"
```

Or place a `config.toml` in the project directory:

```bash
cp config.example.toml config.toml
$EDITOR config.toml
```

The CLI reads this file automatically. It also looks for `~/.config/ai-quota/config.toml`.

Your keys stay on your machine. `ai-quota` only sends them to the provider you query.

## Hermes Plugin

Install the plugin directly from GitHub:

```bash
hermes plugins install Ayscough/ai-quota --enable
```

Then use either:

```text
/quota
/quota --only codex
```

Hermes also gets the `get_ai_quota` tool and can call it when you ask to check
AI provider balances. The plugin runs `ai-quota --json` locally and does not
modify Hermes core files.

## Development

```bash
.venv/bin/pip install pytest
.venv/bin/pytest -q
```

## License

MIT
