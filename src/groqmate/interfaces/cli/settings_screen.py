from textual.screen import ModalScreen
from textual.widgets import (
    Static,
    Input,
    Button,
    Select,
    Label,
)
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.binding import Binding
from textual.reactive import reactive
from groqmate.core.config import Config
from groqmate.core.providers import Provider, DEFAULTS


class SettingsScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close"),
    ]

    CSS = """
    SettingsScreen {
        align: center middle;
    }
    
    SettingsScreen > Container {
        width: 70;
        height: auto;
        max-height: 90%;
        background: #0a0a0a;
        border: thick #1a1a1a;
        padding: 1 2;
    }
    
    .title {
        text-style: bold;
        color: #ff6b35;
        text-align: center;
        margin-bottom: 1;
    }
    
    .section-label {
        color: #666666;
        margin-top: 1;
        margin-bottom: 0;
    }
    
    .setting-row {
        height: auto;
        margin-bottom: 1;
    }
    
    .setting-label {
        width: 12;
        color: #e0e0e0;
    }
    
    .setting-input {
        width: 1fr;
    }
    
    .api-key-row {
        height: auto;
        margin-bottom: 0;
    }
    
    .api-key-label {
        width: 12;
        color: #e0e0e0;
    }
    
    .api-key-input {
        width: 1fr;
    }
    
    .show-btn {
        width: 8;
        min-width: 8;
    }
    
    .buttons {
        align: center middle;
        height: auto;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
        min-width: 12;
    }
    
    .hint {
        color: #666666;
        text-align: center;
        margin-top: 1;
    }
    """

    show_keys: reactive[set] = reactive(set)

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self._original_config = config.model_dump()

    def compose(self):
        yield Container(
            Static("Settings", classes="title"),
            Label("Provider", classes="section-label"),
            Horizontal(
                Label("Provider:", classes="setting-label"),
                Select(
                    options=[(p.value.upper(), p.value) for p in Provider],
                    value=self.config.settings.provider,
                    id="provider-select",
                    classes="setting-input",
                ),
                classes="setting-row",
            ),
            Horizontal(
                Label("Model:", classes="setting-label"),
                Input(
                    value=self.config.settings.model or "",
                    placeholder=f"Default: {DEFAULTS.get(Provider(self.config.settings.provider), 'auto')}",
                    id="model-input",
                    classes="setting-input",
                ),
                classes="setting-row",
            ),
            Label("API Keys", classes="section-label"),
            *self._compose_api_key_rows(),
            Static("Changes apply immediately", classes="hint"),
            Horizontal(
                Button("Cancel", id="cancel-btn", variant="default"),
                Button("Save", id="save-btn", variant="primary"),
                classes="buttons",
            ),
        )

    def _compose_api_key_rows(self):
        providers_with_keys = [
            "groq",
            "gemini",
            "openai",
            "deepseek",
            "openrouter",
            "anthropic",
            "mistral",
        ]
        rows = []

        for provider in providers_with_keys:
            current_key = getattr(self.config.api_keys, provider, None) or ""
            is_visible = provider in self.show_keys

            rows.append(
                Horizontal(
                    Label(f"{provider.upper()}:", classes="api-key-label"),
                    Input(
                        value=current_key,
                        placeholder=f"Enter {provider.upper()} API key...",
                        password=not is_visible,
                        id=f"key-{provider}",
                        classes="api-key-input",
                    ),
                    Button(
                        "Hide" if is_visible else "Show",
                        id=f"toggle-{provider}",
                        classes="show-btn",
                    ),
                    classes="api-key-row",
                )
            )

        return rows

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self._save_settings()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "provider-select":
            self.config.settings.provider = event.value
            model_input = self.query_one("#model-input", Input)
            default_model = DEFAULTS.get(Provider(event.value), "auto")
            model_input.placeholder = f"Default: {default_model}"

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "model-input":
            self.config.settings.model = event.value or None
        elif event.input.id and event.input.id.startswith("key-"):
            provider = event.input.id.replace("key-", "")
            self.config.set_api_key(provider, event.value)

    def on_button_pressed_toggle(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id and button_id.startswith("toggle-"):
            provider = button_id.replace("toggle-", "")

            if provider in self.show_keys:
                self.show_keys = self.show_keys - {provider}
                event.button.label = "Show"
            else:
                self.show_keys = self.show_keys | {provider}
                event.button.label = "Hide"

            key_input = self.query_one(f"#key-{provider}", Input)
            key_input.password = provider not in self.show_keys

    def _save_settings(self) -> None:
        self.config.save()
        self.app.pop_screen()
        if hasattr(self.app, "_on_settings_saved"):
            self.app._on_settings_saved()
