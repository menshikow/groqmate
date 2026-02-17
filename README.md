# Groqmate

An interactive CLI learning coach powered by Groq. Think of it as a gym coach for your brain — it spots you, challenges you, and waits for you to lift the weight.

## What makes it different?

| ChatGPT | Groqmate |
|---------|----------|
| Professor delivering a lecture | Pair programmer / gym coach |
| Passive consumption | Active learning |
| Wall of text | Atomic, bite-sized chunks |
| No friction | Quiz locks between concepts |

## Features

- **Hidden Curriculum:** AI generates a 5-step plan before teaching — you see progress, not a lecture.
- **Quiz Lock:** Must answer correctly to unlock the next concept.
- **`wtf` Command:** Stuck? Type `wtf` and get a fresh analogy.
- **Flashcard Mode:** Session ends with a `notes.md` summary.
- **Terminal-native:** ASCII graphs, Unicode math, no heavy browser UI.
- **Streaming:** Token-by-token responses for a real-time feel.

## Stack

- **Python 3.11+**
- **Textual** — Rich TUI framework
- **Groq API** — LLM backend (instant speed)
- **Pydantic** — Data validation

## Installation

```bash
pip install groqmate
```

## Quick Start

```bash
# Set your API key
export GROQ_API_KEY=your_key_here

# Run
groqmate
```

## Usage Example

```
Groqmate: [Step 1 of 5: Self-Reference]
          A recursive function calls itself...
          
          ❓ Quiz: What must every recursive function have?

You: A base case

Groqmate: ✅ Correct! Type `next` to continue.

You: next

Groqmate: [Step 2 of 5: The Base Case]
          ...
```

## Commands

| Command | Action |
|---------|--------|
| `teach me <topic>` | Start a new lesson |
| `next` | Move to next step (after quiz passed) |
| `wtf` | Get a different analogy for current concept |
| `summary` | Generate flashcard summary |
| `clear` | Clear chat and start fresh |
| `help` | Show available commands |
| `quit` | Exit the app |

## License

MIT
