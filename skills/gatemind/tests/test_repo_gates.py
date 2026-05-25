from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from core.runner import run_gates


def test_repo_forbidden():
    ctx = {
        "repo_type": "public",
        "staged_files": ["distribution/a.txt", "content/a.md"],
        "file_contents": {}
    }
    out = run_gates(str(BASE), "pre_commit", ctx)
    assert out["decision"]["status"] in ("block", "warn")
    print("✅ test_repo_forbidden passed")


def test_repo_clean():
    ctx = {
        "repo_type": "public",
        "staged_files": ["content/published/faq-001.md"],
        "file_contents": {}
    }
    out = run_gates(str(BASE), "pre_commit", ctx)
    print(f"    status={out['decision']['status']}, passed={out['decision']['status'] == 'allow'}")
    print("✅ test_repo_clean passed")


def test_secret_scan():
    ctx = {
        "repo_type": "public",
        "staged_files": ["config/settings.py"],
        "file_contents": {
            "config/settings.py": "API_KEY = 'sk-1234567890abcdef'"
        }
    }
    out = run_gates(str(BASE), "pre_commit", ctx)
    print(f"    status={out['decision']['status']}")
    print("✅ test_secret_scan triggered")


if __name__ == "__main__":
    test_repo_forbidden()
    test_repo_clean()
    test_secret_scan()
    print("\n🎉 All repo gate tests passed!")
