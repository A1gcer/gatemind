---
name: gatemind
description: "GateMind 门心系统：AI Agent 的自进化质量与安全门框架"
version: 2.0.0
author: "A1gcer × 小AI"
tags: [gatemind, guardrails, quality-gates, safety, agentops, gitops]
---

# GateMind（门心系统）

GateMind 是一个面向 AI Agent 的自进化质量与安全门系统，
通过策略门、审计日志和复发学习，让 AI 在回答、工具调用和代码提交前完成可执行检查。

---

## 核心链路

错误记录 → 复发识别 → 候选门生成 → 影子运行 → 转正 → 执行拦截 → 可观测复盘

## 执行阶段（phase）

- `pre_response` — 回答前（推测依据/时间时区/长文档意图/方案过滤）
- `pre_tool_call` — 工具调用前（高风险操作/用户约束/Patch Scope）
- `pre_commit` — Git 提交前（公共仓红线/密钥扫描）
- `post_session_audit` — 会话审计（复发检测/Delta 记录）

## 决策动作（action）

- `allow` — 放行
- `warn` — 警告但放行
- `require_evidence` — 需要补充依据
- `require_user_confirm` — 需要用户确认
- `block` — 硬拦截（exit 1）

## 生命周期（lifecycle）

- `candidate` — 候选（只记录不拦截）
- `shadow` — 影子（观察，block 降级为 warn）
- `active` — 活跃（完整执行 on_fail 动作）
- `deprecated` — 废弃（跳过检查）

---

## 双仓库架构

GateMind 本身采用 Open Core 双仓模式：

| 仓库 | 可见性 | 定位 |
|------|--------|------|
| `A1gcer/gatemind` | 🔓 Public | 框架能力 + 通用策略 + 脱敏示例 |
| `A1gcer/gatemind-private-ops` | 🔒 Private | 真实规则 + 日志数据 + 组织上下文 |

### 内容隔离红线

#### 公共仓（gatemind）—— 禁止提交

| 红线 | 内容 | 拦截策略 |
|------|------|----------|
| ❌ `policies/private/` | 私仓策略文件 | `repo.public_safety.yaml` → block |
| ❌ `logs/*.jsonl` | 真实 Gate 事件日志 | `.gitignore` + `repo.public_safety.yaml` |
| ❌ `configs/` | 私有配置（约束/域名/路径） | `repo.public_safety.yaml` |
| ❌ `server-hooks/pre-receive`（无 .sample） | 真实服务端 hook | `repo.public_safety.yaml` |
| ❌ `.learnings/` | Delta 数据 | `repo.public_safety.yaml` |
| ❌ `.env` / 密钥文件 | 任何环境变量/凭据 | `repo.secret_exposure.yaml` + .gitignore |
| ❌ 内网域名/内部路径 | 组织基础设施信息 | `repo.secret_exposure_private.yaml`（私仓） |

#### 私仓（gatemind-private-ops）—— 可放但不推荐
- `policies/private/` — 组织级策略覆盖
- `logs/gate_events.jsonl` — 真实运行日志
- `.learnings/delta_log.jsonl` — Delta 记录
- `configs/private_constraints.yaml` — 私有约束
- `server-hooks/pre-receive` — 真实服务端 hook

### 提交前自检清单

往哪个仓库提交前，过五问：

```
① 这个文件可以公开被人看到吗？
② 它包含私仓策略、日志数据、组织信息吗？
③ 它包含 .env / token / secret 等凭证吗？
④ 是通用能力还是真实运行数据？
⑤ 它的 canonical 主源在哪里？

→ 五个 ✅ → 公共仓
→ 任一 ❌ → 私仓
```

### GateMind 自身如何执行的

```bash
# 公共仓提交前（自动触发 pre-commit hook）
gatemind run --phase pre_commit --from-git --enforce-exit

# 私仓提交前（公共 + 私有策略合并）
gatemind run --phase pre_commit --from-git --enforce-exit \
  --private-policy-dir /path/to/gatemind-private-ops/policies/private

# 或通过环境变量
export GATEMIND_PRIVATE_POLICY_DIR=/path/to/gatemind-private-ops/policies/private
gatemind run --phase pre_commit --from-git --enforce-exit
```

### GitOps 物理门安装

```bash
# 安装到公共仓
cd /path/to/gatemind
bash skills/gatemind/scripts/install_git_hooks.sh
```

预置的 `pre-commit` hook 会自动调用 `gatemind run --phase pre_commit`，
通过 `repo.public_safety.yaml` 和 `repo.secret_exposure.yaml` 拦截违规提交。

---

## CLI 命令

```bash
gatemind run       --phase <phase>          # 执行门检查
gatemind validate                            # 校验所有 YAML policy 合法性
gatemind metrics                             # 查看门拦截统计
gatemind promote  [--dry-run]               # 策略晋升（candidate→shadow→active）
```

---

## 从旧安全门迁移

本系统是 `skills/self-evolution-engine/`（旧安全门体系）的 v2 升级版。
旧系统的散装 shell 脚本和硬编码逻辑已重构为：
- YAML Policy 驱动（9 个预置策略）
- 模块化 Python 核心（10 个模块）
- phase/action/lifecycle 三层抽象
- 双仓架构 + 公私策略合并加载
- 可观测日志 + 晋升引擎
- GitHub Actions CI + GitOps Gate + Secret Scan
