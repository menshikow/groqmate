# Groqmate Implementation Plan

## Overview

Groqmate is a CLI-based learning coach that uses LiteLLM to teach topics through atomic, quiz-locked steps. Supports multiple LLM providers (Groq, Gemini, OpenAI, DeepSeek, Ollama, etc.). The UI is inspired by OpenCode — full-screen chat interface with streaming responses.

## Requirements

- Python 3.12+
- uv package manager

## Architecture

```
┌─────────────────────────────────────────────┐
│                   CLI Layer                  │
│  ┌─────────────────────────────────────┐    │
│  │           Textual App               │    │
│  │  ┌─────────────────────────────┐    │    │
│  │  │         ChatLog             │    │    │
│  │  │  (scrollable messages)      │    │    │
│  │  └─────────────────────────────┘    │    │
│  │  ┌─────────────────────────────┐    │    │
│  │  │         InputBar            │    │    │
│  │  └─────────────────────────────┘    │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│                 Core Layer                   │
│  ┌───────────┐  ┌───────────┐  ┌─────────┐  │
│  │  Session  │  │   Tutor   │  │ Models  │  │
│  │  (state)  │  │  (LiteLLM)│  │(Pydantic)│ │
│  └───────────┘  └───────────┘  └─────────┘  │
│  ┌───────────────────────────────────────┐  │
│  │         ProviderConfig                │  │
│  │  (groq, gemini, openai, deepseek,     │  │
│  │   openrouter, ollama, anthropic,      │  │
│  │   mistral)                            │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│               External Services              │
│    LiteLLM → Groq / Gemini / OpenAI / ...   │
└─────────────────────────────────────────────┘
```

## Data Models

### SessionStatus
```python
class SessionStatus(str, Enum):
    IDLE       # No active lesson
    PLANNING   # Generating lesson plan
    TEACHING   # Showing content
    QUIZ       # Waiting for answer
    COMPLETE   # Lesson finished
```

### LessonStep
```python
class LessonStep(BaseModel):
    index: int           # Step number (0-4)
    title: str           # Short title
    concept: str         # Core explanation
    quiz_question: str   # Question to test understanding
    quiz_answer: str     # Expected answer
```

### LessonPlan
```python
class LessonPlan(BaseModel):
    topic: str               # e.g., "Recursion"
    steps: List[LessonStep]  # 5 atomic steps
```

### SessionState
```python
class SessionState(BaseModel):
    plan: Optional[LessonPlan]
    current_step: int
    completed: List[int]
    status: SessionStatus
```

## Provider System

### Provider Enum
```python
class Provider(str, Enum):
    GROQ = "groq"
    GEMINI = "gemini"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
```

### ProviderConfig
```python
class ProviderConfig(BaseModel):
    provider: Provider = Provider.GROQ
    model: Optional[str] = None
    
    # Defaults map provider → default model
    # ENV_KEYS map provider → env variable name
    
    def get_model_string(self) -> str:
        # Returns "provider/model" for LiteLLM
        
    def is_local(self) -> bool:
        # True for Ollama (no API key needed)
```

### Default Models

| Provider | Default Model |
|----------|---------------|
| Groq | llama-3.3-70b-versatile |
| Gemini | gemini-2.0-flash |
| OpenAI | gpt-4o-mini |
| DeepSeek | deepseek-chat |
| OpenRouter | openrouter/auto |
| Ollama | llama3.2 |
| Anthropic | claude-3-5-haiku-20241022 |
| Mistral | mistral-small-latest |

## State Machine

```
         ┌──────────┐
         │   IDLE   │
         └────┬─────┘
              │ "teach me X"
              ▼
         ┌──────────┐
         │ PLANNING │
         └────┬─────┘
              │ plan generated
              ▼
         ┌──────────┐
    ┌───►│ TEACHING │◄──────┐
    │    └────┬─────┘       │
    │         │ show step   │
    │         ▼             │
    │    ┌──────────┐       │
    │    │   QUIZ   │───────┘
    │    └────┬─────┘ answer wrong
    │         │ answer correct
    │         ▼
    │    ┌──────────┐
    │    │  "next"  │
    │    └────┬─────┘
    │         │ more steps?
    └─────────┘
              │ no
              ▼
         ┌──────────┐
         │ COMPLETE │
         └──────────┘
```

## Tutor API

### Methods

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `generate_plan` | topic: str | LessonPlan | Creates 5-step curriculum |
| `explain_step_stream` | session | AsyncIterator[str] | Streams explanation + quiz |
| `check_answer` | answer, session | (bool, str) | Validates quiz answer |
| `rephrase_stream` | session | AsyncIterator[str] | New analogy for stuck users |
| `generate_summary` | session | str | Markdown notes for review |

### Prompts

**SYSTEM_PROMPT:** Defines Groqmate personality (terse, encouraging, hacker-ish)

**PLAN_PROMPT:** Forces JSON output with 5 atomic steps

**EXPLAIN_PROMPT:** Generates concise explanation + embedded quiz

**REPHRASE_PROMPT:** Requests alternative analogy (cooking, sports, gaming, etc.)

**SUMMARY_PROMPT:** Compiles lesson into scannable markdown

## CLI Components

### ChatLog (ScrollableContainer)
- Holds ChatMessage widgets
- `add_message()` — adds new message
- `append_to_streaming()` — updates streaming message
- `finalize_streaming()` — marks message complete
- Auto-scrolls to bottom

### ChatMessage (Static)
- Renders with sender prefix ("You:", "Groqmate:", "System:")
- Different colors per sender
- Streaming indicator (▏) when active
- Reactive content updates

### InputBar (Container)
- Fixed at bottom
- Single Input widget
- Emits `Submitted` message on Enter

### GroqmateApp (App)
- Main application class
- Accepts `provider` and `model` CLI args
- Handles command routing
- Manages session state
- Coordinates streaming updates

## Commands

| Command | Handler | Action |
|---------|---------|--------|
| `teach me <topic>` | `_start_lesson()` | Generate plan, show step 1 |
| `next` | `_handle_next()` | Advance if quiz passed |
| `wtf` | `_handle_wtf()` | Stream rephrased explanation |
| `summary` | `_handle_summary()` | Generate and save markdown |
| `clear` | `action_clear()` | Reset session, clear UI |
| `quit` | `exit()` | Exit app |

## CLI Arguments

```bash
groqmate                    # Default: Groq provider
groqmate -p gemini          # Use Gemini
groqmate -p ollama          # Use local Ollama
groqmate -p groq -m llama-3.1-8b-instant  # Custom model
groqmate --list-providers   # Show all providers
```

## Styling (TCSS)

Dark theme inspired by OpenCode:

| Element | Color |
|---------|-------|
| Background | #0d0d0d |
| Panel | #1a1a1a |
| Text | #e0e0e0 |
| AI messages | #00ff88 (green) |
| User messages | #e0e0e0 (white) |
| System messages | #ffcc00 (yellow) |
| Accent | #ff6b35 (orange) |

## File Structure

```
groqmate/
├── src/groqmate/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py       # Pydantic models
│   │   ├── state.py        # Session class
│   │   ├── providers.py    # Multi-provider config
│   │   └── tutor.py        # LiteLLM integration
│   └── interfaces/
│       └── cli/
│           ├── __init__.py
│           ├── app.py      # Main app + CLI args
│           ├── widgets.py  # UI components
│           └── style.tcss  # Theme
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Fixtures
│   ├── test_models.py      # 100% coverage
│   ├── test_state.py       # 100% coverage
│   ├── test_providers.py   # 100% coverage
│   ├── test_tutor.py       # 93% coverage
│   ├── test_widgets.py     # 75% coverage
│   └── test_app.py         # 91% coverage
├── pyproject.toml          # Hatchling build
├── uv.lock                 # Lockfile (commit this)
├── .python-version         # 3.12
├── .env.example            # API key templates
├── README.md
└── IMPLEMENTATION.md
```

## Development Commands

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/groqmate --cov-report=term-missing

# Run the app
uv run groqmate

# Install globally
uv tool install .
```

## Test Coverage

| Module | Coverage |
|--------|----------|
| core/models.py | 100% |
| core/providers.py | 100% |
| core/state.py | 100% |
| core/tutor.py | 93% |
| interfaces/cli/app.py | 91% |
| interfaces/cli/widgets.py | 75% |
| **Total** | **90%** |

## Acceptance Test: "The Recursion Test"

1. Run `uv run groqmate`
2. Type: `teach me recursion`
3. ✅ Shows "Step 1 of 5" in header
4. ✅ Streams explanation with quiz
5. ✅ Correct answer unlocks `next`
6. ✅ `next` advances to Step 2
7. ✅ `wtf` gives different analogy
8. ✅ `summary` generates markdown file
9. ✅ `quit` exits cleanly

## Completed Enhancements

- [x] Multiple LLM providers (Groq, Gemini, OpenAI, DeepSeek, OpenRouter, Ollama, Anthropic, Mistral)
- [x] Free provider support with setup instructions
- [x] 90%+ test coverage
- [x] uv package manager support

## Future Enhancements

- [ ] Multiple choice quizzes (a/b/c/d)
- [ ] Code execution for programming topics
- [ ] Progress persistence across sessions
- [ ] Spaced repetition reminders
- [ ] Export to Anki flashcard format
- [ ] Configuration file (~/.groqmate/config.toml)
