import asyncio
import argparse
from textual.app import App, ComposeResult
from textual.widgets import Header, Static
from textual.containers import Container
from textual.binding import Binding

from groqmate.core.tutor import Tutor
from groqmate.core.state import Session
from groqmate.core.providers import ProviderConfig, Provider, DEFAULTS
from groqmate.core.config import Config
from groqmate.interfaces.cli.widgets import ChatLog, InputBar, CustomFooter
from groqmate.interfaces.cli.settings_screen import SettingsScreen


class GroqmateApp(App):
    CSS_PATH = "style.tcss"
    TITLE = "Groqmate"
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("ctrl+l", "clear", "Clear", show=True),
        Binding("ctrl+p", "settings", "Settings", show=True),
    ]

    def __init__(self, provider: str | None = None, model: str | None = None):
        super().__init__()
        self.config = Config.load()

        provider_str = provider or self.config.settings.provider
        model_str = model or self.config.settings.model

        self.provider_config = ProviderConfig(
            provider=Provider(provider_str), model=model_str
        )
        self.tutor: Tutor | None = None
        self.session = Session()
        self._is_processing = False

    def on_mount(self) -> None:
        self._init_tutor()
        self.query_one(InputBar).focus_input()

    def _init_tutor(self) -> None:
        try:
            self.tutor = Tutor(self.provider_config, self.config)
            self._show_welcome()
        except ValueError as e:
            self._show_error(str(e))

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Container(
            ChatLog(),
        )
        yield InputBar()
        yield CustomFooter(provider=self.provider_config.provider.value)

    def _show_welcome(self) -> None:
        chat = self.query_one(ChatLog)
        provider_name = self.provider_config.provider.value.upper()
        model_name = self.provider_config.model or DEFAULTS.get(
            self.provider_config.provider, "default"
        )
        chat.add_message(
            "System",
            f"Welcome to Groqmate! Your learning coach.\n"
            f"Provider: {provider_name} | Model: {model_name}\n"
            f"Type 'teach me <topic>' to start a lesson.\n"
            f"Commands: next, wtf, summary, quit\n"
            f"Press Ctrl+P for settings.",
            is_system=True,
        )

    def _show_error(self, message: str) -> None:
        chat = self.query_one(ChatLog)
        chat.add_message(
            "System",
            f"Error: {message}\nPress Ctrl+P to configure your API key.",
            is_system=True,
        )

    def _update_header(self) -> None:
        progress = self.session.progress_text()
        if progress:
            self.title = f"Groqmate [{progress}]"
        else:
            self.title = "Groqmate"

    def action_settings(self) -> None:
        self.push_screen(SettingsScreen(self.config))

    def _on_settings_saved(self) -> None:
        self.config = Config.load()

        self.provider_config = ProviderConfig(
            provider=Provider(self.config.settings.provider),
            model=self.config.settings.model,
        )

        self._init_tutor()

        footer = self.query_one(CustomFooter)
        footer.update_provider(self.config.settings.provider)

        chat = self.query_one(ChatLog)
        chat.add_message(
            "System",
            f"Settings applied. Provider: {self.config.settings.provider.upper()}",
            is_system=True,
        )

    async def on_input_bar_submitted(self, message: InputBar.Submitted) -> None:
        if self._is_processing:
            return

        user_input = message.value.strip()
        if not user_input:
            return

        chat = self.query_one(ChatLog)
        chat.add_message("You", user_input, is_user=True)

        await self._handle_input(user_input)

    async def _handle_input(self, user_input: str) -> None:
        chat = self.query_one(ChatLog)
        lower_input = user_input.lower()

        if lower_input in ("quit", "exit", "q"):
            self.app.exit()
            return

        if lower_input in ("clear", "cls"):
            chat.clear_chat()
            self._show_welcome()
            return

        if lower_input in ("help", "?", "commands"):
            self._show_help()
            return

        if lower_input == "wtf":
            await self._handle_wtf()
            return

        if lower_input == "summary":
            await self._handle_summary()
            return

        if lower_input == "next":
            await self._handle_next()
            return

        if self.session.is_in_quiz():
            await self._handle_quiz_answer(user_input)
            return

        if lower_input.startswith("teach me "):
            topic = user_input[9:].strip()
            await self._start_lesson(topic)
            return

        chat.add_message(
            "System",
            "Unknown command. Type 'teach me <topic>' to start learning.",
            is_system=True,
        )

    def _show_help(self) -> None:
        chat = self.query_one(ChatLog)
        chat.add_message(
            "System",
            "Commands:\n"
            "  teach me <topic>  - Start a new lesson\n"
            "  next              - Move to next step\n"
            "  wtf               - Explain differently\n"
            "  summary           - Generate lesson notes\n"
            "  clear             - Clear chat\n"
            "  quit              - Exit",
            is_system=True,
        )

    async def _start_lesson(self, topic: str) -> None:
        if not self.tutor:
            return

        chat = self.query_one(ChatLog)
        self._is_processing = True

        msg = chat.add_message("Groqmate", "", is_streaming=True)
        chat.append_to_streaming(f"Generating lesson plan for: {topic}...")

        try:
            plan = await self.tutor.generate_plan(topic)
            self.session.load_plan(plan)
            self._update_header()

            chat.finalize_streaming()
            msg.remove()

            chat.add_message(
                "System",
                f"Lesson: {plan.topic} ({plan.total_steps} steps)",
                is_system=True,
            )

            await self._explain_current_step()

        except Exception as e:
            chat.finalize_streaming()
            msg.remove()
            chat.add_message("System", f"Error: {e}", is_system=True)

        self._is_processing = False

    async def _explain_current_step(self) -> None:
        if not self.tutor:
            return

        chat = self.query_one(ChatLog)

        msg = chat.add_message("Groqmate", "", is_streaming=True)

        try:
            async for token in self.tutor.explain_step_stream(self.session):
                chat.append_to_streaming(token)
                await asyncio.sleep(0)

            chat.finalize_streaming()
            self.session.enter_quiz()

        except Exception as e:
            chat.finalize_streaming()
            chat.append_to_streaming(f"\nError: {e}")

    async def _handle_quiz_answer(self, answer: str) -> None:
        if not self.tutor:
            return

        chat = self.query_one(ChatLog)

        correct, feedback = await self.tutor.check_answer(answer, self.session)

        if correct:
            chat.add_message("Groqmate", feedback, is_user=False)
            self.session.exit_quiz()
        else:
            chat.add_message("Groqmate", feedback, is_user=False)

    async def _handle_next(self) -> None:
        chat = self.query_one(ChatLog)

        if not self.session.state.plan:
            chat.add_message(
                "System",
                "No active lesson. Start with 'teach me <topic>'",
                is_system=True,
            )
            return

        if self.session.is_in_quiz():
            chat.add_message(
                "System",
                "Answer the quiz first to unlock the next step.",
                is_system=True,
            )
            return

        if self.session.is_complete():
            chat.add_message(
                "Groqmate",
                "Lesson complete! Type 'summary' to get your notes.",
                is_user=False,
            )
            return

        if self.session.advance():
            self._update_header()
            await self._explain_current_step()
        else:
            self._update_header()
            chat.add_message(
                "Groqmate",
                "Lesson complete! Type 'summary' to get your notes.",
                is_user=False,
            )

    async def _handle_wtf(self) -> None:
        if not self.tutor:
            return

        chat = self.query_one(ChatLog)

        if not self.session.state.plan:
            chat.add_message("System", "No active lesson to rephrase.", is_system=True)
            return

        msg = chat.add_message("Groqmate", "", is_streaming=True)

        try:
            async for token in self.tutor.rephrase_stream(self.session):
                chat.append_to_streaming(token)
                await asyncio.sleep(0)

            chat.finalize_streaming()

        except Exception as e:
            chat.finalize_streaming()
            chat.append_to_streaming(f"\nError: {e}")

    async def _handle_summary(self) -> None:
        if not self.tutor:
            return

        chat = self.query_one(ChatLog)

        if not self.session.state.plan:
            chat.add_message("System", "No lesson to summarize.", is_system=True)
            return

        chat.add_message("System", "Generating summary...", is_system=True)

        try:
            summary = await self.tutor.generate_summary(self.session)

            topic_slug = self.session.state.plan.topic.lower().replace(" ", "_")
            filename = f"{topic_slug}_notes.md"

            with open(filename, "w") as f:
                f.write(summary)

            chat.add_message("System", f"Summary saved to {filename}", is_system=True)
            chat.add_message("Groqmate", summary, is_user=False)

        except Exception as e:
            chat.add_message("System", f"Error: {e}", is_system=True)

    def action_clear(self) -> None:
        chat = self.query_one(ChatLog)
        chat.clear_chat()
        self.session.reset()
        self._update_header()
        self._show_welcome()


def run():
    parser = argparse.ArgumentParser(
        description="Groqmate - Interactive CLI learning coach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  groqmate                           # Use default from config or Groq
  groqmate -p gemini                 # Use Gemini
  groqmate -p openai -m gpt-4o-mini  # Use specific model
  groqmate -p ollama                 # Use local Ollama

Supported providers: groq, gemini, openai, deepseek, openrouter, ollama, anthropic, mistral
        """,
    )
    parser.add_argument(
        "--provider",
        "-p",
        choices=[
            "groq",
            "gemini",
            "openai",
            "deepseek",
            "openrouter",
            "ollama",
            "anthropic",
            "mistral",
        ],
        default=None,
        help="LLM provider to use (overrides config)",
    )
    parser.add_argument(
        "--model", "-m", help="Specific model to use (overrides config)"
    )
    parser.add_argument(
        "--list-providers",
        "-l",
        action="store_true",
        help="List available providers and their default models",
    )

    args = parser.parse_args()

    if args.list_providers:
        print("Available providers and default models:\n")
        for provider in Provider:
            default = DEFAULTS.get(provider, "N/A")
            local = "(local)" if provider == Provider.OLLAMA else ""
            print(f"  {provider.value:12} {default:30} {local}")
        print()
        return

    app = GroqmateApp(provider=args.provider, model=args.model)
    app.run()


if __name__ == "__main__":
    run()
