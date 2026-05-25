import json
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

BST = timezone(timedelta(hours=8))

PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5}
ACTION_RANK = {"allow": 0, "warn": 1, "require_evidence": 2, "require_user_confirm": 3, "block": 4}


def now_iso_bst() -> str:
    return datetime.now(BST).isoformat()


def run_cmd(cmd: list[str], cwd: str | None = None, check: bool = False) -> str:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)
        return (p.stdout or "").strip()
    except Exception:
        return ""


def read_json_file(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def dump_json(data: dict, pretty: bool = True) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2 if pretty else None)
