from skills.gatemind.core.policy_validator import validate_policy_dir


def test_validate_policy_dir():
    ok, report = validate_policy_dir(
        "skills/gatemind/policies",
        "skills/gatemind/schemas/policy.schema.json",
    )
    assert isinstance(report, dict)
    assert report["total_files"] >= 1
    assert ok is True
