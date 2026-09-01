# ai-quota

本地 AI API 和 Coding Plan 额度查询 CLI。

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

## 暂未支持

- Cursor
- OpenCode Go
- Alibaba Coding Plan
- Alibaba Token Plan
- Qwen Cloud / Qwen Code
- Google Antigravity
- Devin
- Grok
- Manus

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

也可以使用本地配置文件：

```bash
mkdir -p ~/.config/ai-quota
cp config.example.toml ~/.config/ai-quota/config.toml
chmod 600 ~/.config/ai-quota/config.toml
```

MiMo 使用登录后的 Cookie。Codex、Claude Code、Gemini CLI 读取对应客户端的本地登录凭据。

## Hermes Agent

Hermes 可直接执行：

```bash
ai-quota --json
```

## License

MIT
