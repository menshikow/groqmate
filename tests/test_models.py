import pytest
from groqmate.core.models import SessionStatus, LessonStep, LessonPlan, SessionState
from pydantic import ValidationError


class TestLessonStep:
    def test_create_lesson_step(self, sample_step):
        assert sample_step.index == 0
        assert sample_step.title == "Self-Reference"
        assert "recursive" in sample_step.concept.lower()

    def test_step_requires_all_fields(self):
        with pytest.raises(ValidationError):
            LessonStep(index=0, title="Test")

    def test_step_with_empty_strings(self):
        step = LessonStep(
            index=0, title="", concept="", quiz_question="", quiz_answer=""
        )
        assert step.title == ""

    def test_step_index_can_be_any_int(self):
        step = LessonStep(
            index=100,
            title="Test",
            concept="Test",
            quiz_question="?",
            quiz_answer="yes",
        )
        assert step.index == 100


class TestLessonPlan:
    def test_create_plan(self, sample_plan):
        assert sample_plan.topic == "Recursion"
        assert sample_plan.total_steps == 5

    def test_empty_plan_has_zero_steps(self):
        plan = LessonPlan(topic="Empty")
        assert plan.total_steps == 0

    def test_total_steps_property(self, sample_plan):
        assert sample_plan.total_steps == len(sample_plan.steps)

    def test_plan_with_single_step(self):
        plan = LessonPlan(
            topic="Single",
            steps=[
                LessonStep(
                    index=0,
                    title="Only",
                    concept="One step",
                    quiz_question="?",
                    quiz_answer="yes",
                )
            ],
        )
        assert plan.total_steps == 1

    def test_plan_requires_topic(self):
        with pytest.raises(ValidationError):
            LessonPlan(steps=[])


class TestSessionState:
    def test_default_state(self):
        state = SessionState()
        assert state.status == SessionStatus.IDLE
        assert state.plan is None
        assert state.current_step == 0
        assert state.completed == []

    def test_state_with_plan(self, sample_plan):
        state = SessionState(plan=sample_plan, status=SessionStatus.TEACHING)
        assert state.plan.topic == "Recursion"
        assert state.status == SessionStatus.TEACHING

    def test_state_current_step_defaults_to_zero(self):
        state = SessionState()
        assert state.current_step == 0

    def test_state_completed_defaults_to_empty_list(self):
        state = SessionState()
        assert state.completed == []
        assert len(state.completed) == 0


class TestSessionStatus:
    def test_all_statuses_exist(self):
        assert SessionStatus.IDLE.value == "idle"
        assert SessionStatus.PLANNING.value == "planning"
        assert SessionStatus.TEACHING.value == "teaching"
        assert SessionStatus.QUIZ.value == "quiz"
        assert SessionStatus.COMPLETE.value == "complete"

    def test_status_is_string_enum(self):
        assert SessionStatus.IDLE == "idle"
        assert isinstance(SessionStatus.IDLE, str)

    def test_status_can_be_compared(self):
        assert SessionStatus.IDLE == SessionStatus.IDLE
        assert SessionStatus.IDLE != SessionStatus.TEACHING

    def test_status_can_be_used_in_dict(self):
        d = {SessionStatus.IDLE: "waiting", SessionStatus.TEACHING: "active"}
        assert d[SessionStatus.IDLE] == "waiting"
