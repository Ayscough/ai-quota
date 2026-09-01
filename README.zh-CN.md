<div align="center">

# ai-quota

本地 AI API 和 Coding Plan 额度查询 CLI。

[![Tests](https://github.com/Ayscough/ai-quota/actions/workflows/test.yml/badge.svg)](https://github.com/Ayscough/ai-quota/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/Ayscough/ai-quota)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)

[English](README.md) · 简体中文

</div>

## 功能

- 简洁的终端输出
- JSON 机器可读输出
- Provider 独立失败处理
- 单 Provider 超时控制
- 支持环境变量和 TOML 配置
- 可直接被 Hermes Agent 调用

## 安装

```bash
git clone https://github.com/Ayscough/ai-quota.git
cd ai-quota
python3 -m venv .venv
.venv/bin/pip install -e .
ln -sf "$PWD/.venv/bin/ai-quota" "$HOME/.local/bin/ai-quota"
```

## 使用

```bash
ai-quota
ai-quota --json
ai-quota --only deepseek
ai-quota --timeout 5
```

示例：

```text
AI Quota
────────────────
DeepSeek    ¥32.41
MiMo        68%
────────────────
updated 20:58
```

## 当前支持

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

## 配置

环境变量：

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

也可以把 `config.toml` 放在项目目录里：

```bash
cp config.example.toml config.toml
$EDITOR config.toml
```

CLI 会自动读取这个文件，也会读取 `~/.config/ai-quota/config.toml`。

凭据只留在你的机器上，`ai-quota` 只会把它们发给你正在查询的 Provider。

## Hermes Agent

Hermes 可以直接执行：

```bash
ai-quota --json
```

## 开发

```bash
.venv/bin/pip install pytest
.venv/bin/pytest -q
```

## 许可证

MIT
