#!/bin/bash
set -e
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$BASE_DIR/scripts/gate_runner.py" --phase pre_commit --from-git --repo-root . --enforce-exit
