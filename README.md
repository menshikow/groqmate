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
- **Built-in Settings:** Press `Ctrl+P` to configure providers and API keys

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
# Run groqmate
groqmate

# On first run, press Ctrl+P to open settings
# Add your API key there (or use environment variables)
```

## API Key Setup

### Option 1: Built-in Settings (Recommended)

```bash
# 1. Run groqmate
groqmate

# 2. Press Ctrl+P to open settings
# 3. Enter your API key for your preferred provider
# 4. Click Save - changes apply immediately
```

Settings are saved to `~/.groqmate/config.toml`

### Option 2: Environment Variables

```bash
# Set your API key (pick one provider)
export GROQ_API_KEY=your_key_here      # Groq (free tier)
export GEMINI_API_KEY=your_key_here    # Gemini (free tier)
export OPENAI_API_KEY=your_key_here    # OpenAI
export DEEPSEEK_API_KEY=your_key_here  # DeepSeek (cheap)
```

## Free Provider Setup

### Groq (Recommended)

**Free tier:** Yes, generous rate limits

```bash
# 1. Go to https://console.groq.com/
# 2. Sign up / log in
# 3. Create an API key
# 4. Add it in settings (Ctrl+P) or: export GROQ_API_KEY=gsk_xxx...
# 5. Run groqmate (uses Groq by default)
groqmate
```

### Google Gemini

**Free tier:** Yes, via Google AI Studio

```bash
# 1. Go to https://aistudio.google.com/
# 2. Create an API key
# 3. Add it in settings (Ctrl+P) or: export GEMINI_API_KEY=AIza...
# 4. Run with Gemini provider
groqmate -p gemini
```

### DeepSeek

**Cost:** Very cheap (~$0.55 per 1M tokens)

```bash
# 1. Go to https://platform.deepseek.com/
# 2. Create an account and API key
# 3. Add it in settings (Ctrl+P) or: export DEEPSEEK_API_KEY=sk-...
# 4. Run with DeepSeek provider
groqmate -p deepseek
```

### Ollama (Local, No API Key)

**Cost:** Free, runs locally

```bash
# 1. Install Ollama: https://ollama.ai/
# 2. Pull a model: ollama pull llama3.2
# 3. Run groqmate with Ollama (no API key needed)
groqmate -p ollama
```

### OpenRouter

**Free tier:** 100 requests/day

```bash
# 1. Go to https://openrouter.ai/
# 2. Create an account and API key
# 3. Add it in settings (Ctrl+P) or: export OPENROUTER_API_KEY=sk-or-...
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

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+P` | Open settings |
| `Ctrl+L` | Clear chat |
| `Ctrl+Q` | Quit |

### CLI Options

```bash
# Quick provider switch
groqmate gemini             # Use Gemini
groqmate ollama             # Use local Ollama
groqmate deepseek           # Use DeepSeek

# Provider with model
groqmate groq/llama-3.1-8b-instant
groqmate openai/gpt-4o-mini

# Using flags (alternative)
groqmate -p gemini
groqmate -p openai -m gpt-4o-mini

# List all providers
groqmate --list-providers
```

## Configuration

Settings are stored in `~/.groqmate/config.toml`:

```toml
[settings]
provider = "groq"
model = ""  # Empty = use default

[api_keys]
groq = "gsk_xxx..."
gemini = "AIza_xxx..."
# Add more as needed
```

You can edit this file directly or use `Ctrl+P` in the app.

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
```

## Project Structure

```
groqmate/
├── src/groqmate/
│   ├── core/
│   │   ├── models.py         # Pydantic data models
│   │   ├── state.py          # Session state machine
│   │   ├── providers.py      # Multi-provider config
│   │   ├── config.py         # Settings & API key storage
│   │   └── tutor.py          # LLM integration (LiteLLM)
│   └── interfaces/
│       └── cli/
│           ├── app.py             # Main Textual app
│           ├── widgets.py         # UI components
│           ├── settings_screen.py # Settings modal
│           └── style.tcss         # Dark theme
├── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```

## Supported Providers

| Provider | Config Key | Free Tier | Notes |
|----------|------------|-----------|-------|
| Groq | `groq` | ✅ Yes | Fast inference, recommended |
| Gemini | `gemini` | ✅ Yes | Via Google AI Studio |
| DeepSeek | `deepseek` | Cheap | ~$0.55/1M tokens |
| OpenRouter | `openrouter` | 100/day | Routes to many models |
| Ollama | `ollama` | ✅ Free | Runs locally, no API key |
| OpenAI | `openai` | No | GPT models |
| Anthropic | `anthropic` | No | Claude models |
| Mistral | `mistral` | No | Mistral models |

## License

MIT
