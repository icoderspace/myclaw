# PR Monitor Agent

每天检查 Messaging-Connectors 仓库的 active PR，按规则催作者、必要时直接 abandon。

**不是开发组 4 个角色之一**，是独立的运维自动化 agent。由 OpenClaw cron 触发，跑完即退。

## 触发

| 触发器 | 时间 | 实现 |
|---|---|---|
| 每天检查 | **09:00 Asia/Shanghai = 01:00 UTC** | OpenClaw cron (`agentTurn` → isolated session, 或直接 shell exec) |

## 数据源

- **ADO**: `https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_apis/git/repositories/Messaging-Connectors/pullrequests`
- **PAT**: `~/.openclaw/secrets/ado-pat`（workspace 外，不入 git）
- **Teams Bot**: `https://icm-notification-bot.azurewebsites.net/api/activity`（公网，无 auth gate）
- **目标 channel**: `[Connector]PR Push and review`
  - conversationId: `19:785512bc64f946e9b9062b90f176e314@thread.tacv2`

## 分桶规则

PR 是否 **Urgent**（优先级最高，盖过年龄）：
- 作者是 **`Dependabot`** / `dependabot[bot]`，**或**
- 标题包含 `[SECURITY]`（不区分大小写）

| 桶 | 触发条件 | 动作 |
|---|---|---|
| **Urgent** | 上述 Urgent 标记，**无论 age** | 当天就 @ 作者，要求 5d 内 merge；未 merge 持续每天 @；age ≥30 触发 Abandon |
| **Fresh** | 普通 PR，age 0–4 天 | 不动 |
| **Warn** | 普通 PR，age 5–27 天 | 每天 @ 作者催 check-in |
| **Ultimatum** | 普通 PR，age 28–29 天 | **最后通牒**：@ 作者，明确告知"30 天将自动 abandon"。**不**改 PR 状态、**不**标 Draft。 |
| **Abandon** | age ≥ 30 天 | **当前只通知不关**（`PR_MONITOR_NO_ABANDON=1` 默认开）。文案提醒作者自己 merge / abandon。Hao 在测评作者反馈后才会打开真 abandon。 |

> 年龄按自然日（UTC `now - creationDate`，向下取整）。

## 推送策略（一条主消息 / 天）

- 每天 09:00 BJT 跑一次。
- **先 `messageDelete` 昨天的主消息**（state 文件里存了昨天的 `activityId`），再 POST 今天的新消息。
- 一条 Adaptive Card，按桶分段（Urgent → Ultimatum → Warn → Abandon-result），每条 PR 列：作者 @、age、标题、ADO 链接。
- @mention 用 Teams members list 里的 `29:xxx` userId 匹配 ADO 作者 displayName（不区分大小写、忽略括号后缀如 "(Accenture)"）。匹配不到的作者就在文本里写纯文字 `@AuthorName`（不带 entity），并在报告里标注。
- 失败回滚：`messageDelete` 失败不阻塞 POST；POST 失败的话保留昨天的 state 不动。

## 红线

- **绝不**对 PAT owner 自己创建的 PR 触发 abandon（保险绳；防误关）。
- **DRY_RUN 默认开**（`PR_MONITOR_DRY_RUN=1`）：只渲染消息 + 写报告，不调 Teams API、不 abandon。**首次真跑前 Hao 必须看过一次预览**。
- 单条 PR 操作失败不阻塞其它；报告里列失败项。
- 失败 / 异常 → 失败时由 cron `failureAlert` ping 主会话。

## 输出

`team/pr-monitor/runs/<YYYY-MM-DD>.md`：
- 总览（每桶计数）
- 各桶 PR 明细 + 实际执行结果
- 作者匹配失败列表
- HTTP 错误列表

`team/pr-monitor/state.json`：
- `lastActivityId`：昨天主消息的 ID（用于次日删除）
- `lastConversationId`：目标 conversation
- `lastRunUtc`：上次跑的时间

## 文件

- `AGENT.md` — 本文件
- `run.py` — 主脚本
- `state.json` — 跨天状态（首次跑前不存在）
- `runs/<date>.md` — 每天的运行报告
- `SAMPLE-run-*.md` — 历史样例（参考）
