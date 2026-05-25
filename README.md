# GateMind

GateMind is an AI Agent runtime guardrails framework.

## Features
- Policy registry (YAML + schema validation)
- Multi-phase gates: pre_response / pre_tool_call / pre_commit
- Decision engine: allow/warn/require_evidence/require_user_confirm/block
- Lifecycle: candidate/shadow/active/deprecated
- Observability logs + promotion engine

## Quick Start

```bash
pip install -e .
gatemind validate
gatemind run --phase pre_response --context-file ctx.json
```

## Repo Model
- Public repo: framework + generic policies
- Private repo: org-specific policies/logs/secrets patterns
