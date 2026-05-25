import json
from pathlib import Path
from .utils import now_iso_bst


def append_event(log_file: str, payload: dict):
    p = Path(log_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(payload)
    payload["timestamp"] = now_iso_bst()
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
