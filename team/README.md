# Team — 开发组

Hao 的开发团队，由 Claw（team lead）统一调度。Hao 不直接对接成员，所有沟通经过 Claw。

## 编制

| 角色 | 文件 | 一句话职责 |
|---|---|---|
| **PM** | [pm/PERSONA.md](pm/PERSONA.md) | 澄清需求、管理 ADO work items、把 spec 拆给 Coder/Tester |
| **Coder** | [coder/PERSONA.md](coder/PERSONA.md) | 按 spec 写实现代码 + 自测 |
| **Tester** | [tester/PERSONA.md](tester/PERSONA.md) | 按 spec 独立写测试用例，**不看 Coder 代码** |
| **Reviewer** | [reviewer/PERSONA.md](reviewer/PERSONA.md) | 审 Coder 代码、跑 Tester 测试、给 review 报告 |

## 工作流

详见 [WORKFLOW.md](WORKFLOW.md)。

```
Hao → Claw → PM → ┬─ Coder  ─┐
                  └─ Tester ─┴─ Reviewer → Claw → Hao
```

## 实现机制

每个角色是一份 `PERSONA.md`，**不是常驻进程**。Claw 在派活时用 `sessions_spawn` 拉起一个隔离子会话，把对应 PERSONA 内容注入 task。这保证：

- Coder 与 Tester 真正独立（不同的 session，互不可见）
- 每次新任务从干净状态开始
- 不占用闲置时的资源/token

## 共享资源

- ADO org：`msdata`
- Project：`Messaging Connectors and Event Streams`
- 认证：vm-openclaw 上挂的 UMI `mc-umi-rm` (client_id `85d09484-3dce-4133-bb11-d3ffa18ed50d`)
- 团队成员调用 ADO 都走 IMDS → UMI token，不需要 PAT

## 红线

- **只有 PM 写 ADO work items**；其他角色只读 ADO。
- **Coder 不写测试套件**（避免马克思自审）。
- **Tester 不读 Coder 代码**（避免 test 反向适配实现）。
- **Reviewer 不动代码**，只产出 review 报告。
- 所有跨成员的协调由 Claw 收口，成员之间不直接通话。
