from pathlib import Path
from .utils import now_iso_bst


TEMPLATE = """id: {id}
name: {name}
category: fact
phase: pre_response
priority: P2
severity: medium
lifecycle:
 status: candidate
decision:
 on_fail: require_evidence
message: "自动生成候选门，请先 shadow 观察后再转 active"
check:
 kind: guess_without_evidence
 args:
   guess_words: ["可能", "大概", "应该", "我猜", "maybe", "probably"]
   evidence_words: ["根据", "证据", "日志", "来源", "数据"]
meta:
 generated_at: "{ts}"
 generated_by: "auto_gate"
 source_delta_ids: {delta_ids}
"""


def create_candidate_policy(policy_dir: str, slug: str, delta_ids: list[str]):
    p = Path(policy_dir)
    p.mkdir(parents=True, exist_ok=True)
    file_path = p / f"auto.{slug}.yaml"
    content = TEMPLATE.format(
        id=f"gate.auto.{slug}",
        name=f"自动候选门-{slug}",
        ts=now_iso_bst(),
        delta_ids=str(delta_ids),
    )
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)
