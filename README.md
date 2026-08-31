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

## 数据来源与限制

- DeepSeek：官方 `GET https://api.deepseek.com/user/balance`
- MiMo：控制台 API 的 balance 与 token-plan usage 接口；接口可能随官方控制台调整
- Kimi 普通 API：`GET https://api.moonshot.ai/v1/users/me/balance`；Kimi Coding Plan：`GET https://api.kimi.com/coding/v1/usages`
- GLM 普通 API：`/balance`；GLM Coding Plan：`/api/monitor/usage/quota/limit`
- Claude：优先读取 Claude Code OAuth 凭据，请求 `/api/oauth/usage`，可以得到 5 小时和 7 天订阅窗口；不是 API 账单余额
- Codex：读取 Codex OAuth 凭据，请求 ChatGPT backend 的 `/wham/usage`，得到 5 小时和 7 天窗口；该接口是 Codex 客户端使用的非公开产品接口
- OpenRouter：官方 `GET https://openrouter.ai/api/v1/key`，查询 Key 额度与日/周/月使用量
- OpenAI：Organization Admin API 的 `/v1/organization/costs`，查询近 30 天成本；普通 API Key 无法查询组织账单
- Anthropic：Usage & Cost Admin API 的 `/v1/organizations/cost_report`，查询近 30 天成本；需要 Admin API Key
- Gemini：Google AI Studio 的实时项目限额没有稳定的单一余额 API，因此未伪造接口；可通过 `GEMINI_QUOTA_URL` 接入已验证的官方配额端点
- MiniMax、Qwen、SiliconFlow：当前没有统一稳定的公开余额接口，默认明确返回 `unsupported`；只有设置对应的 `*_BALANCE_URL` 后才请求

单个 Provider 失败不会阻塞其他 Provider；网络请求默认每个 8 秒超时。

## 阶段化支持矩阵

已实现或接入：

- API：DeepSeek、Kimi/Moonshot、OpenRouter、OpenAI Admin Costs、Anthropic Admin Costs
- Coding Plan：Kimi Code、GLM/Z.ai Coding Plan、MiMo Token Plan、MiniMax Coding Plan
- Agent 订阅：Codex、Claude Code、Gemini CLI、GitHub Copilot
- 条件支持：Gemini、MiniMax、Qwen、SiliconFlow 可通过已验证的自定义官方 endpoint 接入

实验性接口（Codex、Claude Code、Kimi Code、GLM/Z.ai、MiniMax Coding Plan、Gemini CLI、Copilot）可能因平台接口变化而失效。程序会返回错误，不会把失败伪装成 0% 或 100%。

## 公开发布边界

本项目是本地 CLI，不会自动登录、绕过验证码、读取无关浏览器数据或上传凭据。网页 Cookie 和 OAuth 适配器只读取用户明确配置的本地凭据。没有稳定公开额度 API 的产品不会被标记为稳定支持。

## Hermes

Hermes 已可通过终端工具调用：

```bash
ai-quota --json
```

因此不增加额外 Skill，也不修改 Hermes 核心配置。Hermes 直接通过 terminal 执行 `ai-quota --json` 即可。
