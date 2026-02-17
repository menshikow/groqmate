from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import tomllib
import tomli_w
import os

CONFIG_DIR = Path.home() / ".groqmate"
CONFIG_PATH = CONFIG_DIR / "config.toml"


class Settings(BaseModel):
    provider: str = "groq"
    model: Optional[str] = None


class ApiKeys(BaseModel):
    groq: Optional[str] = None
    gemini: Optional[str] = None
    openai: Optional[str] = None
    deepseek: Optional[str] = None
    openrouter: Optional[str] = None
    anthropic: Optional[str] = None
    mistral: Optional[str] = None


class Config(BaseModel):
    settings: Settings = Settings()
    api_keys: ApiKeys = ApiKeys()

    @classmethod
    def load(cls) -> "Config":
        if not CONFIG_PATH.exists():
            return cls()

        try:
            with open(CONFIG_PATH, "rb") as f:
                data = tomllib.load(f)

            settings = Settings(**data.get("settings", {}))
            api_keys = ApiKeys(**data.get("api_keys", {}))
            return cls(settings=settings, api_keys=api_keys)
        except Exception:
            return cls()

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        data = {
            "settings": self.settings.model_dump(exclude_none=True),
            "api_keys": self.api_keys.model_dump(exclude_none=True),
        }

        with open(CONFIG_PATH, "wb") as f:
            tomli_w.dump(data, f)

    def get_api_key(self, provider: str) -> Optional[str]:
        provider_lower = provider.lower()
        key = getattr(self.api_keys, provider_lower, None)
        if key:
            return key

        env_mapping = {
            "groq": "GROQ_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "mistral": "MISTRAL_API_KEY",
        }

        env_var = env_mapping.get(provider_lower)
        if env_var:
            return os.getenv(env_var)

        return None

    def set_api_key(self, provider: str, key: str) -> None:
        provider_lower = provider.lower()
        if hasattr(self.api_keys, provider_lower):
            setattr(self.api_keys, provider_lower, key if key else None)
