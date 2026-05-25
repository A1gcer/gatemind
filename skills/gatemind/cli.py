#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parents[0]))

from skills.gatemind.core.runner import run_gates, collect_git_context
from skills.gatemind.core.utils import read_json_file, dump_json
from skills.gatemind.core.policy_validator import validate_policy_dir
from skills.gatemind.scripts.report_metrics import build_metrics
from skills.gatemind.core.promotion_engine import promote_policies


def cmd_run(args):
    ctx = read_json_file(args.context_file) if args.context_file else {}
    if args.from_git:
        ctx.update(collect_git_context(args.repo_root))
    private_dir = args.private_policy_dir or os.getenv("GATEMIND_PRIVATE_POLICY_DIR", "")
    out = run_gates(
        str(BASE), args.phase, ctx,
        private_policy_dir=private_dir if private_dir else None,
    )
    print(dump_json(out, pretty=True))
    if args.enforce_exit and out["decision"]["status"] == "block":
        return 1
    return 0


def cmd_validate(args):
    ok, report = validate_policy_dir(
        str(BASE / "policies"),
        str(BASE / "schemas" / "policy.schema.json"),
    )
    print(dump_json(report, pretty=True))
    return 0 if ok else 1


def cmd_metrics(args):
    out = build_metrics(str(BASE / "logs" / "gate_events.jsonl"))
    print(dump_json(out, pretty=True))
    return 0


def cmd_promote(args):
    result = promote_policies(
        policy_dir=str(BASE / "policies"),
        log_file=str(BASE / "logs" / "gate_events.jsonl"),
        dry_run=args.dry_run,
    )
    print(dump_json(result, pretty=True))
    return 0


def main():
    ap = argparse.ArgumentParser("gatemind")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run")
    r.add_argument("--phase", required=True, choices=["pre_response", "pre_tool_call", "pre_commit", "post_session_audit"])
    r.add_argument("--context-file", default="")
    r.add_argument("--from-git", action="store_true")
    r.add_argument("--repo-root", default=".")
    r.add_argument("--enforce-exit", action="store_true")
    r.add_argument("--private-policy-dir", default="")
    r.set_defaults(func=cmd_run)

    v = sub.add_parser("validate")
    v.set_defaults(func=cmd_validate)

    m = sub.add_parser("metrics")
    m.set_defaults(func=cmd_metrics)

    p = sub.add_parser("promote")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_promote)

    args = ap.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
