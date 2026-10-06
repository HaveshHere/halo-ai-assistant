import re


NUMBER_WORDS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
}


def route_question(question):
    original = question.strip()
    normalized = original.lower()

    if not normalized:
        return {"intent": "unknown"}

    if normalized in {"ai status", "model status"}:
        return {"intent": "ai_status"}

    if normalized.startswith("ask ai "):
        return {"intent": "ask_ai", "text": original[len("ask ai "):].strip()}

    if "model" in normalized:
        return {"intent": "model"}

    task_number = _extract_completed_task_number(normalized)
    if task_number is not None:
        return {"intent": "complete_task", "task_number": task_number}

    note = _extract_note(original, normalized)
    if note is not None:
        return {"intent": "remember", "text": note}

    search_query = _extract_search_query(normalized)
    if search_query:
        return {"intent": "search", "text": search_query}

    if _has_any(normalized, ["briefing", "summary", "morning update", "status update", "what's going on"]):
        return {"intent": "briefing"}

    if _has_any(normalized, ["anything important", "important today", "what matters today"]):
        return {"intent": "important_today"}

    if _has_any(normalized, ["email", "inbox", "messages"]):
        return {"intent": "emails"}

    if _has_any(normalized, ["calendar", "meeting", "schedule", "appointments"]):
        return {"intent": "calendar"}

    if _has_any(normalized, ["engineering", "ticket", "bug", "jira", "issue"]):
        return {"intent": "engineering"}

    if _has_any(normalized, ["plan", "today", "work on first", "where should i start", "what should i do next"]):
        return {"intent": "daily_plan"}

    if _has_any(normalized, ["prioritize", "priority", "urgent"]):
        return {"intent": "daily_plan"}

    if _has_any(normalized, ["completed", "done", "finished tasks"]):
        return {"intent": "completed_tasks"}

    if _has_any(normalized, ["note", "memory", "remembered"]):
        return {"intent": "notes"}

    if "how many" in normalized:
        return {"intent": "task_count"}

    if _has_any(normalized, ["list", "show", "tasks", "to do", "todo", "on my plate"]):
        return {"intent": "tasks"}

    return {"intent": "unknown"}


def _extract_completed_task_number(normalized):
    match = re.search(r"(?:complete|finish|mark done|mark)\s+(?:task\s+)?(\d+|first|second|third|fourth|fifth)", normalized)

    if not match:
        return None

    task_number = match.group(1)

    if task_number.isdigit():
        return int(task_number)

    return NUMBER_WORDS[task_number]


def _extract_note(original, normalized):
    for prefix in ["remember ", "note that ", "save note "]:
        if normalized.startswith(prefix):
            return original[len(prefix):].strip()

    return None


def _extract_search_query(normalized):
    for prefix in ["find ", "search ", "look for ", "anything about ", "tell me about "]:
        if normalized.startswith(prefix):
            return normalized[len(prefix):].strip(" ?.!")

    return None


def _has_any(text, phrases):
    return any(phrase in text for phrase in phrases)