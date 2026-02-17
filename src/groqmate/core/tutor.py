from groq import AsyncGroq
from groqmate.core.models import LessonPlan, LessonStep
from groqmate.core.state import Session
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


class Tutor:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = AsyncGroq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    async def generate_plan(self, topic: str) -> LessonPlan:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": PLAN_PROMPT.format(topic=topic)}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
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
            quiz_question=step.quiz_question
        )

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            temperature=0.7
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def check_answer(self, user_answer: str, session: Session) -> tuple[bool, str]:
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
            topic=session.state.plan.topic,
            concept=step.concept
        )

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            temperature=0.9
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_summary(self, session: Session) -> str:
        if not session.state.plan:
            return "No lesson to summarize."

        steps_text = "\n".join([
            f"{i+1}. {s.title}: {s.concept}"
            for i, s in enumerate(session.state.plan.steps)
        ])

        prompt = SUMMARY_PROMPT.format(
            topic=session.state.plan.topic,
            steps=steps_text
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        return response.choices[0].message.content or "# Error generating summary"
