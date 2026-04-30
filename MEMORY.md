# MEMORY.md — Claw 长期记忆

> 这是我的"长期记忆"——精炼后的关键事实，不是日记。
> 详细日志在 `memory/YYYY-MM-DD.md`。

## 关于 Hao

- 全名：**Hao Ling**，ADO/公司 alias：**haling**
- 北京时区 (UTC+8)，主用中文
- 当前只在网页 webchat 对接（不接 WhatsApp/Telegram）
- **主动推送**：Hao 不一定经常刷网页，有事我主动往 webchat 发就行（PAT 到期、PR 异常、heartbeat 发现的事等）
- 喜欢直接、专业的沟通；反感堆砌话术、想当然
- "知之为知之，不知为不知" 是基本要求

## 关键同事 alias

- **yanling** = Ling Yang（跟 Hao 不是同一人，完全不同的同事）
- 以后遇到 SME / author 字段里的 alias不要当成 Hao

## 关于我（Claw）

- 角色：**团队负责人**，对外是 Hao 的单一对接人
- 我下面有开发组：PM / Coder / Tester / Reviewer，按需 spawn isolated 子会话激活
- 我**不让** Hao 直接 @ 团队成员；所有沟通都经我

## 工作区 & Git

- workspace: `/home/azureuser/.openclaw/workspace`
- 远程仓库（**私有**）: `git@github.com:icoderspace/myclaw.git`
- SSH key: `~/.ssh/id_ed25519_claw`（公钥已加 GitHub）
- git 身份: `Claw <claw@openclaw.local>`
- **自动同步**: 系统 crontab `*/30 * * * *` 跑 `.openclaw/git-autosync.sh`，零 token 成本

## 当前在做的项目：Messaging-Connectors

- ADO Org: **msdata**
- ADO Project: **Messaging Connectors and Event Streams**
- 主仓库本地路径: `~/repos/Messaging-Connectors`
- 项目章程：`team/PROJECT.md`（从仓库内 `.github/copilot-instructions.md` 提炼）
- 业务：Azure 托管的 Kafka Connect connectors（Event Streams / KCaaS）
- 技术栈：C#/.NET 8（Control Plane）+ Java 17（Runtime Plugin）+ Camel/Kafka forks + EV2 部署

## Teams 渠道 (通过 RTI Copilot bot `https://icm-notification-bot.azurewebsites.net`)

- **Hao DM (1:1)** — 只有 Hao 看得到，默认预览 / 堆东西都发这里：
  `a:1ybI-9qx2WMN_JoCouIhiL9Ys44rIEvVCJfEIJPmllqLPgz4oCGKZZT71o0L5Lsr-RCjvf4HpsVL9tiwd6W6KMqORvDnLBXUPFxJDXajCGu15h6w-7Zz4sT54mAQBal5Y`
- **PR Daily Pulse group thread**（9 位 PR author + Hao）：
  `19:785512bc64f946e9b9062b90f176e314@thread.tacv2`
- POST 格式：`POST {BOT}/api/activity` body `{conversationId, activity}`，无 auth gate。

## ADO 接入

- **认证方式**：PAT（不是 UMI，UMI 走不通因为 org 只给 Stakeholder license）
- PAT 文件: `~/.openclaw/secrets/ado-pat`（**workspace 外部**，不会被 push）
- 当前 PAT 过期: **2026-05-06 07:13 UTC**
- 提醒已设: T-2d / T-1d / T-2h cron
- **轮换流程**: Hao 发新 PAT → 我 `echo "<NEW>" > ~/.openclaw/secrets/ado-pat`，旧的 Hao 那边 revoke

## 关键红线

### 项目层（来自 Messaging-Connectors）
- **不许擅自 push / 开 PR**，必须 Hao 明确说 "create PR"
- Push 前必须本地跑静态检查（Java: checkstyle/spotbugs/sonarlint；C#: CodeStyleTest）
- Kusto 查询必须先读 `docs/Troubleshooting/Kusto-Log-Query-Guide.md`
- `tools/rti-copilot/**` 子项目独立规则：Conventional Commits + 必带 `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`

### 我层
- 大功能必先写 plan，Hao 批准后才执行
- ADO PAT 绝不出现在 push 文件里、绝不通过第三方 API 发出去
- 团队成员之间不直接通话，统一经过我

## 在跑的 Agent

- **PR Monitor**（草案中）：`team/pr-monitor/`，每天 09:00 BJT 检查 active PR，5d 提醒 / 30d abandon。**未上线**，等 Hao 给 Teams webhook + 豁免规则。

## 项目级 AI 资产

仓库里有自己的 AI agent 体系（`.github/agents/` + `.github/instructions/`），是按业务场景分的（onboard 新 connector、bug 分诊、IcM、runtime exception 等）。
- 跟我们的 PM/Coder/Tester/Reviewer 是**互补**关系
- 派活时如果场景对得上，对应角色读相应 agent.md 当专家手册

## 对自己的提醒

- **会话 token 越积越多，回复越慢**——长任务后建议开新会话 + 考虑切 Sonnet
- "steer" 是 OpenClaw 把消息插进未结束 turn，不是排队，但容易让 Hao 困惑——做长任务时别让 UI 状态拖太久
- Hao 的工作风格：他**会**愿意在线等我做完事，但喜欢看到清晰的中间汇报
