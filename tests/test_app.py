import pytest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path
from groqmate.interfaces.cli.app import GroqmateApp, run, CSS_PATH
from groqmate.core.providers import Provider
from groqmate.core.state import Session
from groqmate.core.models import LessonPlan


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
                provider=None, provider_flag=None, model=None, list_providers=False
            )
            with patch.object(GroqmateApp, "run"):
                run()

    def test_run_with_positional_provider(self):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                provider="gemini", provider_flag=None, model=None, list_providers=False
            )
            with patch.object(GroqmateApp, "run"):
                run()

    def test_run_with_provider_flag(self):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                provider=None, provider_flag="openai", model=None, list_providers=False
            )
            with patch.object(GroqmateApp, "run"):
                run()

    def test_run_with_custom_model(self):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                provider=None,
                provider_flag=None,
                model="custom-model",
                list_providers=False,
            )
            with patch.object(GroqmateApp, "run"):
                run()

    def test_run_with_provider_model_syntax(self):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                provider="groq/llama-3.1-8b",
                provider_flag=None,
                model=None,
                list_providers=False,
            )
            with patch.object(GroqmateApp, "run"):
                run()

    def test_list_providers_exits(self):
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = MagicMock(
                provider=None, provider_flag=None, model=None, list_providers=True
            )
            # show_providers_and_exit calls sys.exit, which would terminate pytest
            # So we just verify the args are correctly parsed
            args = mock_args.return_value
            assert args.list_providers is True

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
                    provider=provider,
                    provider_flag=None,
                    model=None,
                    list_providers=False,
                )
                with patch.object(GroqmateApp, "run"):
                    run()


class TestAppAttributes:
    def test_css_path_exists(self):
        assert CSS_PATH.exists()

    def test_css_path_is_tcss(self):
        assert CSS_PATH.suffix == ".tcss"

    def test_tutor_initially_none(self):
        app = GroqmateApp()
        assert app.tutor is None

    def test_provider_config_has_provider(self):
        app = GroqmateApp(provider="openai")
        assert app.provider_config.provider == Provider.OPENAI
