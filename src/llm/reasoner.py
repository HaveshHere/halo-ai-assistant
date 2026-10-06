from llm.ollama_client import LLMResult, OllamaClient
from settings import get_ai_provider


class HaloReasoner:
    def __init__(self, client=None):
        self.client = client or OllamaClient()

    def enhance_plan(self, plan, context):
        prompt = _build_prompt(
            "Explain this work plan in a concise, practical way for an intern.",
            plan,
            context,
            getattr(self, "response_style", "Balanced"),
        )
        return self._generate(prompt)

    def summarize_briefing(self, briefing, context):
        prompt = _build_prompt(
            "Summarize this briefing and call out the most important focus.",
            briefing,
            context,
            getattr(self, "response_style", "Balanced"),
        )
        return self._generate(prompt)

    def analyze_important_today(self, plan, context):
        prompt = _build_prompt(
            "Explain what is important today and why the existing plan's first item should come first.",
            plan,
            context,
            getattr(self, "response_style", "Balanced"),
        )
        return self._generate(prompt)

    def answer_with_context(self, question, context):
        prompt = _build_prompt(
            f"Answer this question for an intern: {question}",
            "Use the provided context only.",
            context,
            getattr(self, "response_style", "Balanced"),
        )
        return self._generate(prompt)

    def _generate(self, prompt):
        if get_ai_provider().lower() != "ollama":
            return LLMResult(ok=False, error="AI_PROVIDER is not set to ollama")

        return self.client.generate(prompt)


def _build_prompt(instruction, source_output, context, response_style="Balanced"):
    delivery = {
        "Concise": "Answer in one short sentence with the most useful next step.",
        "Balanced": "Answer in at most two short sentences.",
        "Detailed": "Give a clear, useful explanation in up to one short paragraph, with relevant context.",
    }.get(response_style, "Answer in at most two short sentences.")
    return "\n\n".join(
        [
            "You are Halo, an AI assistant for an intern.",
            "/no_think",
            instruction,
            "Rules:",
            "- Use only the context provided.",
            "- Do not invent meetings, emails, tickets, or tasks.",
            "- Do not reorder or contradict existing Halo recommendations.",
            f"- {delivery}",
            "- Give a clear conclusion and supporting rationale, not analysis steps.",
            "Existing Halo output:",
            source_output,
            "Context:",
            _format_context(context),
        ]
    )


def _format_context(context):
    lines = []

    for name, items in context.items():
        lines.append(f"{name}:")

        if not items:
            lines.append("- None")
            continue

        for item in items:
            lines.append(f"- {item}")

    return "\n".join(lines)