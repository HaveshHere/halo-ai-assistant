def build_ranked_plan(tasks, events, engineering_tasks):
    ranked_tasks = _rank_items(tasks, category="task")
    ranked_engineering = _rank_items(engineering_tasks, category="engineering")
    plan = []

    if ranked_tasks:
        plan.append(("Task", ranked_tasks[0], "Highest urgency or setup value."))

    if events:
        plan.append(("Meeting prep", events[0], "Prepare before the next scheduled event."))

    if ranked_engineering:
        plan.append(("Engineering", ranked_engineering[0], "Move technical work forward."))

    for task in ranked_tasks[1:3]:
        plan.append(("Task", task, "Follow-up work after the top priority."))

    return plan


def _rank_items(items, category):
    return sorted(items, key=lambda item: _priority_score(item, category), reverse=True)


def _priority_score(item, category):
    text = item.lower()
    score = 0

    if category == "engineering":
        if text.startswith("bug"):
            score += 60
        elif text.startswith("feat"):
            score += 30
        elif text.startswith("doc"):
            score += 20

    if any(word in text for word in ["friday", "today", "deadline", "due"]):
        score += 40

    if any(word in text for word in ["ask", "mentor", "sync", "unblock"]):
        score += 30

    if any(word in text for word in ["bug", "timeout", "issue"]):
        score += 25

    if any(word in text for word in ["set up", "setup", "environment"]):
        score += 20

    if any(word in text for word in ["read", "standards", "docs", "document"]):
        score += 10

    return score