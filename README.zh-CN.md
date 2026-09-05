<div align="center">

# Hermes Quota

用于 Hermes Agent 的 AI 平台余额和 Coding Plan 额度查询插件。

[![Tests](https://github.com/Ayscough/hermes-quota/actions/workflows/test.yml/badge.svg)](https://github.com/Ayscough/hermes-quota/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/Ayscough/hermes-quota)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)

[English](README.md) · 简体中文

</div>

## Hermes 插件

从 GitHub 一键安装：

```bash
hermes plugins install Ayscough/hermes-quota --enable
```

重启 Hermes 后使用：

```text
/quota
/quota --only codex
```

插件同时提供 `get_ai_quota` 工具。当你要求查看 AI 平台额度时，Hermes
可以自动调用它。

`/quota` 会自动读取当前 Hermes profile 使用的 Provider，将它优先显示，
并在下面显示其他已配置的平台。Coding Plan 和订阅窗口会以剩余额度进度条显示。

## 支持的平台

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

通过环境变量或本地 TOML 文件配置凭据：

```bash
cp config.example.toml config.toml
$EDITOR config.toml
chmod 600 config.toml
```

CLI 会自动读取当前目录的 `config.toml` 和
`~/.config/ai-quota/config.toml`。Hermes OAuth 凭据使用正常的 Hermes
凭据目录，包括 `$HERMES_HOME/auth.json` 中的 Codex 凭据。

凭据只保留在本机，并只发送给正在查询的平台。

## 独立 CLI

底层 CLI 也可以独立安装和使用：

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

## 开发

```bash
.venv/bin/pip install pytest
.venv/bin/pytest -q
```

## 许可证

MIT
