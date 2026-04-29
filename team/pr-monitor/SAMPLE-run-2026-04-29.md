==============================================================================
📨 SAMPLE 1: Teams 通知消息（warn 桶 5–29 天，按作者聚合）
==============================================================================

```
To: #mc-dev-team (or DM each author)
From: PR Monitor 🤖
Date: 2026-04-29 09:00 (Beijing) / 01:00 UTC

Hi team — 你们有 **17 个 PR 滞留 5+ 天** 没合，请尽快推进或主动 abandon。
⚠️ 超过 30 天的 PR 会被自动 abandon（目前已有 4 个待清理）。

**@Nikita Kokitkar** (2 PRs)
  • #2023903  (29d)  [AI][PR] DCF: Happy path tip test for DCF connector
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2023903
  • #2064752  (5d)  [AI][PR]-Mongodb Sanitize password from logs
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2064752

**@zhipeng zhou (Accenture International Limited)** (1 PRs)
  • #2022547  (29d)  [AI PR] Switch Solace and CosmosDB to enhanced connector class names
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2022547

**@Abhineet Garg** (1 PRs)
  • #2034780  (22d)  [AI PR] Redesign branch-aware versioning with clean 3-phase resolve-version.ps1
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2034780

**@Qiang Li (Accenture International Limited)** (1 PRs)
  • #2039843  (20d)  Add DatasourceTestingSdk and test project
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2039843

**@Zhengyi Zhao** (2 PRs)
  • #2040191  (19d)  [AI PR] Remove ContractsV2 folder and move LocalizedErrorNumber to Common
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2040191
  • #2050005  (13d)  [AI PR] feat: add Execute SQL Statement Geneva Action
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2050005

**@Leander Mathisen** (2 PRs)
  • #2048765  (14d)  [AI PR] Migrate SampleData connectors to capacity-capped clusters
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2048765
  • #2060991  (7d)  Add SampleData capacity-capped cluster logic
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2060991

**@Dependabot** (1 PRs)
  • #2054393  (11d)  [SECURITY] Bump System.Security.Cryptography.Xml from 8.0.2 to 8.0.3
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2054393

**@Junfei Wang (Accenture International Limited)** (1 PRs)
  • #2056768  (9d)  [AI PR] Enable managed Prometheus on dedicated (custom-connector) AKS clusters
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2056768

**@Wanyong Song** (2 PRs)
  • #2058963  (8d)  [AI PR] feat: add mTLS and SSL properties to Solace connector codegen config
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2058963
  • #2059664  (7d)  [AI PR] feat: add mTLS support to Solace connector control plane
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2059664

**@Shengzhi Na (Accenture International Limited)** (1 PRs)
  • #2061487  (7d)  Updated tiptest buildout configs for Fairfax env
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2061487

**@Weisa Kong (FESCO Adecco Human Resources)** (1 PRs)
  • #2061450  (7d)  [AI PR] RTI Copilot: MI storage auth + group chat assistant bot-side
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2061450

**@Prathamesh Govekar** (1 PRs)
  • #2059409  (7d)  feat: Add AvroBinary source data format support
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2059409

**@Tangqian Hong** (1 PRs)
  • #2065332  (5d)  Fix Dataverse V2 connector reactor isolation and add diagnostics
     https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2065332

回复 `extend #<id>` 可申请豁免一次（push 30 天 deadline）。
```

==============================================================================
🗑️ SAMPLE 2: 即将对 stale (≥30 天) 执行的 abandon 操作
==============================================================================

PR #2004348  (42d, by Junfei Wang (Accenture International Limited))
  Title: [AI PR] Fix DiagnosticContext propagation for metrics and logging
  URL:   https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2004348
  Action 1 → POST comment:
    "This PR has been inactive for 42 days. Closing automatically per the
     stale-PR policy. Please reopen or recreate if you still want to land it."
  Action 2 → PATCH /pullRequests/2004348  body: {"status":"abandoned"}

PR #2010735  (38d, by Abhineet Garg)
  Title: [AI PR] Fix nightly TipTests build: disable SdkAnalyzers
  URL:   https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2010735
  Action 1 → POST comment:
    "This PR has been inactive for 38 days. Closing automatically per the
     stale-PR policy. Please reopen or recreate if you still want to land it."
  Action 2 → PATCH /pullRequests/2010735  body: {"status":"abandoned"}

PR #2019259  (33d, by Nikita Kokitkar)
  Title: DCF: Upgrade Delta library
  URL:   https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2019259
  Action 1 → POST comment:
    "This PR has been inactive for 33 days. Closing automatically per the
     stale-PR policy. Please reopen or recreate if you still want to land it."
  Action 2 → PATCH /pullRequests/2019259  body: {"status":"abandoned"}

PR #2018529  (33d, by Nikita Kokitkar)
  Title: [AI PR] Add dotnet sidecar cluster type with Docker image and control plane support
  URL:   https://dev.azure.com/msdata/Messaging%20Connectors%20and%20Event%20Streams/_git/Messaging-Connectors/pullrequest/2018529
  Action 1 → POST comment:
    "This PR has been inactive for 33 days. Closing automatically per the
     stale-PR policy. Please reopen or recreate if you still want to land it."
  Action 2 → PATCH /pullRequests/2018529  body: {"status":"abandoned"}

==============================================================================
📋 SAMPLE 3: 跑完后写到 team/pr-monitor/runs/2026-04-29.md 的内容
==============================================================================

# PR Monitor — 2026-04-29

**Run mode**: 🟡 dry-run (no Teams sent, no PRs abandoned)
**Repo**: msdata/Messaging Connectors and Event Streams/Messaging-Connectors
**Active PRs**: 32

| 桶 | 范围 | 数量 | 动作 |
|---|---|---|---|
| Fresh | 0–4d | 11 | 不动 |
| Warn | 5–29d | 17 | 拟发 Teams 通知 |
| Stale | ≥30d | 4 | 拟 abandon |

## Stale (would abandon)

| # | Age | Author | Title |
|---|---|---|---|
| #2004348 | 42d | Junfei Wang (Accenture International Limited) | [AI PR] Fix DiagnosticContext propagation for metrics and lo |
| #2010735 | 38d | Abhineet Garg | [AI PR] Fix nightly TipTests build: disable SdkAnalyzers |
| #2019259 | 33d | Nikita Kokitkar | DCF: Upgrade Delta library |
| #2018529 | 33d | Nikita Kokitkar | [AI PR] Add dotnet sidecar cluster type with Docker image an |

## Warn (would notify, top 10)

| # | Age | Author | Title |
|---|---|---|---|
| #2023903 | 29d | Nikita Kokitkar | [AI][PR] DCF: Happy path tip test for DCF connector |
| #2022547 | 29d | zhipeng zhou (Accenture International Limited) | [AI PR] Switch Solace and CosmosDB to enhanced connector cla |
| #2034780 | 22d | Abhineet Garg | [AI PR] Redesign branch-aware versioning with clean 3-phase  |
| #2039843 | 20d | Qiang Li (Accenture International Limited) | Add DatasourceTestingSdk and test project |
| #2040191 | 19d | Zhengyi Zhao | [AI PR] Remove ContractsV2 folder and move LocalizedErrorNum |
| #2048765 | 14d | Leander Mathisen | [AI PR] Migrate SampleData connectors to capacity-capped clu |
| #2050005 | 13d | Zhengyi Zhao | [AI PR] feat: add Execute SQL Statement Geneva Action |
| #2054393 | 11d | Dependabot | [SECURITY] Bump System.Security.Cryptography.Xml from 8.0.2  |
| #2056768 | 9d | Junfei Wang (Accenture International Limited) | [AI PR] Enable managed Prometheus on dedicated (custom-conne |
| #2058963 | 8d | Wanyong Song | [AI PR] feat: add mTLS and SSL properties to Solace connecto |
