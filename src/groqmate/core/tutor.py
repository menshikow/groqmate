from litellm import acompletion
from groqmate.core.models import LessonPlan
from groqmate.core.state import Session
from groqmate.core.providers import ProviderConfig, Provider
from groqmate.core.config import Config
from typing import AsyncIterator, Optional
import json
import os


SYSTEM_PROMPT = """You are Groqmate, a terse and encouraging learning coach.
You teach through atomic chunks, not lectures.

Rules:
- Use ASCII art for diagrams when helpful
- Use Unicode math symbols (∫, ∑, √, π, ^) instead of LaTeX
- Be concise. No fluff. Maximum 3-4 sentences per response.
- When asked for a quiz, provide a single clear question.
- Always format code blocks with proper syntax."""

PLAN_PROMPT = """Generate a JSON lesson plan for the topic: "{topic}"

Output ONLY valid JSON in this exact format:
{{
  "topic": "<topic>",
  "steps": [
    {{
      "index": 0,
      "title": "<short title, 2-4 words>",
      "concept": "<one paragraph explanation, 2-3 sentences>",
      "quiz_question": "<a single question to test understanding>",
      "quiz_answer": "<the correct answer, keep it short>"
    }},
    {{
      "index": 1,
      "title": "<next concept title>",
      "concept": "<explanation>",
      "quiz_question": "<question>",
      "quiz_answer": "<answer>"
    }}
  ]
}}

Generate exactly 5 steps that progressively build understanding.
Start with basics, end with practical application or common pitfalls."""

EXPLAIN_PROMPT = """Explain this concept to the user. Be concise and engaging.

Topic: {topic}
Step {step_num}: {step_title}
Concept: {concept}

Guidelines:
- Start with a brief, punchy explanation (2-3 sentences max)
- Use an analogy if helpful
- Include a code example if relevant
- End with: "Quiz: {quiz_question}"
- Keep total response under 100 words"""

REPHRASE_PROMPT = """The user is stuck. Explain this concept using a completely different analogy.

Topic: {topic}
Original concept: {concept}

Pick from: cooking, sports, gaming, music, travel, or building.
Be very brief - 3 sentences max. Make it click."""

SUMMARY_PROMPT = """Create a markdown summary of this lesson for the user to save.

Topic: {topic}

Steps:
{steps}

Format as clean markdown with:
- Main heading with topic
- Each step as a subheading
- Bullet points for key concepts
- Keep it scannable and useful for review"""


ENV_KEY_MAPPING = {
    "groq": "GROQ_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "mistral": "MISTRAL_API_KEY",
}


class Tutor:
    def __init__(
        self,
        provider_config: Optional[ProviderConfig] = None,
        config: Optional[Config] = None,
    ):
        self.provider_config = provider_config or ProviderConfig()
        self.config = config or Config.load()
        self.model = self.provider_config.get_model_string()

        if not self.provider_config.is_local():
            self._setup_api_key()

    def _setup_api_key(self) -> None:
        provider = self.provider_config.provider.value
        api_key = self.config.get_api_key(provider)

        if not api_key:
            provider_upper = provider.upper()
            raise ValueError(
                f"No API key for {provider_upper}. "
                f"Press Ctrl+P to open settings and add your API key, "
                f"or set the {ENV_KEY_MAPPING.get(provider, 'API_KEY')} environment variable."
            )

        env_var = ENV_KEY_MAPPING.get(provider)
        if env_var:
            os.environ[env_var] = api_key

    async def generate_plan(self, topic: str) -> LessonPlan:
        response = await acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": PLAN_PROMPT.format(topic=topic)},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from API")
        data = json.loads(content)
        return LessonPlan(**data)

    async def explain_step_stream(self, session: Session) -> AsyncIterator[str]:
        step = session.current_step()
        if not step:
            yield "No active lesson. Start with 'Teach me <topic>'"
            return

        if not session.state.plan:
            yield "No lesson plan loaded."
            return

        prompt = EXPLAIN_PROMPT.format(
            topic=session.state.plan.topic,
            step_num=step.index + 1,
            step_title=step.title,
            concept=step.concept,
            quiz_question=step.quiz_question,
        )

        response = await acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            temperature=0.7,
        )

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def check_answer(
        self, user_answer: str, session: Session
    ) -> tuple[bool, str]:
        step = session.current_step()
        if not step:
            return False, "No active lesson."

        expected = step.quiz_answer.strip().lower()
        actual = user_answer.strip().lower()

        if expected in actual or actual in expected:
            return True, "Correct! Type `next` to continue."

        similarity = len(set(expected.split()) & set(actual.split()))
        if similarity >= len(expected.split()) // 2:
            return False, f"Close! The answer is related to: {step.quiz_answer}"

        return False, f"Not quite. Hint: Think about {step.quiz_answer[:10]}..."

    async def rephrase_stream(self, session: Session) -> AsyncIterator[str]:
        step = session.current_step()
        if not step:
            yield "No active lesson."
            return

        if not session.state.plan:
            yield "No lesson plan loaded."
            return

        prompt = REPHRASE_PROMPT.format(
            topic=session.state.plan.topic, concept=step.concept
        )

        response = await acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            stream=True,
            temperature=0.9,
        )

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_summary(self, session: Session) -> str:
        if not session.state.plan:
            return "No lesson to summarize."

        steps_text = "\n".join(
            [
                f"{i + 1}. {s.title}: {s.concept}"
                for i, s in enumerate(session.state.plan.steps)
            ]
        )

        prompt = SUMMARY_PROMPT.format(topic=session.state.plan.topic, steps=steps_text)

        response = await acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )

        return response.choices[0].message.content or "# Error generating summary"
