from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

from core.runner import run_gates


def test_guess_gate_trigger():
    ctx = {"draft_response": "我猜可能是网络问题。"}
    out = run_gates(str(BASE), "pre_response", ctx)
    assert out["decision"]["status"] in ("require_evidence", "require_user_confirm", "warn")
    print("✅ test_guess_gate_trigger passed")


def test_timezone_gate_trigger():
    ctx = {"draft_response": "今天下午3点开会"}
    out = run_gates(str(BASE), "pre_response", ctx)
    assert out["decision"]["status"] in ("require_evidence", "warn")
    print("✅ test_timezone_gate_trigger passed")


def test_timezone_gate_pass():
    ctx = {"draft_response": "北京时间今天下午3点开会"}
    out = run_gates(str(BASE), "pre_response", ctx)
    assert out["decision"]["status"] == "allow"
    print("✅ test_timezone_gate_pass passed")


def test_filter_skip_trigger():
    # 给方案选项但没有约束过滤
    ctx = {
        "draft_response": "我建议三个方案：A方案B方案C方案",
        "user_constraints": ["不要用百度", "服务器在内网"]
    }
    out = run_gates(str(BASE), "pre_response", ctx)
    assert out["decision"]["status"] in ("require_evidence", "warn")
    print("✅ test_filter_skip_trigger passed")


def test_filter_skip_pass():
    # 给了方案 but 也做了过滤
    ctx = {
        "draft_response": "两个方案：方案A不适合内网，推荐方案B",
        "user_constraints": ["服务器在内网"],
        "gave_conclusion": True,
    }
    out = run_gates(str(BASE), "pre_response", ctx)
    assert out["decision"]["status"] == "allow"
    print("✅ test_filter_skip_pass passed")


if __name__ == "__main__":
    test_guess_gate_trigger()
    test_timezone_gate_trigger()
    test_timezone_gate_pass()
    test_filter_skip_trigger()
    test_filter_skip_pass()
    print("\n🎉 All fact gate tests passed!")
