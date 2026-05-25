from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from core.runner import run_gates


def test_repo_forbidden_private_policy():
    """GateMind 公共仓禁止私仓策略"""
    ctx = {
        "repo_type": "public",
        "staged_files": ["skills/gatemind/policies/private/my_policy.yaml", "README.md"],
        "file_contents": {}
    }
    out = run_gates(str(BASE), "pre_commit", ctx)
    assert out["decision"]["status"] in ("block", "warn")
    print("✅ test_repo_forbidden_private_policy passed")


def test_repo_forbidden_logs():
    """GateMind 公共仓禁止真实日志"""
    ctx = {
        "repo_type": "public",
        "staged_files": ["skills/gatemind/logs/gate_events.jsonl"],
        "file_contents": {}
    }
    out = run_gates(str(BASE), "pre_commit", ctx)
    assert out["decision"]["status"] in ("block", "warn")
    print("✅ test_repo_forbidden_logs passed")


def test_repo_forbidden_configs():
    """GateMind 公共仓禁止私有配置"""
    ctx = {
        "repo_type": "public",
        "staged_files": ["configs/private_constraints.yaml", "README.md"],
        "file_contents": {}
    }
    out = run_gates(str(BASE), "pre_commit", ctx)
    assert out["decision"]["status"] in ("block", "warn")
    print("✅ test_repo_forbidden_configs passed")


def test_repo_clean():
    """干净提交应放行"""
    ctx = {
        "repo_type": "public",
        "staged_files": ["README.md", "skills/gatemind/core/runner.py", "skills/gatemind/policies/fact.guess.yaml"],
        "file_contents": {}
    }
    out = run_gates(str(BASE), "pre_commit", ctx)
    assert out["decision"]["status"] == "allow"
    print("✅ test_repo_clean passed")


def test_secret_scan():
    """密钥扫描应拦截"""
    ctx = {
        "repo_type": "public",
        "staged_files": ["config/settings.py"],
        "file_contents": {
            "config/settings.py": "API_KEY = 'sk-1234567890abcdef'"
        }
    }
    out = run_gates(str(BASE), "pre_commit", ctx)
    assert out["decision"]["status"] == "block"
    print("✅ test_secret_scan passed")


def test_learnings_forbidden():
    """GateMind 公共仓禁止 .learnings/"""
    ctx = {
        "repo_type": "public",
        "staged_files": [".learnings/delta_log.jsonl"],
        "file_contents": {}
    }
    out = run_gates(str(BASE), "pre_commit", ctx)
    assert out["decision"]["status"] in ("block", "warn")
    print("✅ test_learnings_forbidden passed")


if __name__ == "__main__":
    test_repo_forbidden_private_policy()
    test_repo_forbidden_logs()
    test_repo_forbidden_configs()
    test_repo_clean()
    test_secret_scan()
    test_learnings_forbidden()
    print("\n🎉 All repo gate tests passed!")
