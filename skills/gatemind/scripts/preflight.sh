#!/bin/bash
set -e
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

CTX_FILE="${1:-}"
if [ -z "$CTX_FILE" ]; then
  echo '{"user_input":"","draft_response":"","intent_confirmed":false}' > /tmp/gatemind_pre_response_ctx.json
  CTX_FILE="/tmp/gatemind_pre_response_ctx.json"
fi

python3 "$BASE_DIR/scripts/gate_runner.py" --phase pre_response --context-file "$CTX_FILE"
