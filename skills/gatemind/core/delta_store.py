import json
from pathlib import Path
from .utils import now_iso_bst


def append_delta(db_file: str, severity: str, gap_type: str, summary: str, detail: str = ""):
    p = Path(db_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "id": f"DLT-{now_iso_bst().replace(':', '').replace('-', '')[:15]}",
        "timestamp": now_iso_bst(),
        "severity": severity,
        "gap_type": gap_type,
        "summary": summary[:200],
        "detail": detail[:500],
        "status": "open",
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry
