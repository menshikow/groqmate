from enum import Enum
from pydantic import BaseModel
from typing import Optional, ClassVar


class Provider(str, Enum):
    GROQ = "groq"
    GEMINI = "gemini"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"


DEFAULTS: dict = {
    Provider.GROQ: "llama-3.3-70b-versatile",
    Provider.GEMINI: "gemini-2.0-flash",
    Provider.OPENAI: "gpt-4o-mini",
    Provider.DEEPSEEK: "deepseek-chat",
    Provider.OPENROUTER: "openrouter/auto",
    Provider.OLLAMA: "llama3.2",
    Provider.ANTHROPIC: "claude-3-5-haiku-20241022",
    Provider.MISTRAL: "mistral-small-latest",
}

ENV_KEYS: dict = {
    Provider.GROQ: "GROQ_API_KEY",
    Provider.GEMINI: "GEMINI_API_KEY",
    Provider.OPENAI: "OPENAI_API_KEY",
    Provider.DEEPSEEK: "DEEPSEEK_API_KEY",
    Provider.OPENROUTER: "OPENROUTER_API_KEY",
    Provider.ANTHROPIC: "ANTHROPIC_API_KEY",
    Provider.MISTRAL: "MISTRAL_API_KEY",
}


class ProviderConfig(BaseModel):
    provider: Provider = Provider.GROQ
    model: Optional[str] = None

    DEFAULTS: ClassVar[dict] = DEFAULTS
    ENV_KEYS: ClassVar[dict] = ENV_KEYS

    def get_model_string(self) -> str:
        model = self.model or DEFAULTS.get(self.provider)
        return f"{self.provider.value}/{model}"

    def get_env_key(self) -> str:
        return ENV_KEYS.get(self.provider, "")

    def is_local(self) -> bool:
        return self.provider == Provider.OLLAMA
