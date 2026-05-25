from skills.gatemind.core.decision_engine import decide


def test_priority_block_wins():
    results = [
        {"failed": True, "priority_rank": 2, "action": "warn"},
        {"failed": True, "priority_rank": 0, "action": "block"},
    ]
    out = decide(results)
    assert out["status"] == "block"
