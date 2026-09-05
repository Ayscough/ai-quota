<div align="center">

# Hermes Quota

Hermes Agent plugin for checking AI provider balances and coding-plan quotas.

[![Tests](https://github.com/Ayscough/hermes-quota/actions/workflows/test.yml/badge.svg)](https://github.com/Ayscough/hermes-quota/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/Ayscough/hermes-quota)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)

[English](README.md) · [简体中文](README.zh-CN.md)

</div>

## Hermes Plugin

Install directly from GitHub:

```bash
hermes plugins install Ayscough/hermes-quota --enable
```

Restart Hermes, then use:

```text
/quota
/quota --only codex
```

The plugin also provides the `get_ai_quota` tool. Hermes can call it when you
ask to check AI provider quotas.

`/quota` automatically detects the Provider configured in the current Hermes
profile, puts it first, and shows other configured providers below it. Coding
Plan and subscription windows are displayed as remaining-capacity progress bars.

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

Set provider credentials with environment variables or a local TOML file:

```bash
cp config.example.toml config.toml
$EDITOR config.toml
chmod 600 config.toml
```

The CLI reads `config.toml` from the current directory and
`~/.config/ai-quota/config.toml`. Hermes OAuth credentials are read from the
normal Hermes credential locations, including Codex credentials in
`$HERMES_HOME/auth.json`.

Credentials stay on your machine and are sent only to the provider being
queried.

## Standalone CLI

The underlying CLI can also be installed and used independently:

```bash
git clone https://github.com/Ayscough/hermes-quota.git
cd hermes-quota
python3 -m venv .venv
.venv/bin/pip install -e .
ln -sf "$PWD/.venv/bin/ai-quota" "$HOME/.local/bin/ai-quota"
```

```bash
ai-quota
ai-quota --json
ai-quota --only codex
```

## Development

```bash
.venv/bin/pip install pytest
.venv/bin/pytest -q
```

## License

MIT
