# Groqmate

* **ChatGPT feels like:** A Professor delivering a lecture. You sit back and listen.
* **Groqmate feels like:** A Gym Coach or a Pair Programmer. It’s active. It spots you. It waits for you to lift the weight.

## 2. The "Hidden State" Architecture

We need to brainstorm how the AI manages the lesson in the background.

**The Hidden Curriculum:**
When a user asks "Teach me Recursion," the AI shouldn't just start talking. It should generate a **Hidden Plan** first:

1. *Concept: What is a function calling itself?*
2. *Concept: The Base Case (Stopping condition).*
3. *Concept: The Recursive Step.*
4. *Example: Factorial function.*
5. *Risk: Stack Overflow error.*

**Brainstorm Idea:**

* Progress bar like in the videogame: `Step 1 of 5: The Base Case`. 

## 3. Feature Ideas

Since we aren't coding yet, let's dream big about what this CLI could do.

* **The "WTF" Command:**
Sometimes the user gets stuck but doesn't know what to ask.
* *Feature:* User types `wtf` (or `?`).
* *Action:* Groqmate instantly re-phrases the *current* chunk using a completely different analogy (e.g., "Okay, let's explain it like a cooking recipe instead of math").

* **The "Quiz Lock":**
To truly solve "Cognitive Overload," maybe we don't just ask "Did you understand?"
* *Feature:* To unlock Chunk 3, the user *must* answer a multiple-choice question about Chunk 2.
* *Interaction:*
> **Groqmate:** "To move on, what is the output of `print(2**3)`?"
> **User:** "6"
> **Groqmate:** "Incorrect. It is . Let's review exponents."

* **The "Flashcard" Mode:**
Since the AI is breaking things into chunks, can we save those chunks?
* *Feature:* At the end of the session, Groqmate saves a summary file `recursion_notes.md` with just the key definitions.

## 4. Visualizing the "Math" Problem

**Brainstorming Solutions:**

1. **ASCII Art:** We train the system prompt to draw graphs using text characters.
```text
   y
   ^
   |    /
   |   /
   |  /
---+---------> x

```


2. **The "Desmos" Link:** If the math gets too hard, Groqmate generates a link to a graphing calculator pre-filled with the formula.
3. **LaTeX to Unicode:** We force the AI to use symbols like `∫` and `∑` which *do* work in most terminals, rather than standard LaTeX code.

## 5. The "Groqmate" Brand Identity

If you launch this, it needs a personality.

* **Tone:** "Terse, Encouraging, Hacker-ish."
* **Colors (Textual Theme):**
* **User:** White text.
* **AI:** "Groq Orange" (Since they are the hardware provider) or "Matrix Green."
* **Alerts:** Bright Yellow.

## 6. Summary of the "Product Spec"

* **Input:** "Teach me X."
* **Process:** AI splits X into 5 atomic concepts.
* **Output:** Concept 1 displayed.
* **Constraint:** User CANNOT see Concept 2 until they interact.
* **UI:** Dark mode terminal, progress bars, syntax highlighting.
* **Engine:** Groq (Instant speed).
