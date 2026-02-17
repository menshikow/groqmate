from groqmate.core.models import SessionState, SessionStatus, LessonPlan, LessonStep
from typing import Optional


class Session:
    def __init__(self):
        self.state = SessionState()

    def load_plan(self, plan: LessonPlan) -> None:
        self.state.plan = plan
        self.state.current_step = 0
        self.state.completed = []
        self.state.status = SessionStatus.TEACHING

    def advance(self) -> bool:
        if not self.state.plan:
            return False
        if self.state.current_step >= self.state.plan.total_steps - 1:
            self.state.status = SessionStatus.COMPLETE
            return False
        self.state.completed.append(self.state.current_step)
        self.state.current_step += 1
        return True

    def current_step(self) -> Optional[LessonStep]:
        if not self.state.plan:
            return None
        if self.state.current_step >= len(self.state.plan.steps):
            return None
        return self.state.plan.steps[self.state.current_step]

    def is_complete(self) -> bool:
        return self.state.status == SessionStatus.COMPLETE

    def reset(self) -> None:
        self.state = SessionState()

    def enter_quiz(self) -> None:
        self.state.status = SessionStatus.QUIZ

    def exit_quiz(self) -> None:
        self.state.status = SessionStatus.TEACHING

    def is_in_quiz(self) -> bool:
        return self.state.status == SessionStatus.QUIZ

    def progress_text(self) -> str:
        if not self.state.plan:
            return ""
        return f"Step {self.state.current_step + 1}/{self.state.plan.total_steps}"
