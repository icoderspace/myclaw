# PROJECT.md — Messaging-Connectors 项目章程

> 这是从 `Messaging-Connectors/.github/copilot-instructions.md` 提炼出来的**项目宪法**。
> Claw 派 PM/Coder/Tester/Reviewer 子会话时，必须把这份文件作为上下文一并注入。
> 仓库本地路径：`~/repos/Messaging-Connectors`

## 一、这是什么项目

**Azure Messaging Connectors**（也叫 Azure Event Streams / Kafka Connect as a Service）的统一 monorepo，由 16 个旧仓库合并而成。

- **业务**：托管的 Kafka Connect connectors（source / sink），把 Azure Event Hubs 和外部系统（数据库、存储、消息队列）打通。
- **服务形态**：客户在 Azure 上点几下，就拿到一个跑着的 connector。

## 二、代码结构（最高层）

```
src/control/        Control Plane (RP) — C#/.NET 8, Service Fabric
src/runtime/plugin/ Runtime Plugin     — Java 17, Gradle, Kafka Connect
src/contracts/      ARM contracts (codegen / arm-sdk / arm-config)
src/monitoring/     Geneva 配置
externals/          Apache Kafka / Camel / camel-kafka-connector / kamelets 的 vendor fork
deploy/             EV2 部署（24 个 service group）
tests/              TipTests（E2E，Test-In-Production）
tools/icm/          IcM 工单工具
tools/release-manager-v2/
tools/rti-copilot/  Teams Bot（给 on-call 工程师用，AI 主导）
tsg/                TSG 文档 + Copilot agents
```

## 三、技术栈速查

| 组件 | 语言 | 构建 | 框架 |
|---|---|---|---|
| Control Plane | C# / .NET 8 | dotnet | Service Fabric |
| Runtime Plugin | Java 17 | Gradle 8.5 | Kafka Connect |
| External Forks | Java 17 | Maven / Gradle | Apache Camel / Kafka |
| Docker Image | — | docker | Strimzi base |
| TipTests | C# / .NET 8 | dotnet | MSTest / Geneva Synthetics |
| Deployments | PowerShell / JSON | EV2 | ARM |

## 四、构建入口

```powershell
.\init.ps1                              # 一次性环境检查
.\build.ps1                             # java + dotnet（默认）
.\build.ps1 -Component dotnet           # 只 .NET，~5 min
.\build.ps1 -Component java             # Java 全链路，~25 min
.\build.ps1 -Component image            # Docker 运行时镜像
.\build.ps1 -Component all-with-image   # 全套
```

构建依赖链：
```
externals/camel → camel-kamelets → camel-kafka-connector
externals/kafka → src/runtime/plugin → Docker image
src/contracts/codegen → src/control → tests
```

## 五、🚨 全局硬性规则（所有角色必读）

### 1. PR 流程
- **本地先看，再 PR**：所有改动先在本地给 Hao 看 diff，**用户明确说 "create PR" 才能建分支 / push / 开 PR**。绝不能擅自 push。
- **Push 前 rebase**：`git fetch origin main && git rebase origin/main`，本地解冲突。

### 2. Push 前静态检查（强制）
- **Java 改动**：每个改动模块都要跑
  ```bash
  ./gradlew :<module>:checkstyleMain :<module>:checkstyleTest \
            :<module>:spotbugsMain :<module>:spotbugsTest \
            :<module>:sonarlintMain :<module>:sonarlintTest
  ```
  Checkstyle / SpotBugs 必须 0 violation 才能 push。
- **C# 改动**：必须跑
  ```bash
  dotnet test src/control/KafkaConnectService/Test/Commons/CodeStyleTest/CodeStyleTest.csproj
  ```
  确保 `MetadataValidationTest` 通过 —— 所有 controller 类要有 `[ClassMetadata]`，所有 public controller 方法要有 `[MethodMetadata]`。

### 3. Kusto 查询规则（强制）
- 任何针对 MC 日志表（TraceLog / ExternalConnectApp / Runtime / KubernetesContainers / UserActivityLogs）的 Kusto 查询，**必须先读** `docs/Troubleshooting/Kusto-Log-Query-Guide.md` 拿正确的列名。
- 不许凭记忆猜列名（每张表命名都不一样：`message` 不是 `EventMessage`，`Level` 是 long 不是 string，等等）。
- 查询失败因为列名错了 → **必须立刻更新文档**。
- 已知例外：`IcmDataWarehouse.Incidents` 列名是 `CreateDate`（不是 `CreatedDate`）。

## 六、编码规范

### .NET
- target `net8.0`
- 中央包管理：`Directory.Packages.props`
- 强名签名：`src/control/.build/Local/StrongNamePrivateKeys/testkey.snk`
- StyleCop 强制；Control Plane 和 CodeGenerator 是 `-warnAsError`

### Java
- JDK 17 (Microsoft OpenJDK)
- Gradle 8.5（RT-Plugin、Kafka）；Maven（Camel forks）
- Checkstyle、SpotBugs、SonarLint 已配（CI 里 build 阶段不跑，提速用，但 push 前必须本地跑）
- Forks 用 `mavenLocal()` 解项目间依赖

### EV2
- 24 个 service group
- `deploy/ev2/Build.ps1` 打包（merge templates + 打版本号）
- `RolloutSpec.json` 定义滚动步骤
- 区域配置在 `deploy/Shared/GlobalConfigs/`

## 七、子项目特殊规则

### `tools/rti-copilot/**` 有自己的硬规则
- 框架：**Microsoft 365 Agents SDK**（不许偏离）
- 分层：Agent / Services / Models / Program.cs
- 依赖：NuGet，核心包 `Microsoft.Agents.Authentication.Msal`、`Microsoft.Agents.Hosting.AspNetCore`
- 引入新第三方依赖必须先讲清楚理由
- Commit 必须 Conventional Commits（`feat:` / `fix:` / `docs:` / ...），消息英文
- 每个 commit 必须带：`Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`
- 大功能要先写 plan、用户批准了才能动手
- 任务做完要更新 `tools/rti-copilot/docs/roadmap.md` 并 commit

### Component-level 指令（按需读）
派活时如果涉及以下组件，对应 PERSONA 要去读 `.github/instructions/components/` 下对应文件：
- `rp.instructions.md` — Control Plane
- `runtime-plugin.instructions.md`
- `tiptests/` — E2E 测试
- `runtime-exception/` — 运行时异常自动化
- `release-manager-v2/`
- `monitors/` — 告警规则
- `contracts/{arm-config, arm-sdk}/`
- `ev2/`

### Workflow-level 指令（命令触发）
项目内嵌了一批"命令"，触发时**必须读对应 workflow 文件按步骤执行**：

| 命令 | 文件 |
|---|---|
| Analyze Weekly Incidents | `workflows/dri-weekly-incident-analysis.instructions.md` |
| Run RT Exception Analysis（`run rt exception analysis`） | `workflows/runtime-exception-execute-all.instructions.md` |
| Regenerate RT Exception Report | `workflows/runtime-exception-regenerate-report.instructions.md` |
| Generate Release Commits（`生成 release commits`） | `workflows/generate-release-prs.instructions.md` |
| Pipeline Test Timeline（`分析 pipeline 时间线`） | `workflows/pipeline-test-timeline.instructions.md` |
| Create Connector ADO List（`创建 XX connector 的 ADO list`） | `references/new-connector-pbi-template.instructions.md` |
| Create Repair Item: {description} | `references/create-repair-item.instructions.md` |

## 八、专用 AI Agent（项目自带的）

`.github/agents/` 下：
- `add-new-connector.agent.md`
- `connector-bug-triage.agent.md`
- `mc-icm-copilot.md` — DRI 助手 `@mc-icm-copilot`
- `runtime-exception-copilot.agent.md`
- `rti-copilot/` 子目录

> 这些跟我们的 PM/Coder/Tester/Reviewer 是不同维度：
> - **他们的 agents** 是按业务场景分（onboard 新 connector、bug 分诊、IcM 处理）
> - **我们的角色** 是按职能分（产品 / 实现 / 测试 / 审查）
> 派活时如果场景对得上，让对应角色读相应的 agent.md 当参考。

## 九、常见任务速查

### 加新 connector
1. 在 `src/runtime/plugin/connector/` 加模块
2. 改 `settings.gradle` + `build.gradle` 的 copy task
3. 用 `src/contracts/codegen/` 生 ARM contract
4. 在 `tests/` 加 TipTests

### Debug 部署
1. 看 `deploy/<ServiceGroup>/RolloutSpec.json`
2. 看 `deploy/<ServiceGroup>/Parameters/`
3. 看 `deploy/Shared/GlobalConfigs/GlobalConfig.*.json`
4. 参考 `tsg/docs/Engineering/Deployment/RP-deployment-process.md`

### OneBox（本地开发）
1. `.\init.ps1`
2. 跟 `src/control/OneBoxEnvironmentScript/`
3. 看 `tsg/docs/Engineering/Academy/Connector-Integration/OneboxSetup.md`

## 十、给团队角色的执行映射

| 角色 | 必看 | 何时下钻 components/ workflows/ |
|---|---|---|
| **PM** | 全文 + § 五 + § 七 workflow 表 | 接到任务时 |
| **Coder** | 全文 + § 五 + § 六 + § 七（如果改 rti-copilot） | 改哪个组件就读对应 components/ |
| **Tester** | 全文 + § 五 + tiptests 部分 | 写测试前读 `components/tiptests/` |
| **Reviewer** | 全文 + § 五（push 前检查） + § 六 | 审改动涉及的所有 components/ 文档 |

---

**最后更新**：2026-04-29，by Claw
**源文件**：`Messaging-Connectors/.github/copilot-instructions.md`（318 行）
