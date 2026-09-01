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

## 数据来源与支持边界

### 稳定支持

以下 Provider 使用公开文档中的官方 API，并且输出仅表示 API 返回的余额、额度或成本数据：

- DeepSeek API：官方余额接口
- Kimi/Moonshot API：官方余额接口
- OpenRouter API：官方 Key usage/limit 接口
- OpenAI API：官方 Organization Usage/Costs API；需要组织级 Admin Key
- Anthropic API：官方 Usage & Cost Admin API；需要组织级 Admin Key

### 实验性支持

以下适配器可能依赖产品登录态、本地 CLI 凭据、Cookie，或平台没有承诺长期稳定的接口。它们默认不构成稳定 API 兼容承诺：

- Xiaomi MiMo Token Plan：控制台登录态；需要用户手动提供 Cookie
- Kimi Code、GLM/Z.ai Coding Plan、MiniMax Coding Plan
- Codex、Claude Code、Gemini CLI、GitHub Copilot

这些适配器只在用户明确配置凭据后运行。接口变化、账号类型差异或登录过期时，程序会返回错误，不会伪造额度。

### 暂不承诺支持

Gemini API、MiniMax API、Qwen API、SiliconFlow API，以及 Cursor、OpenCode Go、Alibaba/Qwen Cloud、Antigravity、Devin、Grok、Manus 等产品，目前没有在本项目中承诺稳定的官方额度查询支持。

原因可能包括：

- 平台只在控制台展示额度，没有公开查询 API
- 额度属于消费者订阅或 Coding Plan，而不是 API 账户余额
- 接口是内部网页接口，随时可能变化
- 需要浏览器自动化、设备授权或额外风控流程

### 安全边界

本项目不会自动登录、绕过验证码、上传 Cookie、读取无关浏览器数据，或把私有接口描述成官方公开 API。所有非公开接口适配器都必须保持 `experimental` 定位。

单个 Provider 失败不会阻塞其他 Provider；网络请求默认每个 8 秒超时。

## 支持矩阵

| 产品 | 类型 | 状态 | 数据来源 |
|---|---|---|---|
| DeepSeek | API | stable | 官方 API |
| Kimi/Moonshot | API | stable | 官方 API |
| OpenRouter | API | stable | 官方 API |
| OpenAI | API | stable | Organization Admin API |
| Anthropic | API | stable | Usage & Cost Admin API |
| MiMo | Coding Plan | experimental | 控制台登录态 |
| Kimi Code | Coding Plan | experimental | 产品登录态/API |
| GLM/Z.ai | Coding Plan | experimental | 产品登录态/API |
| MiniMax | Coding Plan | experimental | 产品登录态/API，需账户验证 |
| Codex | Subscription | experimental | 本地客户端登录态 |
| Claude Code | Subscription | experimental | 本地客户端登录态 |
| Gemini CLI | Subscription | experimental | 本地 CLI 登录态 |
| GitHub Copilot | Subscription | experimental | GitHub 登录态/API |
| Cursor | Coding Plan | planned | 尚未稳定接入 |
| OpenCode Go | Subscription | planned | 尚未稳定接入 |
| Alibaba/Qwen Cloud | Coding Plan | planned | 尚未稳定接入 |

“stable”只表示接口来源公开且契约相对明确，不代表平台永不变更；“experimental”不保证所有账号、地区和套餐都可用。

## 公开发布边界

这是一个本地 CLI 和 Provider 适配实验项目，不是官方客户端，也不是账单系统。发布前请确认自己的凭据没有进入 Git 历史，并阅读各 Provider 的官方服务条款。

## Hermes

Hermes 已可通过终端工具调用：

```bash
ai-quota --json
```

因此不增加额外 Skill，也不修改 Hermes 核心配置。Hermes 直接通过 terminal 执行 `ai-quota --json` 即可。
