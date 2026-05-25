import re
from .utils import PRIORITY_RANK


def _guess_without_evidence(ctx: dict, args: dict) -> tuple[bool, str]:
    draft = ctx.get("draft_response", "") or ""
    guess_words = args.get("guess_words", ["可能", "大概", "应该", "我猜", "maybe", "probably"])
    evidence_words = args.get("evidence_words", ["根据", "证据", "日志", "来源", "数据", "I checked", "from"])

    hit_guess = any(w in draft for w in guess_words)
    hit_evidence = any(w in draft for w in evidence_words)
    failed = hit_guess and not hit_evidence
    return failed, "检测到推测表达但缺少依据标记"


def _time_without_timezone(ctx: dict, args: dict) -> tuple[bool, str]:
    draft = ctx.get("draft_response", "") or ""
    time_words = args.get("time_words", ["今天", "明天", "现在", "时间", "date", "today", "now"])
    tz_words = args.get("timezone_words", ["UTC", "CST", "北京时间", "Asia/Shanghai", "时区"])
    hit_time = any(w in draft for w in time_words)
    hit_tz = any(w in draft for w in tz_words)
    failed = hit_time and not hit_tz
    return failed, "涉及时间信息但未明确时区"


def _long_document_without_intent(ctx: dict, args: dict) -> tuple[bool, str]:
    user_input = ctx.get("user_input", "") or ""
    threshold = int(args.get("length_threshold", 800))
    intent_confirmed = bool(ctx.get("intent_confirmed", False))
    failed = len(user_input) >= threshold and not intent_confirmed
    return failed, "用户输入疑似长文档，但未做意图确认"


def _high_risk_action_without_confirm(ctx: dict, args: dict) -> tuple[bool, str]:
    cmds = " ".join(ctx.get("planned_commands", []) or [])
    patterns = args.get("risk_patterns", [r"rm\s+-rf", r"chmod\s+777", r"DROP\s+TABLE", r"开放公网", r"sudo"])
    matched = any(re.search(p, cmds, flags=re.IGNORECASE) for p in patterns)
    user_confirmed = bool(ctx.get("user_confirmed", False))
    failed = matched and not user_confirmed
    return failed, "检测到高风险操作但未确认"


def _constraint_violation_simple(ctx: dict, args: dict) -> tuple[bool, str]:
    user_constraints = ctx.get("user_constraints", []) or []
    text = (ctx.get("draft_response", "") or "") + " " + " ".join(ctx.get("planned_commands", []) or [])
    violated = []
    for c in user_constraints:
        c = str(c)
        if c.startswith("不要"):
            kw = c.replace("不要", "").strip()
            if kw and kw in text:
                violated.append(kw)
    failed = len(violated) > 0
    return failed, f"违反用户约束: {violated}" if failed else "未检测到约束冲突"


def _patch_scope_without_plan(ctx: dict, args: dict) -> tuple[bool, str]:
    files_n = int(ctx.get("changed_files_count", 0))
    lines_n = int(ctx.get("changed_lines", 0))
    has_plan = bool(ctx.get("has_change_plan", False))
    f_th = int(args.get("file_threshold", 8))
    l_th = int(args.get("line_threshold", 300))
    failed = (files_n > f_th or lines_n > l_th) and not has_plan
    return failed, "变更范围过大但缺少变更计划"


def _repo_forbidden_paths(ctx: dict, args: dict) -> tuple[bool, str]:
    repo_type = ctx.get("repo_type", "unknown")
    staged_files = ctx.get("staged_files", []) or []
    apply_repo_types = args.get("apply_repo_types", ["public"])
    if repo_type not in apply_repo_types:
        return False, "仓库类型不匹配，跳过"

    forbidden = args.get("forbidden_regex", [])
    bad = []
    for f in staged_files:
        for r in forbidden:
            if re.search(r, f):
                bad.append(f)
                break
    failed = len(bad) > 0
    return failed, f"命中禁止路径: {bad}" if failed else "未命中禁止路径"


def _repo_secret_scan(ctx: dict, args: dict) -> tuple[bool, str]:
    patterns = args.get("secret_patterns", [
        r"AKIA[0-9A-Z]{16}",
        r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]+",
    ])
    exclude_paths = args.get("exclude_paths", [])
    file_contents = ctx.get("file_contents", {}) or {}
    bad = []
    for path, content in file_contents.items():
        # 跳过白名单路径
        if any(re.search(ep, path) for ep in exclude_paths):
            continue
        for p in patterns:
            if re.search(p, content or ""):
                bad.append(path)
                break
    failed = len(bad) > 0
    return failed, f"检测到疑似密钥泄露: {bad}" if failed else "未检测到密钥模式"


def _constraint_filter_skip(ctx: dict, args: dict) -> tuple[bool, str]:
    """
    方案过滤门 — 给方案前检查是否过滤了用户已知约束。
    旧 check_filter_skip.sh 的升级版。
    """
    draft = ctx.get("draft_response", "") or ""
    cmds = " ".join(ctx.get("planned_commands", []) or [])
    combined_text = draft + " " + cmds

    # 如果回复不涉及给方案/推荐，直接放行
    option_keywords = args.get("option_keywords", ["方案", "建议", "推荐", "选择", "可以", "option", "suggest", "recommend"])
    has_options = any(kw in combined_text for kw in option_keywords)
    if not has_options:
        return False, ""

    # 检查用户已知约束是否被引用
    user_constraints = ctx.get("user_constraints", []) or []
    if not user_constraints:
        return False, "无已知用户约束，跳过"

    # 检查是否有过滤动作（排除不可行选项 / 给出推荐结论）
    filter_markers = args.get("filter_markers", [
        "不可用", "不能使用", "不适合", "推荐", "建议使用",
        "not available", "not suitable", "recommend",
        "排除", "不推荐",
    ])
    has_filter = any(m in combined_text for m in filter_markers)
    gave_conclusion = bool(ctx.get("gave_conclusion", False))

    failed = has_options and not (has_filter or gave_conclusion)
    return failed, "回复包含方案选项但未做约束过滤，请排除不可行选项并给出推荐结论"


EVALUATORS = {
    "guess_without_evidence": _guess_without_evidence,
    "time_without_timezone": _time_without_timezone,
    "long_document_without_intent": _long_document_without_intent,
    "high_risk_action_without_confirm": _high_risk_action_without_confirm,
    "constraint_violation_simple": _constraint_violation_simple,
    "patch_scope_without_plan": _patch_scope_without_plan,
    "repo_forbidden_paths": _repo_forbidden_paths,
    "repo_secret_scan": _repo_secret_scan,
    "constraint_filter_skip": _constraint_filter_skip,
}


def evaluate_policy(policy: dict, ctx: dict) -> dict:
    policy_id = policy.get("id", "unknown")
    lifecycle = (policy.get("lifecycle") or {}).get("status", "active")
    if lifecycle == "deprecated":
        return {
            "policy_id": policy_id, "status": "skipped", "failed": False,
            "action": "allow", "reason": "deprecated", "priority": policy.get("priority", "P5")
        }

    check = policy.get("check", {}) or {}
    kind = check.get("kind")
    args = check.get("args", {}) or {}

    fn = EVALUATORS.get(kind)
    if not fn:
        return {
            "policy_id": policy_id, "status": "error", "failed": False,
            "action": "warn", "reason": f"unknown check kind: {kind}", "priority": policy.get("priority", "P5")
        }

    failed, reason = fn(ctx, args)
    on_fail = (policy.get("decision", {}) or {}).get("on_fail", "warn")
    action = on_fail if failed else "allow"

    # candidate / shadow 不硬拦截
    if lifecycle in ("candidate", "shadow") and failed and on_fail == "block":
        action = "warn"

    return {
        "policy_id": policy_id,
        "name": policy.get("name", policy_id),
        "phase": policy.get("phase"),
        "priority": policy.get("priority", "P5"),
        "severity": policy.get("severity", "low"),
        "lifecycle": lifecycle,
        "failed": failed,
        "enforce": lifecycle == "active",
        "action": action,
        "reason": reason,
        "message": policy.get("message", ""),
        "status": "fail" if failed else "pass",
        "priority_rank": PRIORITY_RANK.get(policy.get("priority", "P5"), 5),
    }
