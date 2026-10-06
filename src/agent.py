from llm import HaloReasoner
from tools.task_file import complete_task, load_tasks
from tools.ai_model import ai_status
from tools.email_inbox import fetch_recent_emails
from tools.calendar_file import load_events
from tools.engineering_file import load_engineering_tasks
from tools.intent_router import route_question
from tools.notes_file import add_note, load_notes
from tools.planner import build_ranked_plan
from tools.search import search_items
from settings import get_recommended_model


class HaloAgent:
    def __init__(
        self,
        tasks_file,
        events_file="data/calendar.txt",
        engineering_file="data/engineering_tasks.txt",
        completed_file="data/completed_tasks.txt",
        notes_file="data/notes.txt",
        reasoner=None,
    ):
        self.tasks_file = tasks_file
        self.completed_file = completed_file
        self.notes_file = notes_file
        self.tasks = load_tasks(tasks_file)
        self.completed_tasks = load_tasks(completed_file)
        self.events = load_events(events_file)
        self.engineering_tasks = load_engineering_tasks(engineering_file)
        self.notes = load_notes(notes_file)
        self.reasoner = reasoner or HaloReasoner()

    def answer(self, question):
        question = question.strip()
        intent = route_question(question)

        if intent["intent"] == "ai_status":
            return ai_status()

        if intent["intent"] == "model":
            return f"The recommended starter AI model for this project is {get_recommended_model()}."

        if intent["intent"] == "ask_ai":
            return self._ask_ai(intent["text"])

        if intent["intent"] == "emails":
            inbox = fetch_recent_emails()

            if not inbox["ok"]:
                return inbox["error"]

            if not inbox["emails"]:
                return "Your inbox is empty."

            return "\n".join(
                f"- {email['subject']} | From: {email['from']} | Date: {email['date']}"
                for email in inbox["emails"]
            )

        if intent["intent"] == "calendar":
            if not self.events:
                return "You do not have any calendar events yet."

            events_text = "\n".join(f"- {event}" for event in self.events)
            return events_text

        if intent["intent"] == "engineering":
            if not self.engineering_tasks:
                return "You do not have any engineering tasks yet."

            return "\n".join(f"- {task}" for task in self.engineering_tasks)

        if intent["intent"] == "briefing":
            return self._briefing()

        if intent["intent"] == "complete_task":
            return self._complete_task(intent["task_number"])

        if intent["intent"] == "remember":
            return self._remember(intent["text"])

        if intent["intent"] == "search":
            return self._search(intent["text"])

        if intent["intent"] == "notes":
            if not self.notes:
                return "I do not have any notes yet."

            return "\n".join(f"- {note}" for note in self.notes)

        if intent["intent"] == "completed_tasks":
            if not self.completed_tasks:
                return "You do not have any completed tasks yet."

            return "\n".join(f"- {task}" for task in self.completed_tasks)

        if intent["intent"] == "daily_plan":
            return self._daily_plan()

        if intent["intent"] == "important_today":
            return self._important_today()

        if intent["intent"] == "task_count":
            return f"You have {len(self.tasks)} tasks."

        if intent["intent"] == "tasks":
            return "\n".join(f"- {task}" for task in self.tasks)

        return "I can answer questions about tasks, emails, calendar events, engineering tickets, search, and today's plan."

    def _daily_plan(self):
        plan = self._daily_plan_without_ai()
        reasoning = self.reasoner.enhance_plan(plan, self._context())
        return self._with_ai_reasoning(plan, reasoning)

    def _daily_plan_without_ai(self):
        ranked_plan = build_ranked_plan(self.tasks, self.events, self.engineering_tasks)

        if not ranked_plan:
            return "I do not have enough context to build a daily plan yet."

        lines = ["Focused plan for today:"]

        for index, (category, item, reason) in enumerate(ranked_plan, start=1):
            lines.append(f"{index}. {category}: {item}")
            lines.append(f"   Why: {reason}")

        return "\n".join(lines)

    def _briefing(self):
        inbox = fetch_recent_emails()
        email_count = len(inbox["emails"]) if inbox["ok"] else 0
        ranked_plan = build_ranked_plan(self.tasks, self.events, self.engineering_tasks)
        top_recommendation = ranked_plan[0][1] if ranked_plan else "No recommendation available yet."

        briefing = "\n".join(
            [
                "Halo Briefing",
                "=============",
                "Status",
                f"- Tasks: {len(self.tasks)} open",
                f"- Completed tasks: {len(self.completed_tasks)} done",
                f"- Emails: {email_count} available",
                f"- Calendar events: {len(self.events)} scheduled",
                f"- Engineering tickets: {len(self.engineering_tasks)} tracked",
                f"- Notes: {len(self.notes)} remembered",
                "",
                "Recommended Focus",
                f"- {top_recommendation}",
                "",
                "Next Step",
                "- Ask 'Plan my day' for the ordered action plan.",
            ]
        )
        reasoning = self.reasoner.summarize_briefing(briefing, self._context())
        return self._with_ai_reasoning(briefing, reasoning, title="AI Summary")

    def _complete_task(self, task_number):
        completed_task = complete_task(self.tasks_file, self.completed_file, task_number)

        if completed_task is None:
            return f"Task {task_number} does not exist."

        self.tasks = load_tasks(self.tasks_file)
        self.completed_tasks = load_tasks(self.completed_file)
        return f"Completed task {task_number}: {completed_task}"

    def _search(self, query):
        inbox = fetch_recent_emails()
        emails = inbox["emails"] if inbox["ok"] else []
        matches = search_items(
            query,
            {
                "tasks": self.tasks,
                "completed tasks": self.completed_tasks,
                "emails": emails,
                "calendar": self.events,
                "engineering": self.engineering_tasks,
                "notes": self.notes,
            },
        )

        if not matches:
            return f"I could not find anything matching '{query}'."

        return "\n".join(f"- {source}: {text}" for source, text in matches)

    def _ask_ai(self, question):
        if not question:
            return "Ask an AI question like: Ask AI what should I prepare for today?"

        context_summary = "\n".join(
            [
                f"Tasks: {len(self.tasks)} open",
                f"Completed tasks: {len(self.completed_tasks)} done",
                f"Calendar events: {len(self.events)} scheduled",
                f"Engineering tickets: {len(self.engineering_tasks)} tracked",
                f"Notes: {len(self.notes)} remembered",
            ]
        )

        reasoning = self.reasoner.answer_with_context(question, self._context())

        if reasoning.ok:
            return reasoning.text

        return "\n".join(
            [
                "AI reasoning is unavailable right now.",
                f"Reason: {reasoning.error}",
                "Here is the context I would send to Qwen3 through Ollama:",
                context_summary,
                f"Question: {question}",
            ]
        )

    def _remember(self, note):
        if not note:
            return "Tell me what to remember, like: Remember ask mentor about logging."

        saved_note = add_note(self.notes_file, note)
        self.notes = load_notes(self.notes_file)
        return f"Remembered: {saved_note}"

    def _important_today(self):
        base = self._daily_plan_without_ai()
        reasoning = self.reasoner.analyze_important_today(base, self._context())
        return self._with_ai_reasoning(base, reasoning)

    def _context(self):
        inbox = fetch_recent_emails()
        emails = inbox["emails"] if inbox["ok"] else []

        return {
            "tasks": self.tasks,
            "completed tasks": self.completed_tasks,
            "emails": [
                f"{email['subject']} | From: {email['from']} | Date: {email['date']}"
                for email in emails
            ],
            "calendar events": self.events,
            "engineering tickets": self.engineering_tasks,
            "notes": self.notes,
        }

    def _with_ai_reasoning(self, base_output, reasoning, title="AI Reasoning"):
        if reasoning.ok:
            return "\n\n".join([base_output, title, reasoning.text])

        return "\n\n".join(
            [
                base_output,
                title,
                f"Ollama/Qwen3 is unavailable, so Halo is showing the trusted local result. ({reasoning.error})",
            ]
        )
