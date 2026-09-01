# ai-quota

极简本地 AI API/订阅额度查询 CLI。当前注册：DeepSeek、Xiaomi MiMo、Kimi、GLM、OpenRouter、OpenAI、Anthropic、Gemini、MiniMax、Qwen、SiliconFlow、Claude Code、Codex。

## 安装

```bash
cd ~/ai-quota
.venv/bin/pip install -e .
```

安装后运行：

```bash
ai-quota
ai-quota --json
ai-quota --only deepseek
ai-quota --only kimi
ai-quota --only glm
ai-quota --only claude
ai-quota --only codex
ai-quota --only openrouter
ai-quota --only openai
ai-quota --only anthropic
ai-quota --only gemini
ai-quota --only minimax
ai-quota --only qwen
ai-quota --only siliconflow
```

## 凭据

推荐使用环境变量（不会写入源码）：

```bash
export DEEPSEEK_API_KEY='你的 DeepSeek API Key'
export MIMO_COOKIE='从 MiMo 控制台请求复制的 Cookie 头'
export MOONSHOT_API_KEY='你的 Kimi API Key'
export GLM_API_KEY='你的 GLM API Key'
export ANTHROPIC_ADMIN_KEY='你的 Claude Admin API Key'
export OPENROUTER_API_KEY='你的 OpenRouter API Key'
export OPENAI_ADMIN_KEY='你的 OpenAI Admin Key'
export OPENAI_ORG_ID='你的 OpenAI Organization ID（可选）'
export GEMINI_API_KEY='你的 Gemini API Key'
```

启用 Coding Plan 查询：

```bash
export KIMI_CODING_PLAN=1
export GLM_CODING_PLAN=1
```

Codex 和 Claude Code 订阅模式会读取本机 CLI 的登录凭据：

- Codex：`~/.codex/auth.json`，也可用 `CODEX_AUTH_FILE` 指定
- Claude Code：`~/.claude/.credentials.json`，也遵循 `CLAUDE_CONFIG_DIR`

这两类 OAuth 凭据属于本机敏感文件，程序只读 access token，不会输出或写入 token。

也可写入 `~/.config/ai-quota/config.toml`：

```toml
[deepseek]
api_key = "..."

[mimo]
cookie = "api-platform_serviceToken=...; userId=..."
```

环境变量优先于 TOML。MiMo 使用网页登录 Cookie，Cookie 过期后需重新复制；程序不会自动登录或绕过登录。

## 当前支持

API：

- DeepSeek
- Kimi / Moonshot
- OpenRouter
- OpenAI Organization Usage/Costs
- Anthropic Usage & Cost

Coding Plan / Agent：

- Xiaomi MiMo
- Kimi Code
- GLM / Z.ai Coding Plan
- MiniMax Coding Plan
- Codex
- Claude Code
- Gemini CLI
- GitHub Copilot

每个 Provider 查询失败时，其他 Provider 继续执行。网络请求默认超时 8 秒。

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

## 凭据安全

凭据只从环境变量、本地配置文件或对应客户端的本地登录文件读取，不写入源码，不上传网络，不自动登录。

## Hermes

Hermes 已可通过终端工具调用：

```bash
ai-quota --json
```

因此不增加额外 Skill，也不修改 Hermes 核心配置。Hermes 直接通过 terminal 执行 `ai-quota --json` 即可。
