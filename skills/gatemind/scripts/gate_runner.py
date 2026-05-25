#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from core.runner import run_gates, collect_git_context
from core.utils import read_json_file, dump_json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True,
                    choices=["pre_response", "pre_tool_call", "pre_commit", "post_session_audit"])
    ap.add_argument("--context-file", default="")
    ap.add_argument("--from-git", action="store_true")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--enforce-exit", action="store_true")
    ap.add_argument("--private-policy-dir", default="")  # 新增
    args = ap.parse_args()

    ctx = read_json_file(args.context_file)
    if args.from_git:
        ctx.update(collect_git_context(args.repo_root))

    private_dir = args.private_policy_dir or os.getenv("GATEMIND_PRIVATE_POLICY_DIR", "")

    out = run_gates(
        str(BASE), args.phase, ctx,
        private_policy_dir=private_dir if private_dir else None,
    )
    print(dump_json(out, pretty=True))

    if args.enforce_exit and out["decision"]["status"] == "block":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
