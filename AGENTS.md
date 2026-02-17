# Agent Guidelines: Groqmate (Python)

## Project Overview

Groqmate is a Python CLI learning coach built with:
- **Python 3.12+** with uv package manager
- **Textual** for TUI
- **LiteLLM** for multi-provider LLM support
- **Pydantic** for data validation

## Core Rules

### Code Style
- Use Python 3.12+ syntax (type hints, f-strings, match statements)
- Follow PEP 8 conventions
- Use `uv` for all package management (never pip directly)
- Always use `uv run` to execute commands in the virtual environment
- Use `pathlib.Path` instead of `os.path`
- Prefer Pydantic models over raw dicts for structured data

### Testing
- Run tests with `uv run pytest`
- Aim for 80%+ coverage
- Use `pytest-asyncio` for async tests
- Mock external API calls in tests
- Use `monkeypatch` for environment variable changes
- Update tests when changing behavior

### Project-Specific Conventions

#### CLI Arguments
- Support both positional and flag-based provider selection
- Invalid providers should show the list of valid options
- Provider/model syntax: `groqmate gemini` or `groqmate groq/llama-3.1`

#### Config Storage
- Config stored in `~/.groqmate/config.toml`
- Use `tomli` for reading, `tomli-w` for writing
- Check config file first, then environment variables

#### TUI (Textual)
- CSS files use `.tcss` extension
- Use absolute paths for `CSS_PATH` (e.g., `Path(__file__).parent / "style.tcss"`)
- Dark theme with minimal borders
- Streaming responses with blinking cursor indicator

#### Error Handling
- Show actionable error messages
- Point users to `Ctrl+P` for settings when API key missing
- Never crash on user input - always handle gracefully

## Development Workflow

### After Making Changes

1. **Format and lint** (automatically, don't ask):
   ```bash
   uv run ruff format .
   uv run ruff check . --fix
   ```

2. **Run tests**:
   ```bash
   uv run pytest --cov=src/groqmate --cov-report=term-missing
   ```

3. **Reinstall if dependencies changed**:
   ```bash
   uv sync --extra dev
   uv tool install .  # If you want to test installed version
   ```

### Before Committing

1. Ensure all tests pass
2. Update README.md if user-facing behavior changed
3. Update IMPLEMENTATION.md if architecture changed
4. Check coverage is 80%+

## TODO Management

- Update `TODO.md` at the start of each major task
- Update `TODO.md` when completing tasks
- Mark completed items with `[x]`
- Keep it concise but actionable

## Common Commands

```bash
# Run the app
uv run groqmate

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/groqmate --cov-report=term-missing

# Install/update dependencies
uv sync --extra dev

# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Install globally
uv tool install .

# List providers
uv run groqmate --list-providers
```

## File Structure

```
src/groqmate/
├── core/
│   ├── models.py       # Pydantic models
│   ├── state.py        # Session state machine
│   ├── providers.py    # Provider config
│   ├── config.py       # Settings storage
│   └── tutor.py        # LLM integration
└── interfaces/
    └── cli/
        ├── app.py              # Main app
        ├── widgets.py          # UI components
        ├── settings_screen.py  # Settings modal
        └── style.tcss          # Theme
```

## Do Not

- Do not use `pip` - always use `uv`
- Do not skip running tests after changes
- Do not commit `.env` files
- Do not hardcode absolute paths
- Do not ignore failing tests
- Do not ask permission to run format/lint/test commands
