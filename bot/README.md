# detroit.dev Discord Bot

A bot that lives in your Discord server — search and chat with the corpus directly from Discord.

## What it does

- **`/ask`** — RAG-powered Q&A. Retrieves the 5 most relevant corpus chunks, sends them to an LLM, and returns a grounded answer.
- **`/search`** — Semantic search. Returns the top 5 matching corpus sections with relevance scores and previews.
- **`/capture`** — Save a thread or conversation as a corpus note (creates a GitHub PR)
- **`/notes`** — List recent corpus additions

## Setup

### 1. Create a Discord bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. New Application → name it `detroit.dev bot`
3. Bot tab → Reset Token → copy it
4. Enable **Message Content Intent** (required for reading messages)
5. OAuth2 → URL Generator → scopes: `bot`, `applications.commands`
6. Bot permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
7. Use the generated URL to invite the bot to your server

### 2. Prerequisites

The bot uses the same RAG engine as the rest of the project. You need:

```bash
# From the project root — build the embedding index first
pip install -r requirements.txt
python tools/ingest.py

# Ollama must be running for embeddings + LLM (unless you set API keys)
ollama pull nomic-embed-text
ollama pull qwen3:4b
```

### 3. Environment variables

```bash
cp bot/.env.example bot/.env
```

**Required:**
- `DISCORD_TOKEN` — your bot token from step 1

**Optional (bot works with local Ollama if none are set):**
- `GROQ_API_KEY` — fastest, recommended for production
- `OPENROUTER_API_KEY` — alternative cloud LLM
- `OPENAI_API_KEY` — OpenAI models
- `GITHUB_TOKEN` — enables `/capture` to create PRs
- `GITHUB_REPO` — defaults to `JacobHind/detroitdotdev`
- `LLM_MODEL` — override the default model for any provider

### 4. Run

```bash
cd bot
pip install -r requirements.txt
python bot.py
```

## How /ask works

```
User: /ask how do reactors breed tritium?
               │
               ▼
     ┌── semantic_search() ──┐
     │  Embed query with      │
     │  nomic-embed-text      │
     │  Find top-5 chunks     │
     │  by cosine similarity  │
     └────────┬───────────────┘
              ▼
     ┌── LLM completion ─────┐
     │  System prompt with    │
     │  retrieved chunks      │
     │  → grounded answer     │
     └────────┬───────────────┘
              ▼
     Bot replies in Discord
```

## Commands

| Command | Description |
|---------|------------|
| `/ask [question]` | RAG query — retrieves relevant chunks, sends to LLM, returns grounded answer |
| `/search [query]` | Semantic search — top 5 results with scores and previews |
| `/digest [count]` | Evaluate recent conversation — if it's useful knowledge, summarize and create a PR |
| `/capture [title] [count]` | Grab last N messages as a raw transcript, create a GitHub PR |
| `/notes` | List recent corpus commits |

## Auto-digest (passive knowledge capture)

The bot can watch channels and automatically capture knowledge. When conversation goes quiet, the bot:

1. Collects the recent messages from the buffer
2. Asks the LLM: "Is this conversation knowledge-worthy?"
3. If yes — summarizes it into a clean, structured corpus note (not a raw transcript)
4. Opens a GitHub PR and notifies the channel

Casual chat, greetings, scheduling, and banter are ignored. Only substantive discussions — technical explanations, problem-solving, research, how-tos — get captured.

### Auto-digest setup

Add to your `bot/.env`:

```bash
# Watch specific channels (comma-separated IDs)
WATCH_CHANNELS=123456789,987654321

# Or watch everything
WATCH_CHANNELS=all

# Tune the trigger
DIGEST_QUIET_MINUTES=10    # wait this long after last message
DIGEST_MIN_MESSAGES=8      # need at least this many messages
```

### /digest vs /capture

| | `/digest` | `/capture` |
|---|---|---|
| Output | Clean summary written by LLM | Raw message transcript |
| Quality filter | Yes — skips if not knowledge-worthy | No — captures everything |
| Trigger | Manual or automatic (via WATCH_CHANNELS) | Manual only |
| Best for | Extracting knowledge from discussion | Archiving a specific thread |
