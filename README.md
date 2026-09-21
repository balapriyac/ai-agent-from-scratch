# Building an AI Agent From Scratch

A minimal example of an AI agent built directly against the Anthropic API, with no agent framework involved. Companion code for the article "How and Why to Build an AI Agent From Scratch in Python."

## What This Contains

- `agent.py`: a single file containing a tool definition (an order lookup), the schema the model reads to decide when to call it, and an `Agent` class that runs the tool-calling loop and keeps conversation memory across calls.

## Setup

1. Install Python 3.10 or newer.
2. Install the dependency:

   ```bash
   pip install anthropic
   ```

3. Set your Anthropic API key as an environment variable:

   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

## Running It

```bash
python agent.py
```

This runs two calls against the same `Agent` instance. The first asks about order #4471 directly. The second asks a follow-up question, "And when will it arrive?", which only makes sense if the earlier exchange is still available. This demonstrates why `self.messages` persists across calls instead of resetting each time.

