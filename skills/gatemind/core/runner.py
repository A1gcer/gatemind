from pathlib import Path
from .policy_loader import load_policies
from .evaluators import evaluate_policy
from .decision_engine import decide
from .observability import append_event
from .utils import run_cmd


def detect_repo_type(repo_url: str) -> str:
    u = (repo_url or "").lower()
    if "private" in u:
        return "private"
    if "github" in u or "content-hub" in u or "public" in u:
        return "public"
    return "unknown"


def collect_git_context(repo_root: str = ".") -> dict:
    staged_raw = run_cmd(["git", "diff", "--cached", "--name-only"], cwd=repo_root)
    staged_files = [x.strip() for x in staged_raw.splitlines() if x.strip()]
    file_contents = {}
    for f in staged_files[:200]:
        content = run_cmd(["git", "show", f":{f}"], cwd=repo_root)
        file_contents[f] = content[:200000]
    repo_url = run_cmd(["git", "remote", "get-url", "origin"], cwd=repo_root)
    return {
        "staged_files": staged_files,
        "file_contents": file_contents,
        "repo_url": repo_url,
        "repo_type": detect_repo_type(repo_url),
    }


def run_gates(base_dir: str, phase: str, context: dict, private_policy_dir: str | None = None) -> dict:
    base_policy_dir = str(Path(base_dir) / "policies")
    log_file = str(Path(base_dir) / "logs" / "gate_events.jsonl")

    # 核心：加载并合并 public + private
    all_policies = load_policies(base_policy_dir, private_policy_dir)
    policies = [p for p in all_policies if p.get("phase") == phase]

    results = [evaluate_policy(p, context) for p in policies]
    summary = decide(results)

    append_event(log_file, {
        "phase": phase,
        "summary_status": summary["status"],
        "failed_count": summary["failed_count"],
        "policy_count": len(policies),
        "private_policy_dir": private_policy_dir or "",
        "context_keys": sorted(list(context.keys())),
        "violations": [
            {"policy_id": v["policy_id"], "action": v["action"], "reason": v["reason"]}
            for v in summary["violations"]
        ],
    })

    return {
        "phase": phase,
        "policy_count": len(policies),
        "results": results,
        "decision": summary,
    }
