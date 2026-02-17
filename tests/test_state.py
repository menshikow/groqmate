import pytest
from groqmate.core.state import Session
from groqmate.core.models import SessionStatus


class TestSession:
    def test_session_starts_idle(self, empty_session):
        assert empty_session.state.status == SessionStatus.IDLE
        assert empty_session.state.plan is None

    def test_load_plan(self, session, sample_plan):
        assert session.state.plan.topic == "Recursion"
        assert session.state.status == SessionStatus.TEACHING
        assert session.state.current_step == 0
        assert session.state.completed == []

    def test_current_step_returns_step(self, session):
        step = session.current_step()
        assert step is not None
        assert step.index == 0
        assert step.title == "Self-Reference"

    def test_current_step_none_without_plan(self, empty_session):
        assert empty_session.current_step() is None

    def test_advance_moves_forward(self, session):
        assert session.state.current_step == 0
        result = session.advance()
        assert result is True
        assert session.state.current_step == 1
        assert 0 in session.state.completed

    def test_advance_returns_false_at_end(self, session):
        for _ in range(4):
            session.advance()
        result = session.advance()
        assert result is False
        assert session.is_complete()

    def test_advance_without_plan_returns_false(self, empty_session):
        assert empty_session.advance() is False

    def test_is_complete(self, session):
        assert not session.is_complete()
        session.state.status = SessionStatus.COMPLETE
        assert session.is_complete()

    def test_reset(self, session):
        session.advance()
        session.advance()
        session.reset()
        assert session.state.status == SessionStatus.IDLE
        assert session.state.plan is None
        assert session.state.current_step == 0

    def test_enter_exit_quiz(self, session):
        session.enter_quiz()
        assert session.is_in_quiz()
        assert session.state.status == SessionStatus.QUIZ

        session.exit_quiz()
        assert not session.is_in_quiz()
        assert session.state.status == SessionStatus.TEACHING

    def test_progress_text_with_plan(self, session):
        assert session.progress_text() == "Step 1/5"
        session.advance()
        assert session.progress_text() == "Step 2/5"

    def test_progress_text_without_plan(self, empty_session):
        assert empty_session.progress_text() == ""

    def test_is_in_quiz_false_initially(self, session):
        assert not session.is_in_quiz()

    def test_completed_list_tracks_progress(self, session):
        assert session.state.completed == []
        session.advance()
        assert 0 in session.state.completed
        session.advance()
        assert 1 in session.state.completed
        assert len(session.state.completed) == 2

    def test_multiple_advances(self, session):
        for i in range(3):
            assert session.advance() is True
        assert session.state.current_step == 3

    def test_current_step_updates_after_advance(self, session):
        first_step = session.current_step()
        assert first_step.index == 0

        session.advance()
        second_step = session.current_step()
        assert second_step.index == 1
        assert second_step.title == "Base Case"

    def test_session_with_no_steps(self):
        from groqmate.core.models import LessonPlan

        plan = LessonPlan(topic="Empty", steps=[])
        s = Session()
        s.load_plan(plan)
        assert s.current_step() is None

    def test_quiz_mode_independence(self, session):
        session.enter_quiz()
        session.exit_quiz()
        session.enter_quiz()
        assert session.is_in_quiz()
