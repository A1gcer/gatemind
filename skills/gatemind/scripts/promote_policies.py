#!/usr/bin/env python3
import argparse
import json
from skills.gatemind.core.promotion_engine import promote_policies


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    result = promote_policies(
        policy_dir="skills/gatemind/policies",
        log_file="skills/gatemind/logs/gate_events.jsonl",
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
