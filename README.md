# Groqmate

An interactive CLI learning coach powered by LLMs. Think of it as a gym coach for your brain — it spots you, challenges you, and waits for you to lift the weight.

## What makes it different?

| ChatGPT | Groqmate |
|---------|----------|
| Professor delivering a lecture | Pair programmer / gym coach |
| Passive consumption | Active learning |
| Wall of text | Atomic, bite-sized chunks |
| No friction | Quiz locks between concepts |

## Features

- **Hidden Curriculum:** AI generates a 5-step plan before teaching — you see progress, not a lecture
- **Quiz Lock:** Must answer correctly to unlock the next concept
- **`wtf` Command:** Stuck? Type `wtf` and get a fresh analogy
- **Flashcard Mode:** Session ends with a `<topic>_notes.md` summary
- **Terminal-native:** ASCII graphs, Unicode math, no heavy browser UI
- **Streaming:** Token-by-token responses for a real-time feel
- **Multi-provider:** Works with Groq, Gemini, OpenAI, DeepSeek, Ollama, and more

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install groqmate globally
uv tool install groqmate

# Or install from source
git clone https://github.com/yourname/groqmate.git
cd groqmate
uv tool install .
```

## Quick Start

```bash
# Set your API key (pick one provider)
export GROQ_API_KEY=your_key_here      # Groq (free tier)
# export GEMINI_API_KEY=your_key_here  # Gemini (free tier)

# Run
groqmate
```

## Free Provider Setup

Groqmate works with multiple LLM providers. Here's how to set up free options:

### Option 1: Groq (Recommended)

**Free tier:** Yes, generous rate limits

```bash
# 1. Go to https://console.groq.com/
# 2. Sign up / log in
# 3. Create an API key
# 4. Export it:
export GROQ_API_KEY=gsk_xxx...

# 5. Run groqmate (uses Groq by default)
groqmate
```

### Option 2: Google Gemini

**Free tier:** Yes, via Google AI Studio

```bash
# 1. Go to https://aistudio.google.com/
# 2. Create an API key
# 3. Export it:
export GEMINI_API_KEY=AIza...

# 4. Run with Gemini provider
groqmate -p gemini
```

### Option 3: DeepSeek

**Cost:** Very cheap (~$0.55 per 1M tokens)

```bash
# 1. Go to https://platform.deepseek.com/
# 2. Create an account and API key
# 3. Export it:
export DEEPSEEK_API_KEY=sk-...

# 4. Run with DeepSeek provider
groqmate -p deepseek
```

### Option 4: Ollama (Local, No API Key)

**Cost:** Free, runs locally

```bash
# 1. Install Ollama: https://ollama.ai/
# 2. Pull a model:
ollama pull llama3.2

# 3. Run groqmate with Ollama (no API key needed)
groqmate -p ollama
```

### Option 5: OpenRouter

**Free tier:** 100 requests/day

```bash
# 1. Go to https://openrouter.ai/
# 2. Create an account and API key
# 3. Export it:
export OPENROUTER_API_KEY=sk-or-...

# 4. Run with OpenRouter
groqmate -p openrouter
```

## Usage

### Starting a Lesson

```
You: teach me recursion

Groqmate: [Step 1 of 5: Self-Reference]
          A recursive function calls itself...
          
          ❓ Quiz: What must every recursive function have?

You: a base case

Groqmate: ✅ Correct! Type `next` to continue.

You: next

Groqmate: [Step 2 of 5: The Base Case]
          The base case is the condition that stops...
```

### Commands

| Command | Description |
|---------|-------------|
| `teach me <topic>` | Start a new lesson on any topic |
| `next` | Move to the next step (after passing quiz) |
| `wtf` | Get a different analogy (stuck? use this) |
| `summary` | Generate markdown notes for the lesson |
| `clear` | Clear chat and start fresh |
| `help` | Show available commands |
| `quit` | Exit the app |

### CLI Options

```bash
# Use a specific provider
groqmate -p gemini
groqmate -p openai
groqmate -p deepseek
groqmate -p ollama

# Use a specific model
groqmate -p groq -m llama-3.1-8b-instant
groqmate -p openai -m gpt-4o-mini

# List all providers and their default models
groqmate --list-providers
```

## Development

```bash
# Clone the repo
git clone https://github.com/yourname/groqmate.git
cd groqmate

# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/groqmate --cov-report=term-missing

# Run the app locally
uv run groqmate

# Format/lint (if configured)
uv run ruff check .
uv run ruff format .
```

## Project Structure

```
groqmate/
├── src/groqmate/
│   ├── core/
│   │   ├── models.py       # Pydantic data models
│   │   ├── state.py        # Session state machine
│   │   ├── providers.py    # Multi-provider config
│   │   └── tutor.py        # LLM integration (LiteLLM)
│   └── interfaces/
│       └── cli/
│           ├── app.py      # Main Textual app
│           ├── widgets.py  # UI components
│           └── style.tcss  # Dark theme
├── tests/
│   ├── conftest.py         # Test fixtures
│   ├── test_models.py
│   ├── test_state.py
│   ├── test_providers.py
│   ├── test_tutor.py
│   ├── test_widgets.py
│   └── test_app.py
├── pyproject.toml
├── uv.lock
├── .python-version
└── README.md
```

## Supported Providers

| Provider | Env Variable | Free Tier | Notes |
|----------|-------------|-----------|-------|
| Groq | `GROQ_API_KEY` | ✅ Yes | Fast inference, recommended |
| Gemini | `GEMINI_API_KEY` | ✅ Yes | Via Google AI Studio |
| DeepSeek | `DEEPSEEK_API_KEY` | Cheap | ~$0.55/1M tokens |
| OpenRouter | `OPENROUTER_API_KEY` | 100/day | Routes to many models |
| Ollama | None needed | ✅ Free | Runs locally |
| OpenAI | `OPENAI_API_KEY` | No | GPT models |
| Anthropic | `ANTHROPIC_API_KEY` | No | Claude models |
| Mistral | `MISTRAL_API_KEY` | No | Mistral models |

## License

MIT
