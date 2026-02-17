import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from groqmate.interfaces.cli.app import GroqmateApp, run
from groqmate.core.providers import Provider
from groqmate.core.state import Session
from groqmate.core.models import LessonPlan, LessonStep


class TestGroqmateApp:
    def test_app_title(self):
        app = GroqmateApp()
        assert app.TITLE == "Groqmate"

    def test_bindings_exist(self):
        app = GroqmateApp()
        binding_actions = [b.action for b in app.BINDINGS]
        assert "quit" in binding_actions
        assert "clear" in binding_actions

    def test_init_with_provider(self):
        app = GroqmateApp(provider="gemini")
        assert app.provider_config.provider == Provider.GEMINI

    def test_init_with_custom_model(self):
        app = GroqmateApp(provider="groq", model="llama-3.1-8b-instant")
        assert app.provider_config.model == "llama-3.1-8b-instant"

    def test_default_provider_is_groq(self):
        app = GroqmateApp()
        assert app.provider_config.provider == Provider.GROQ

    def test_default_model_is_none(self):
        app = GroqmateApp()
        assert app.provider_config.model is None

    def test_session_initial_state(self):
        app = GroqmateApp()
        assert app.session.state.plan is None

    def test_is_processing_initially_false(self):
        app = GroqmateApp()
        assert app._is_processing is False

    def test_session_is_session_instance(self):
        app = GroqmateApp()
        assert isinstance(app.session, Session)


class TestAppMethods:
    def test_update_header_with_plan(self, sample_plan):
        app = GroqmateApp()
        app.session.load_plan(sample_plan)
        app._update_header()
        assert "Step 1/5" in app.title

    def test_update_header_without_plan(self):
        app = GroqmateApp()
        app._update_header()
        assert app.title == "Groqmate"

    def test_update_header_after_advance(self, sample_plan):
        app = GroqmateApp()
        app.session.load_plan(sample_plan)
        app.session.advance()
        app._update_header()
        assert "Step 2/5" in app.title

    def test_update_header_at_last_step(self, sample_plan):
        app = GroqmateApp()
        app.session.load_plan(sample_plan)
        for _ in range(4):
            app.session.advance()
        app._update_header()
        assert "Step 5/5" in app.title

    def test_action_clear_resets_session(self, sample_plan):
        app = GroqmateApp()
        app.session.load_plan(sample_plan)
        app.session.advance()
        app.session.reset()
        assert app.session.state.plan is None
        assert app.session.state.current_step == 0


class TestRunFunction:
    def test_run_creates_app_with_default_provider(self):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                provider="groq", model=None, list_providers=False
            )
            with patch.object(GroqmateApp, "run"):
                run()

    def test_run_with_custom_provider(self):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                provider="gemini", model=None, list_providers=False
            )
            with patch.object(GroqmateApp, "run"):
                run()

    def test_run_with_custom_model(self):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                provider="groq", model="custom-model", list_providers=False
            )
            with patch.object(GroqmateApp, "run"):
                run()

    def test_list_providers_calls_print(self):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                provider="groq", model=None, list_providers=True
            )
            with patch("builtins.print") as mock_print:
                run()
                assert mock_print.called

    def test_run_with_all_providers(self):
        providers = [
            "groq",
            "gemini",
            "openai",
            "deepseek",
            "openrouter",
            "ollama",
            "anthropic",
            "mistral",
        ]
        for provider in providers:
            with patch("argparse.ArgumentParser.parse_args") as mock_args:
                mock_args.return_value = MagicMock(
                    provider=provider, model=None, list_providers=False
                )
                with patch.object(GroqmateApp, "run"):
                    run()


class TestAppAttributes:
    def test_css_path(self):
        app = GroqmateApp()
        assert app.CSS_PATH == "style.tcss"

    def test_tutor_initially_none(self):
        app = GroqmateApp()
        assert app.tutor is None

    def test_provider_config_has_provider(self):
        app = GroqmateApp(provider="openai")
        assert app.provider_config.provider == Provider.OPENAI
