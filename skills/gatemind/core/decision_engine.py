from .utils import ACTION_RANK


def decide(results: list[dict]) -> dict:
    failed = [r for r in results if r.get("failed")]
    failed_sorted = sorted(
        failed,
        key=lambda x: (x.get("priority_rank", 5), -ACTION_RANK.get(x.get("action", "allow"), 0))
    )

    final_action = "allow"
    for r in failed_sorted:
        act = r.get("action", "warn")
        if ACTION_RANK.get(act, 0) > ACTION_RANK.get(final_action, 0):
            final_action = act

    status = "allow"
    if final_action == "warn":
        status = "warn"
    elif final_action in ("require_evidence", "require_user_confirm"):
        status = final_action
    elif final_action == "block":
        status = "block"

    return {
        "status": status,
        "final_action": final_action,
        "failed_count": len(failed),
        "violations": failed_sorted,
    }
