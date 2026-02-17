from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional


class SessionStatus(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    TEACHING = "teaching"
    QUIZ = "quiz"
    COMPLETE = "complete"


class LessonStep(BaseModel):
    index: int
    title: str
    concept: str
    quiz_question: str
    quiz_answer: str


class LessonPlan(BaseModel):
    topic: str
    steps: List[LessonStep] = Field(default_factory=list)

    @property
    def total_steps(self) -> int:
        return len(self.steps)


class SessionState(BaseModel):
    plan: Optional[LessonPlan] = None
    current_step: int = 0
    completed: List[int] = Field(default_factory=list)
    status: SessionStatus = SessionStatus.IDLE
