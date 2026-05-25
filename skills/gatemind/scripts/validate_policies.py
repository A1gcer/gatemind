#!/usr/bin/env python3
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE.parents[0]))

from skills.gatemind.core.policy_validator import validate_policy_dir


def main():
    ok, report = validate_policy_dir(
        policy_dir=str(BASE / "policies"),
        schema_path=str(BASE / "schemas" / "policy.schema.json"),
    )
    import json
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
