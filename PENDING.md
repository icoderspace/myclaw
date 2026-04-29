# PENDING.md — 等 Hao 拍板的事

> 我（Claw）自己维护这个文件。任何"我做不下去、需要 Hao 决定"的事都进这里。
> 每天 21:00 BJT cron 唤醒我盘点 → 给 Hao 列清单。
> Hao 拍板后我划掉对应行。
> Format: `- [ ] [yyyy-mm-dd] <事项> — <为什么需要 Hao 决定>`

## 当前未决

- [ ] [2026-04-29] **PR Reviewer v0.2 输出审阅** — 我做完 v0.2 prompt + match_academy + poll.py 后，会拿 3 个 PR 跑对比给 Hao 审，审过才能上线
- [ ] [2026-04-29] **PR Reviewer 何时从 dry-run 切到真发 PR comment** — 第一周 DM 给 Hao，之后视情况切，需要 Hao 拍板"切了"

## 已决 / 已闭环

- [x] [2026-04-29] PR Reviewer 是否 auto-approve Dependabot/[SECURITY] PR → **不**，改"DM + ⚡可 approve 提醒"
- [x] [2026-04-29] PR Reviewer 是否要"docs-only 跳过"规则 → **删除**，TSG 写给 AI 必须 review，加 prompt-doc.md
- [x] [2026-04-29] Academy 文档加载策略 → 路径匹配 + 实时从 main pull
- [x] [2026-04-29] Lingxia 那条 TSG PR 是否需要我起草 comment → 不用，Hao 自己看
- [x] [2026-04-29] PR Monitor 是否上线 → 已上 cron `0 1 * * *` UTC，notify-only 模式
