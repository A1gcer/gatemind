from pathlib import Path
import yaml
from copy import deepcopy


def _read_yaml(file_path: Path) -> dict:
    try:
        return yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _deep_merge(base: dict, override: dict) -> dict:
    """dict 深度合并：override 优先"""
    if not isinstance(base, dict):
        return deepcopy(override)
    result = deepcopy(base)
    for k, v in (override or {}).items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def _load_policy_dir(policy_dir: str) -> list[dict]:
    out = []
    p = Path(policy_dir)
    if not p.exists():
        return out
    for f in sorted(p.glob("*.yaml")):
        data = _read_yaml(f)
        if not data:
            continue
        data["_file"] = str(f)
        out.append(data)
    return out


def load_policies(base_policy_dir: str, private_override_dir: str | None = None) -> list[dict]:
    """
    合并策略：
    1) 先加载公共 base
    2) 再加载 private override（同 id 深度覆盖）
    3) private 中 base 没有的策略直接追加
    """
    base_list = _load_policy_dir(base_policy_dir)
    merged_map: dict[str, dict] = {}

    # 先放 base
    for p in base_list:
        pid = p.get("id")
        if not pid:
            continue
        p["_source"] = "base"
        merged_map[pid] = p

    # 再合并 private
    if private_override_dir:
        private_list = _load_policy_dir(private_override_dir)
        for p in private_list:
            pid = p.get("id")
            if not pid:
                continue

            if pid in merged_map:
                merged = _deep_merge(merged_map[pid], p)
                merged["_source"] = "merged(base+private)"
                merged["_base_file"] = merged_map[pid].get("_file")
                merged["_private_file"] = p.get("_file")
                merged_map[pid] = merged
            else:
                p["_source"] = "private_only"
                merged_map[pid] = p

    # 稳定排序：按 id
    return [merged_map[k] for k in sorted(merged_map.keys())]
