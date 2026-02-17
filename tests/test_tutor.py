import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from groqmate.core.tutor import (
    Tutor,
    SYSTEM_PROMPT,
    PLAN_PROMPT,
    EXPLAIN_PROMPT,
    REPHRASE_PROMPT,
    SUMMARY_PROMPT,
)
from groqmate.core.providers import ProviderConfig, Provider


class TestTutorInit:
    def test_init_with_config(self, provider_config_groq, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor(provider_config_groq)
        assert tutor.config == provider_config_groq
        assert tutor.model == "groq/llama-3.3-70b-versatile"

    def test_init_without_config_uses_default(self, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor()
        assert tutor.config.provider == Provider.GROQ

    def test_init_raises_without_api_key(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            Tutor(ProviderConfig(provider=Provider.GROQ))

    def test_init_ollama_no_key_needed(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        config = ProviderConfig(provider=Provider.OLLAMA)
        tutor = Tutor(config)
        assert tutor.config.is_local()

    def test_model_string_set_correctly(self, provider_config_gemini, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        tutor = Tutor(provider_config_gemini)
        assert tutor.model == "gemini/gemini-2.0-flash"


class TestGeneratePlan:
    @pytest.mark.asyncio
    async def test_returns_lesson_plan(
        self, provider_config_groq, mock_litellm_response, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        with patch("groqmate.core.tutor.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = mock_litellm_response
            tutor = Tutor(provider_config_groq)
            plan = await tutor.generate_plan("Recursion")

            assert plan.topic == "Test"
            assert len(plan.steps) == 1
            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_calls_with_correct_model(
        self, provider_config_groq, mock_litellm_response, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        with patch("groqmate.core.tutor.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = mock_litellm_response
            tutor = Tutor(provider_config_groq)
            await tutor.generate_plan("Test Topic")

            call_kwargs = mock.call_args[1]
            assert call_kwargs["model"] == "groq/llama-3.3-70b-versatile"

    @pytest.mark.asyncio
    async def test_includes_topic_in_prompt(
        self, provider_config_groq, mock_litellm_response, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        with patch("groqmate.core.tutor.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = mock_litellm_response
            tutor = Tutor(provider_config_groq)
            await tutor.generate_plan("Binary Search")

            messages = mock.call_args[1]["messages"]
            user_message = [m for m in messages if m["role"] == "user"][0]
            assert "Binary Search" in user_message["content"]

    @pytest.mark.asyncio
    async def test_requests_json_format(
        self, provider_config_groq, mock_litellm_response, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        with patch("groqmate.core.tutor.acompletion", new_callable=AsyncMock) as mock:
            mock.return_value = mock_litellm_response
            tutor = Tutor(provider_config_groq)
            await tutor.generate_plan("Test")

            assert mock.call_args[1]["response_format"] == {"type": "json_object"}

    @pytest.mark.asyncio
    async def test_raises_on_empty_response(self, provider_config_groq, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None

        with patch(
            "groqmate.core.tutor.acompletion",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            tutor = Tutor(provider_config_groq)
            with pytest.raises(ValueError, match="Empty response"):
                await tutor.generate_plan("Test")


class TestExplainStepStream:
    @pytest.mark.asyncio
    async def test_yields_tokens(
        self, session, provider_config_groq, mock_streaming_chunks, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")

        async def mock_stream(*args, **kwargs):
            for chunk in mock_streaming_chunks:
                yield chunk

        with patch("groqmate.core.tutor.acompletion", return_value=mock_stream()):
            tutor = Tutor(provider_config_groq)
            tokens = []
            async for token in tutor.explain_step_stream(session):
                tokens.append(token)

            assert tokens == ["Hello", " ", "World"]

    @pytest.mark.asyncio
    async def test_handles_no_session(
        self, empty_session, provider_config_groq, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor(provider_config_groq)
        tokens = []
        async for token in tutor.explain_step_stream(empty_session):
            tokens.append(token)

        assert "No active lesson" in tokens[0]

    @pytest.mark.asyncio
    async def test_uses_stream_mode(
        self, session, provider_config_groq, mock_streaming_chunks, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")

        async def mock_stream(*args, **kwargs):
            for chunk in mock_streaming_chunks:
                yield chunk

        with patch(
            "groqmate.core.tutor.acompletion", return_value=mock_stream()
        ) as mock:
            tutor = Tutor(provider_config_groq)
            async for _ in tutor.explain_step_stream(session):
                pass

            assert mock.call_args[1]["stream"] is True

    @pytest.mark.asyncio
    async def test_skips_none_content(
        self, session, provider_config_groq, mock_empty_streaming_chunks, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")

        async def mock_stream(*args, **kwargs):
            for chunk in mock_empty_streaming_chunks:
                yield chunk

        with patch("groqmate.core.tutor.acompletion", return_value=mock_stream()):
            tutor = Tutor(provider_config_groq)
            tokens = []
            async for token in tutor.explain_step_stream(session):
                tokens.append(token)

            assert tokens == []


class TestCheckAnswer:
    @pytest.mark.asyncio
    async def test_correct_answer(self, session, provider_config_groq, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor(provider_config_groq)
        correct, feedback = await tutor.check_answer("base case", session)

        assert correct is True
        assert "Correct" in feedback

    @pytest.mark.asyncio
    async def test_incorrect_answer(self, session, provider_config_groq, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor(provider_config_groq)
        correct, feedback = await tutor.check_answer("wrong answer", session)

        assert correct is False

    @pytest.mark.asyncio
    async def test_partial_match(self, session, provider_config_groq, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor(provider_config_groq)
        correct, feedback = await tutor.check_answer("the base case", session)

        assert correct is True

    @pytest.mark.asyncio
    async def test_handles_no_session(
        self, empty_session, provider_config_groq, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor(provider_config_groq)
        correct, feedback = await tutor.check_answer("test", empty_session)

        assert correct is False
        assert "No active lesson" in feedback

    @pytest.mark.asyncio
    async def test_close_answer(self, session, provider_config_groq, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor(provider_config_groq)
        correct, feedback = await tutor.check_answer("base", session)

        assert correct is True


class TestRephraseStream:
    @pytest.mark.asyncio
    async def test_yields_rephrased_content(
        self, session, provider_config_groq, mock_streaming_chunks, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")

        async def mock_stream(*args, **kwargs):
            for chunk in mock_streaming_chunks:
                yield chunk

        with patch("groqmate.core.tutor.acompletion", return_value=mock_stream()):
            tutor = Tutor(provider_config_groq)
            tokens = []
            async for token in tutor.rephrase_stream(session):
                tokens.append(token)

            assert len(tokens) > 0

    @pytest.mark.asyncio
    async def test_handles_no_session(
        self, empty_session, provider_config_groq, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor(provider_config_groq)
        tokens = []
        async for token in tutor.rephrase_stream(empty_session):
            tokens.append(token)

        assert "No active lesson" in tokens[0]

    @pytest.mark.asyncio
    async def test_uses_higher_temperature(
        self, session, provider_config_groq, mock_streaming_chunks, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")

        async def mock_stream(*args, **kwargs):
            for chunk in mock_streaming_chunks:
                yield chunk

        with patch(
            "groqmate.core.tutor.acompletion", return_value=mock_stream()
        ) as mock:
            tutor = Tutor(provider_config_groq)
            async for _ in tutor.rephrase_stream(session):
                pass

            assert mock.call_args[1]["temperature"] == 0.9


class TestGenerateSummary:
    @pytest.mark.asyncio
    async def test_returns_markdown(self, session, provider_config_groq, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "# Recursion Notes\n\n## Step 1\n..."

        with patch(
            "groqmate.core.tutor.acompletion",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            tutor = Tutor(provider_config_groq)
            summary = await tutor.generate_summary(session)

            assert "# Recursion Notes" in summary

    @pytest.mark.asyncio
    async def test_handles_no_session(
        self, empty_session, provider_config_groq, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        tutor = Tutor(provider_config_groq)
        summary = await tutor.generate_summary(empty_session)

        assert "No lesson" in summary

    @pytest.mark.asyncio
    async def test_handles_none_content(
        self, session, provider_config_groq, monkeypatch
    ):
        monkeypatch.setenv("GROQ_API_KEY", "test_key")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None

        with patch(
            "groqmate.core.tutor.acompletion",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            tutor = Tutor(provider_config_groq)
            summary = await tutor.generate_summary(session)

            assert "Error" in summary


class TestPrompts:
    def test_system_prompt_exists(self):
        assert len(SYSTEM_PROMPT) > 0
        assert "Groqmate" in SYSTEM_PROMPT
        assert "concise" in SYSTEM_PROMPT.lower()

    def test_system_prompt_has_rules(self):
        assert "ASCII" in SYSTEM_PROMPT
        assert "Unicode" in SYSTEM_PROMPT

    def test_plan_prompt_format(self):
        formatted = PLAN_PROMPT.format(topic="Recursion")
        assert "Recursion" in formatted
        assert "JSON" in formatted

    def test_plan_prompt_requests_five_steps(self):
        assert "5 steps" in PLAN_PROMPT

    def test_explain_prompt_format(self):
        formatted = EXPLAIN_PROMPT.format(
            topic="Recursion",
            step_num=1,
            step_title="Base Case",
            concept="The stopping condition",
            quiz_question="What stops recursion?",
        )
        assert "Base Case" in formatted
        assert "What stops recursion?" in formatted

    def test_explain_prompt_has_guidelines(self):
        assert "punchy explanation" in EXPLAIN_PROMPT
        assert "100 words" in EXPLAIN_PROMPT

    def test_rephrase_prompt_format(self):
        formatted = REPHRASE_PROMPT.format(
            topic="Recursion", concept="Function calls itself"
        )
        assert "Recursion" in formatted
        assert "different analogy" in formatted.lower()

    def test_rephrase_prompt_lists_analogies(self):
        assert "cooking" in REPHRASE_PROMPT
        assert "sports" in REPHRASE_PROMPT
        assert "gaming" in REPHRASE_PROMPT

    def test_summary_prompt_format(self):
        formatted = SUMMARY_PROMPT.format(
            topic="Recursion", steps="1. Intro: Basic concept"
        )
        assert "Recursion" in formatted
        assert "markdown" in formatted.lower()
