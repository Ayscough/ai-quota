<div align="center">

# ai-quota

Local-first CLI for checking AI API and coding-plan quotas.

[![Tests](https://github.com/Ayscough/ai-quota/actions/workflows/test.yml/badge.svg)](https://github.com/Ayscough/ai-quota/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/Ayscough/ai-quota)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)

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
export MIMO_COOKIE='...'
export MOONSHOT_API_KEY='...'
export GLM_API_KEY='...'
export OPENROUTER_API_KEY='...'
export OPENAI_ADMIN_KEY='...'
export OPENAI_ORG_ID='...'
export ANTHROPIC_ADMIN_KEY='...'
export MINIMAX_CODING_API_KEY='...'
export GITHUB_COPILOT_TOKEN='...'
export GEMINI_OAUTH_FILE="$HOME/.gemini/oauth_creds.json"
```

Or use a local file:

```bash
mkdir -p ~/.config/ai-quota
cp config.example.toml ~/.config/ai-quota/config.toml
chmod 600 ~/.config/ai-quota/config.toml
```

Never commit real keys, cookies, or OAuth files.

## Hermes Agent

Hermes can call the CLI directly:

```bash
ai-quota --json
```

## Development

```bash
.venv/bin/pip install pytest
.venv/bin/pytest -q
```

## License

MIT
