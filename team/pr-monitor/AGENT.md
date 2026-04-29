# PR Monitor Agent

每天检查 Messaging-Connectors 仓库的 active PR，提醒滞留作者，关闭超期僵尸 PR。

**这不是开发组的 4 个角色之一**。它是个独立的运维自动化 agent，由 cron 定时触发，跑完即退。

## 触发

| 触发器 | 时间 | 实现 |
|---|---|---|
| 每天检查 | 09:00 Asia/Shanghai = 01:00 UTC | OpenClaw cron (`agentTurn` to isolated session) |

## 输入

无（自取数据）：
- ADO PAT: `~/.openclaw/secrets/ado-pat`
- Org: `msdata`
- Project: `Messaging Connectors and Event Streams`
- Repo: `Messaging-Connectors`

## 阈值

| 桶 | 年龄（自然日） | 动作 |
|---|---|---|
| Fresh | 0–4 天 | 不动 |
| Warn | **5–29 天** | 发 Teams 提醒，@ author 催 check-in |
| Stale | **≥30 天** | **直接 abandon**（ADO 上没有"close"，对应状态是 `abandoned`），并在 PR 上留一条 comment 解释 |

## 数据流

```
1. GET /pullrequests?status=active&top=200
   → 拿到全部 active PR
2. 对每个 PR 计算 age = now - creationDate
3. 分桶：fresh / warn / stale
4. 对 warn 桶：
     - 渲染 Teams Adaptive Card（一条聚合消息，分组按 author）
     - POST 到 Teams webhook
5. 对 stale 桶（每个 PR 独立）：
     - POST comment: "This PR has been inactive for {age} days; closed automatically by PR Monitor. Reopen or recreate if still relevant."
     - PATCH /pullRequests/{id}  body { "status": "abandoned" }
6. 写报告 team/pr-monitor/runs/<YYYY-MM-DD>.md
7. 失败 → escalate 到 Claw（system event）
```

## 红线

- **绝不**对自己（PAT owner）创建的 PR 触发 abandon —— 防止把 Hao 自己的 PR 干掉。
- **dry-run mode**：环境变量 `PR_MONITOR_DRY_RUN=1` 时，只渲染消息和报告，不发 Teams、不 abandon。**首跑必须 dry-run**，让 Hao 看一次再切真跑。
- 失败重试：单条 PR 操作失败不阻塞其他，但要在报告里列出。
- 时区：年龄按 UTC 算（避免跨时区歧义），呈现给人时换 Beijing 时间。
- "AI PR" 标记的 PR 同样适用规则（很多是自动化产生的，更应该被清理）。

## 输出

每次运行产出 `team/pr-monitor/runs/<YYYY-MM-DD>.md`：
- 总览：fresh/warn/stale 计数
- warn 列表（带 author / 年龄 / 标题 / 链接）
- stale 列表 + 实际执行结果（abandoned ✓ / failed ✗）
- 异常 / 跳过项

跑完简短结果由 cron 的 `delivery: announce` 直接发给 Hao（webchat），失败时 ping 主会话。

## 配置缺口（首跑前要补）

- [ ] Teams Incoming Webhook URL（暂无 → 现在用 mock，跑出文本/卡片样子给 Hao 看）
- [ ] 是否需要 PR 作者 Teams 用户 ID 映射（@ 提及精准送达）？还是按邮箱即可？
- [ ] 阈值是否照搬"5 天 / 30 天"，还是想区分工作日？
