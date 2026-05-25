import json
from pathlib import Path
import yaml


def _load_logs(log_file: str) -> list[dict]:
    p = Path(log_file)
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def _policy_hits(logs: list[dict]) -> dict:
    hits = {}
    for e in logs:
        for v in e.get("violations", []):
            pid = v.get("policy_id")
            if pid:
                hits[pid] = hits.get(pid, 0) + 1
    return hits


def promote_policies(policy_dir: str, log_file: str, dry_run: bool = True) -> dict:
    logs = _load_logs(log_file)
    hits = _policy_hits(logs)

    changed = []
    for f in sorted(Path(policy_dir).glob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        pid = data.get("id")
        lc = (data.get("lifecycle") or {}).get("status", "active")
        h = hits.get(pid, 0)

        target = lc
        if lc == "candidate" and h >= 5:
            target = "shadow"
        elif lc == "shadow" and h >= 20:
            target = "active"

        if target != lc:
            changed.append({"file": f.name, "id": pid, "from": lc, "to": target, "hits": h})
            if not dry_run:
                data.setdefault("lifecycle", {})["status"] = target
                f.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    return {"dry_run": dry_run, "changes": changed, "log_events": len(logs)}
