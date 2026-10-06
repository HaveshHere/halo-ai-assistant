import unittest
from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agent import HaloAgent
from llm.ollama_client import LLMResult
from llm.reasoner import _build_prompt
from tools.email_inbox import fetch_recent_emails


class UnavailableReasoner:
    def enhance_plan(self, plan, context):
        return LLMResult(ok=False, error="test Ollama unavailable")

    def summarize_briefing(self, briefing, context):
        return LLMResult(ok=False, error="test Ollama unavailable")

    def analyze_important_today(self, plan, context):
        return LLMResult(ok=False, error="test Ollama unavailable")

    def answer_with_context(self, question, context):
        return LLMResult(ok=False, error="test Ollama unavailable")


class SuccessfulReasoner:
    def enhance_plan(self, plan, context):
        return LLMResult(ok=True, text="Start with the deadline task, then prepare for meetings.")

    def summarize_briefing(self, briefing, context):
        return LLMResult(ok=True, text="Today is task-heavy with one urgent onboarding deadline.")

    def analyze_important_today(self, plan, context):
        return LLMResult(ok=True, text="The onboarding deadline and backend mentor sync matter most.")

    def answer_with_context(self, question, context):
        return LLMResult(ok=True, text="Prepare questions about the backend API before the mentor sync.")


class HaloAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_directory.name)
        self.tasks_file = self.temp_path / "tasks.txt"
        self.completed_file = self.temp_path / "completed_tasks.txt"
        self.notes_file = self.temp_path / "notes.txt"
        self.tasks_file.write_text(
            "Review onboarding checklist by Friday\n"
            "Ask mentor about the backend API architecture\n"
            "Read the team coding standards document\n"
            "Prepare questions for the weekly engineering sync\n"
            "Set up local development environment\n"
        )
        self.completed_file.write_text("")
        self.notes_file.write_text("")

        self.agent = HaloAgent(
            self.tasks_file,
            events_file="data/calendar.txt",
            engineering_file="data/engineering_tasks.txt",
            completed_file=self.completed_file,
            notes_file=self.notes_file,
            reasoner=UnavailableReasoner(),
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_counts_tasks(self):
        self.assertIn("5 tasks", self.agent.answer("How many tasks do I have?"))

    def test_email_uses_sample_data(self):
        result = fetch_recent_emails()

        self.assertTrue(result["ok"])
        self.assertTrue(result["emails"])

    def test_calendar_uses_sample_data(self):
        with tempfile.TemporaryDirectory() as directory:
            events_file = Path(directory) / "calendar.txt"
            events_file.write_text("Sample-only meeting\n")
            agent = HaloAgent(
                self.tasks_file,
                events_file=events_file,
                engineering_file="data/engineering_tasks.txt",
                completed_file=self.completed_file,
                notes_file=self.notes_file,
                reasoner=UnavailableReasoner(),
            )

        self.assertEqual(agent.events, ["Sample-only meeting"])

    def test_lists_calendar(self):
        self.assertIn("Daily engineering standup", self.agent.answer("Show my calendar"))

    def test_lists_engineering_tasks(self):
        self.assertIn("BUG-102", self.agent.answer("Show engineering tickets"))

    def test_builds_daily_plan(self):
        plan = self.agent.answer("Plan my day")

        self.assertIn("Focused plan", plan)
        self.assertIn("Why:", plan)
        self.assertIn("BUG-102", plan)

    def test_suggests_prioritization(self):
        self.assertIn("Focused plan", self.agent.answer("What should I prioritize?"))

    def test_understands_natural_language_task_request(self):
        self.assertIn("Review onboarding", self.agent.answer("What is on my plate?"))

    def test_understands_natural_language_calendar_request(self):
        answer = self.agent.answer("Do I have meetings today?")

        self.assertIn("Daily engineering standup", answer)
        self.assertNotIn("Focused plan", answer)

    def test_understands_natural_language_search_request(self):
        result = self.agent.answer("Anything about backend?")

        self.assertIn("tasks", result)
        self.assertIn("backend", result)

    def test_completes_task_with_natural_language(self):
        self.assertIn("Completed task 1", self.agent.answer("Mark first task done"))

    def test_builds_briefing(self):
        briefing = self.agent.answer("Give me a briefing")

        self.assertIn("Halo Briefing", briefing)
        self.assertIn("Engineering tickets", briefing)
        self.assertIn("Recommended Focus", briefing)

    def test_completes_numbered_task(self):
        with tempfile.TemporaryDirectory() as directory:
            tasks_file = Path(directory) / "tasks.txt"
            completed_file = Path(directory) / "completed_tasks.txt"
            tasks_file.write_text("First task\nSecond task\n")

            agent = HaloAgent(
                tasks_file,
                events_file="data/calendar.txt",
                engineering_file="data/engineering_tasks.txt",
                completed_file=completed_file,
                notes_file=Path(directory) / "notes.txt",
                reasoner=UnavailableReasoner(),
            )

            self.assertIn("Completed task 1", agent.answer("Complete task 1"))
            self.assertEqual(tasks_file.read_text(), "Second task\n")
            self.assertEqual(completed_file.read_text(), "First task\n")

    def test_lists_completed_tasks(self):
        self.agent.answer("Complete task 1")

        self.assertIn("Review onboarding", self.agent.answer("Show completed tasks"))

    def test_searches_across_context_sources(self):
        result = self.agent.answer("Find backend")

        self.assertIn("tasks", result)
        self.assertIn("calendar", result)
        self.assertIn("engineering", result)

    def test_remembers_and_lists_notes(self):
        self.assertIn("Remembered", self.agent.answer("Remember ask mentor about logging"))
        self.assertIn("ask mentor about logging", self.agent.answer("Show notes"))

    def test_searches_notes(self):
        self.agent.answer("Remember backend owner is the platform team")

        self.assertIn("notes", self.agent.answer("Find platform"))

    def test_reports_ai_status(self):
        self.assertIn("Ollama", self.agent.answer("AI status"))
        self.assertIn("qwen3", self.agent.answer("AI status"))

    def test_reports_model_status(self):
        self.assertIn("Ollama", self.agent.answer("Model status"))

    def test_drafts_ai_context_without_live_call(self):
        answer = self.agent.answer("Ask AI what should I prepare for today?")

        self.assertIn("AI reasoning is unavailable", answer)
        self.assertIn("Tasks:", answer)
        self.assertIn("Question: what should I prepare for today?", answer)

    def test_plan_includes_ai_reasoning_when_available(self):
        agent = HaloAgent(
            self.tasks_file,
            events_file="data/calendar.txt",
            engineering_file="data/engineering_tasks.txt",
            completed_file=self.completed_file,
            notes_file=self.notes_file,
            reasoner=SuccessfulReasoner(),
        )

        answer = agent.answer("What should I work on first?")

        self.assertIn("Focused plan", answer)
        self.assertIn("AI Reasoning", answer)
        self.assertIn("deadline task", answer)

    def test_reasoner_prompt_requests_concise_non_thinking_answer(self):
        prompt = _build_prompt("Explain the plan.", "Existing local plan", {"tasks": ["Review checklist"]})

        self.assertIn("/no_think", prompt)
        self.assertIn("at most two short sentences", prompt)
        self.assertIn("Review checklist", prompt)

    def test_briefing_includes_ai_summary_when_available(self):
        agent = HaloAgent(
            self.tasks_file,
            events_file="data/calendar.txt",
            engineering_file="data/engineering_tasks.txt",
            completed_file=self.completed_file,
            notes_file=self.notes_file,
            reasoner=SuccessfulReasoner(),
        )

        answer = agent.answer("Give me a briefing")
        self.assertIn("Halo Briefing", answer)
        self.assertIn("AI Summary", answer)
        self.assertIn("task-heavy", answer)

    def test_important_today_uses_ai_reasoning(self):
        agent = HaloAgent(
            self.tasks_file,
            events_file="data/calendar.txt",
            engineering_file="data/engineering_tasks.txt",
            completed_file=self.completed_file,
            notes_file=self.notes_file,
            reasoner=SuccessfulReasoner(),
        )

        answer = agent.answer("Anything important today?")
        self.assertIn("Focused plan", answer)
        self.assertIn("AI Reasoning", answer)
        self.assertIn("backend mentor sync", answer)

    def test_important_today_passes_authoritative_plan_to_reasoner(self):
        class PlanCapturingReasoner(SuccessfulReasoner):
            def analyze_important_today(self, plan, context):
                self.plan = plan
                return LLMResult(ok=True, text="The listed onboarding deadline is the main focus.")

        reasoner = PlanCapturingReasoner()
        agent = HaloAgent(
            self.tasks_file,
            events_file="data/calendar.txt",
            engineering_file="data/engineering_tasks.txt",
            completed_file=self.completed_file,
            notes_file=self.notes_file,
            reasoner=reasoner,
        )

        answer = agent.answer("Anything important today?")

        self.assertIn("Review onboarding checklist by Friday", reasoner.plan)
        self.assertIn("Review onboarding checklist by Friday", answer)
        self.assertIn("onboarding deadline", answer)

    def test_preserves_note_case(self):
        self.agent.answer("Remember Ask Ravi About API Logs")

        self.assertIn("Ask Ravi About API Logs", self.agent.answer("Show notes"))
        self.assertNotIn("Remember Ask Ravi", self.agent.answer("Show notes"))


if __name__ == "__main__":
    unittest.main()
