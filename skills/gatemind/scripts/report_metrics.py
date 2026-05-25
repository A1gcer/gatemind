#!/usr/bin/env python3
import json
from pathlib import Path


def build_metrics(log_file: str) -> dict:
    p = Path(log_file)
    if not p.exists():
        return {"total_events": 0}

    lines = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
    total = len(lines)
    by_status = {}
    by_policy = {}

    for e in lines:
        st = e.get("summary_status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        for v in e.get("violations", []):
            pid = v.get("policy_id", "unknown")
            by_policy[pid] = by_policy.get(pid, 0) + 1

    return {
        "total_events": total,
        "status_distribution": by_status,
        "top_violations": sorted(by_policy.items(), key=lambda x: x[1], reverse=True)[:20],
    }


if __name__ == "__main__":
    out = build_metrics("skills/gatemind/logs/gate_events.jsonl")
    print(json.dumps(out, ensure_ascii=False, indent=2))
