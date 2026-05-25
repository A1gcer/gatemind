from pathlib import Path
import yaml
import json
from jsonschema import Draft202012Validator


def _load_schema(schema_path: str) -> dict:
    return json.loads(Path(schema_path).read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def validate_policy_file(path: str, schema: dict) -> list[str]:
    p = Path(path)
    try:
        data = _load_yaml(p)
    except Exception as e:
        return [f"{p.name}: YAML parse error: {e}"]

    v = Draft202012Validator(schema)
    errs = []
    for e in sorted(v.iter_errors(data), key=lambda x: x.path):
        loc = ".".join(map(str, e.absolute_path)) or ""
        errs.append(f"{p.name}: {loc} -> {e.message}")
    return errs


def validate_policy_dir(policy_dir: str, schema_path: str) -> tuple[bool, dict]:
    schema = _load_schema(schema_path)
    root = Path(policy_dir)
    files = sorted(root.glob("*.yaml"))
    all_errs = {}
    for f in files:
        errs = validate_policy_file(str(f), schema)
        if errs:
            all_errs[f.name] = errs

    report = {
        "policy_dir": str(root),
        "total_files": len(files),
        "valid_files": len(files) - len(all_errs),
        "invalid_files": len(all_errs),
        "errors": all_errs,
    }
    return len(all_errs) == 0, report
