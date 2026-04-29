# PR Reviewer Agent

每小时检查 Messaging-Connectors 仓库所有有新 commit 的 active 非-draft PR，用 LLM 做架构 / 业务规则 / bug 风险 / 测试覆盖 / 重复代码 五项 review。

**这是 L2 级 LLM agent**（每小时 cron 触发，每个 PR 起一个 isolated subagent，跑完即退）。

## 触发

| 触发器 | 时间 | 实现 |
|---|---|---|
| 每小时扫描 | `0 * * * *` UTC | OS crontab → `poll.py` |

## 范围筛选

包含：
- `status=active` 的 PR
- **非 draft**（`isDraft != true`）
- 最近 **3 天** 内有 push（`lastMergeCommit.author.date` 在 72h 内）
- 当前 commit hash **未被 review 过**（state.json 记录）
- 同一 PR 24h 内 review 次数 < 3

跳过：
- diff 超过 **10,000 行**（在报告里标记）
- 只动文档 / yaml / `.gitignore` / `.gitattributes` 的 PR

## Review 5 项

| 代码 | 项目 | 投递 |
|---|---|---|
| **b** | 架构 / 设计：改动是否动了不该动的层；新代码是否放对位置 | DM 给 Hao（personal chat），Hao 审完决定是否手动转贴 |
| **c** | 业务规则：是否违反 `.github/instructions/components/*.md` 里的规则 | inline comment 到 PR（第二阶段） |
| **d** | bug 风险：null 检查 / 异常处理 / 资源泄漏 / 并发问题 | inline comment 到 PR（第二阶段） |
| **e** | 测试覆盖：改了 X，没测 Y | inline comment 到 PR（第二阶段） |
| **f** | 重复代码：PR 内 + 全仓 ripgrep 候选 + LLM 判定 | inline comment 到 PR（第二阶段） |

**第一周阶段**：所有 5 项都 DM 给 Hao 审，**不进 PR**。

## 仓库副本

`~/repos/pr-reviewer/Messaging-Connectors`（独占）。每次 review 流程：
1. `git fetch origin pull/<id>/merge:pr-<id>`
2. `git checkout pr-<id>`
3. 跑 LLM（diff + 全仓 ripgrep 重复检测 + 读 `.github/instructions/`）
4. `git checkout main`（清理）

## LLM

- 模型：Claude Opus 4.x（与主会话一致）
- 调用方式：每个 PR 一个 isolated subagent，单 turn
- 上下文构成：
  - PR diff（patch 格式）
  - 改动的每个 file 当前完整内容（如 < 1500 行）
  - 匹配到的 `.github/instructions/` 文件
  - ripgrep 找出的"重复候选"代码片段（每条 ≤30 行）
  - prompt（见 `prompt.md`）

## 状态

`state.json`：
```json
{
  "<pr_id>": {
    "lastReviewedCommit": "<hash>",
    "reviewsToday": 2,
    "reviewsTodayDate": "YYYY-MM-DD",
    "lastReviewedUtc": "...",
    "lastDmActivityId": "<teams id>"
  }
}
```

## 投递

- **第一周**：所有输出 → DM Hao 的 personal Teams chat（一个 PR 一条聚合 Adaptive Card）
  - conversationId: `a:1ybI-9qx2WMN_JoCouIhiL9Ys44rIEvVCJfEIJPmllqLPgz4oCGKZZT71o0L5Lsr-RCjvf4HpsVL9tiwd6W6KMqORvDnLBXUPFxJDXajCGu15h6w-7Zz4sT54mAQBal5Y`
- **第二周起**（Hao 拍板后）：c/d/e/f → ADO PR inline comment；b + 任何 LLM 标低置信度的 → 仍然 DM Hao

## 红线

- **DRY_RUN 默认开**（`PR_REVIEWER_DRY_RUN=1`）：只产报告，不调 LLM、不发 DM
- **NO_PR_COMMENT 默认开**（第一周强制为 1）：不调 ADO PR comment API
- 失败不阻塞其它 PR；报告里列异常
- 单个 PR review 超时 5 分钟 → 杀掉，记 timeout
- 24h 内同 PR 不超过 3 次 review
- 跳过 diff > 10000 行的 PR
- 同一 commit hash 不重复 review

## 输出

`team/pr-reviewer/runs/<YYYY-MM-DD>/<PR_ID>-<commit-short>.md`：
- PR 元信息
- 5 项 review 的原始 LLM 输出
- 投递结果（activityId / inline thread id）
- 异常 / 跳过项

## 文件

- `AGENT.md` — 本文件
- `prompt.md` — LLM system prompt（**核心**，需 Hao 审）
- `poll.py` — 主调度脚本（每小时 cron）
- `review_one.py` — 对单个 PR 跑 review（被 poll.py 调用）
- `state.json` — 跨 run 状态
- `runs/<date>/...` — 每次 review 的产物
