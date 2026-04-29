# ADO PAT 元数据（**不**包含 token 本体）

- **存放位置**: `~/.openclaw/secrets/ado-pat`（VM 外部，不在 workspace 里，不会被 git push）
- **权限**: 700/600
- **创建日期**: 2026-04-29
- **过期日期**: **2026-05-06**（7 天有效期）
- **org**: msdata
- **scope**: 至少能 read/clone 私有 repo（已验证）

## 使用方式

```bash
PAT=$(cat ~/.openclaw/secrets/ado-pat)

# REST API
curl -u ":$PAT" "https://dev.azure.com/msdata/_apis/..."

# Git clone / push（用 extraHeader，避免 PAT 落到 .git/config）
git -c http.extraHeader="Authorization: Basic $(printf ":$PAT" | base64 -w0)" \
    clone "https://dev.azure.com/msdata/<project>/_git/<repo>"
```

## 轮换流程

PAT 即将到期前 Hao 会发新 PAT。轮换：
```bash
echo "<NEW_PAT>" > ~/.openclaw/secrets/ado-pat
chmod 600 ~/.openclaw/secrets/ado-pat
# 旧 PAT 在 ADO 那边由 Hao revoke
```

## 红线

- **绝不**把 PAT 写到 workspace 里任何文件（包括 memory/、commit log、PR description）
- **绝不**把 PAT 通过 web_fetch / 第三方 API 发出去
- 跨会话调用工具时，从文件现读，不在 message 里 echo
