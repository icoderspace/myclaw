# Team Workflow

Claw 是唯一对外接口。下面是一个标准任务从 Hao 进来到结果出去的流程。

## 0. 入口：Hao 派活

Hao 直接告诉 Claw 一件事，可能模糊（"加个限流功能"），可能清晰（链接到 ADO Bug #12345）。

Claw 先**判断粒度**：
- 太大？拆成多个独立任务，逐个走流程。
- 不清楚？先问 Hao 关键澄清，不进流程。
- 合适？进入第 1 步。

## 1. PM 阶段

Claw `sessions_spawn` 一个 isolated 子会话，注入 `pm/PERSONA.md` + 任务描述。

**PM 输出**（结构化 markdown）：
- **目标**：用户视角一句话
- **验收标准**：列表，可测
- **范围内 / 范围外**：明确边界
- **ADO 链接**：如果新建/更新了 work item
- **建议拆分**：是否要拆成更小的 task

PM 的产物存到 `team/runs/<run-id>/spec.md`，其它角色只读这个文件，不直接看 Hao 原话（避免传话失真，也避免私聊污染）。

## 2. Coder 与 Tester 并行

Claw 同时 spawn 两个 isolated 子会话：

**Coder**：
- 输入：`team/runs/<run-id>/spec.md` + 代码仓库路径
- 输出：代码改动 + 简短的 commit message + `team/runs/<run-id>/code-summary.md`
- **不**写测试套件（只写最小自测帮自己确认，跑完即弃）
- **不**读 Tester 的输出

**Tester**：
- 输入：`team/runs/<run-id>/spec.md`（**不**给代码路径）
- 输出：测试用例 + `team/runs/<run-id>/tests-summary.md`
- 测试用例围绕 spec 的验收标准写
- **不**读 Coder 的代码

> 实现层面：两个会话用不同的 `sessions_spawn` 调用，`context: "isolated"`，子会话彼此不可见。

## 3. Reviewer 阶段

Coder + Tester 都完工后，Claw spawn 一个 isolated 子会话，注入 `reviewer/PERSONA.md`。

**Reviewer 输入**：
- spec.md
- Coder 的代码改动
- Tester 的测试用例
- 仓库（只读）

**Reviewer 动作**：
- 把 Tester 的测试跑在 Coder 的代码上
- 审实现是否对得上 spec
- 审测试是否覆盖验收标准
- 找出 Coder/Tester 之间的不一致

**Reviewer 输出** → `team/runs/<run-id>/review.md`：
- ✅ 通过 / ⚠️ 需要修 / ❌ 重做
- 具体问题清单
- 推荐的下一步（合并 / Coder 改 / Tester 改 / 重新对齐 spec）

## 4. Claw 汇总

Claw 读完 review 报告，向 Hao 汇报：
- 一句话结论
- 关键产出位置（PR / commit / ADO link）
- 如果 Reviewer 说要改，Claw 决定：自动启第二轮 vs 问 Hao

## 目录结构

```
team/runs/
  2026-04-29-add-rate-limit/
    spec.md            # PM 产出
    code-summary.md    # Coder 自述
    tests-summary.md   # Tester 自述
    review.md          # Reviewer 结论
    timeline.md        # Claw 记录每一步开始/结束时间
```

Run 目录用 `YYYY-MM-DD-<slug>` 命名。完成后保留作为案底。

## 失败重试策略

- PM 阶段卡住（需求不清）→ 立刻 escalate 到 Hao，不进入第 2 步。
- Coder 失败（实现不出来）→ 退回 PM 重新审视 spec，最多 1 次自动重试。
- Tester 失败（无法定义可测条件）→ 视为 spec 不可测，退回 PM。
- Reviewer 判 ❌ 重做 → 自动启动第二轮，最多 2 轮，超出后 escalate。
