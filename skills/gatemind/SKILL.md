---
name: gatemind
description: "GateMind 门心系统：AI Agent 的自进化质量与安全门框架"
version: 2.0.0
author: "A1gcer × 小AI"
tags: [gatemind, guardrails, quality-gates, safety, agentops]
---

# GateMind（门心系统）

GateMind 是一个面向 AI Agent 的自进化质量与安全门系统，
通过策略门、审计日志和复发学习，让 AI 在回答、工具调用和代码提交前完成可执行检查。

## 核心链路

错误记录 -> 复发识别 -> 候选门生成 -> 影子运行 -> 转正 -> 执行拦截 -> 可观测复盘

## 执行阶段（phase）

- pre_response
- pre_tool_call
- pre_commit
- post_session_audit

## 决策动作（action）

- allow
- warn
- require_evidence
- require_user_confirm
- block

## 生命周期（lifecycle）

- candidate
- shadow
- active
- deprecated

## 从旧安全门迁移

本系统是 `skills/self-evolution-engine/`（旧安全门体系）的 v2 升级版。
旧系统的散装 shell 脚本和硬编码逻辑已重构为：
- YAML Policy 驱动
- 模块化 Python 核心
- phase/action/lifecycle 三层抽象
