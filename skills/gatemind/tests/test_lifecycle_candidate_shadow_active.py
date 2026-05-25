from skills.gatemind.core.evaluators import evaluate_policy


def _policy(status):
    return {
        "id": "gate.test.lifecycle",
        "name": "lifecycle test",
        "phase": "pre_response",
        "priority": "P2",
        "severity": "medium",
        "lifecycle": {"status": status},
        "decision": {"on_fail": "block"},
        "check": {"kind": "guess_without_evidence", "args": {}},
        "message": "",
    }


def test_candidate_not_block():
    ctx = {"draft_response": "我猜可能是这样"}
    r = evaluate_policy(_policy("candidate"), ctx)
    assert r["action"] in ("warn", "allow")


def test_active_can_block():
    ctx = {"draft_response": "我猜可能是这样"}
    r = evaluate_policy(_policy("active"), ctx)
    assert r["action"] in ("block", "allow")
