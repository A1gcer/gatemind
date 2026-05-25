import json
from pathlib import Path

CORRECTION_SIGNALS = [
    "不对", "错了", "你理解错了", "你又", "不是这个意思", "请先确认意图"
]


def scan_sessions(session_dir: str, max_files: int = 30) -> list[dict]:
    p = Path(session_dir)
    if not p.exists():
        return []
    out = []
    for f in sorted(p.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True)[:max_files]:
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                obj = json.loads(line)
                if obj.get("type") != "message":
                    continue
                msg = obj.get("message", {})
                if msg.get("role") != "user":
                    continue
                content = msg.get("content", "")
                if any(s in str(content) for s in CORRECTION_SIGNALS):
                    out.append({"file": f.name, "content": str(content)[:300]})
            except Exception:
                continue
    return out
