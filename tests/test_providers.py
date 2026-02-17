import pytest
from groqmate.core.providers import Provider, ProviderConfig


class TestProvider:
    def test_all_providers_exist(self):
        assert Provider.GROQ.value == "groq"
        assert Provider.GEMINI.value == "gemini"
        assert Provider.OPENAI.value == "openai"
        assert Provider.DEEPSEEK.value == "deepseek"
        assert Provider.OPENROUTER.value == "openrouter"
        assert Provider.OLLAMA.value == "ollama"
        assert Provider.ANTHROPIC.value == "anthropic"
        assert Provider.MISTRAL.value == "mistral"

    def test_provider_is_string_enum(self):
        assert Provider.GROQ == "groq"
        assert isinstance(Provider.GROQ, str)

    def test_provider_can_be_compared(self):
        assert Provider.GROQ == Provider.GROQ
        assert Provider.GROQ != Provider.GEMINI

    def test_provider_count(self):
        assert len(list(Provider)) == 8


class TestProviderConfig:
    def test_default_is_groq(self):
        config = ProviderConfig()
        assert config.provider == Provider.GROQ

    def test_custom_provider(self, provider_config_gemini):
        assert provider_config_gemini.provider == Provider.GEMINI
        assert provider_config_gemini.model == "gemini-2.0-flash"

    def test_model_string_format_groq(self, provider_config_groq):
        assert provider_config_groq.get_model_string() == "groq/llama-3.3-70b-versatile"

    def test_model_string_format_gemini(self, provider_config_gemini):
        assert provider_config_gemini.get_model_string() == "gemini/gemini-2.0-flash"

    def test_model_string_custom_model(self):
        config = ProviderConfig(provider=Provider.OPENAI, model="gpt-4")
        assert config.get_model_string() == "openai/gpt-4"

    def test_model_string_uses_default_when_none(self):
        config = ProviderConfig(provider=Provider.DEEPSEEK)
        assert config.get_model_string() == "deepseek/deepseek-chat"

    def test_get_env_key_groq(self, provider_config_groq):
        assert provider_config_groq.get_env_key() == "GROQ_API_KEY"

    def test_get_env_key_gemini(self, provider_config_gemini):
        assert provider_config_gemini.get_env_key() == "GEMINI_API_KEY"

    def test_get_env_key_all_providers(self):
        env_keys = {
            Provider.GROQ: "GROQ_API_KEY",
            Provider.GEMINI: "GEMINI_API_KEY",
            Provider.OPENAI: "OPENAI_API_KEY",
            Provider.DEEPSEEK: "DEEPSEEK_API_KEY",
            Provider.OPENROUTER: "OPENROUTER_API_KEY",
            Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
            Provider.MISTRAL: "MISTRAL_API_KEY",
        }
        for provider, expected_key in env_keys.items():
            config = ProviderConfig(provider=provider)
            assert config.get_env_key() == expected_key

    def test_is_local_ollama(self):
        config = ProviderConfig(provider=Provider.OLLAMA)
        assert config.is_local() is True

    def test_is_local_not_ollama(self, provider_config_groq):
        assert provider_config_groq.is_local() is False

    def test_is_local_gemini(self, provider_config_gemini):
        assert provider_config_gemini.is_local() is False

    def test_defaults_exist_for_all_providers(self):
        for provider in Provider:
            assert provider in ProviderConfig.DEFAULTS
            assert ProviderConfig.DEFAULTS[provider] is not None
            assert len(ProviderConfig.DEFAULTS[provider]) > 0

    def test_env_keys_exist_for_most_providers(self):
        for provider in Provider:
            if provider != Provider.OLLAMA:
                assert provider in ProviderConfig.ENV_KEYS

    def test_ollama_has_no_env_key(self):
        config = ProviderConfig(provider=Provider.OLLAMA)
        assert config.get_env_key() == ""

    def test_model_override(self):
        config = ProviderConfig(provider=Provider.GROQ, model="custom-model")
        assert config.model == "custom-model"
        assert config.get_model_string() == "groq/custom-model"

    def test_config_is_pydantic_model(self):
        config = ProviderConfig()
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")

    def test_config_serialization(self, provider_config_groq):
        data = provider_config_groq.model_dump()
        assert data["provider"] == Provider.GROQ
        assert "model" in data
