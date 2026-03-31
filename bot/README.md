# detroit.dev Discord Bot

A bot that lives in your Discord server and bridges discussions into the corpus.

## What it does

- **`/capture`** — Save a thread or conversation as a corpus note (creates a PR)
- **`/ask`** — Ask a question answered from the corpus (like the site AI chat)
- **`/search`** — Search the corpus from Discord
- **Auto-notify** — Posts to a channel when new notes are merged

## Setup

### 1. Create a Discord bot

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. New Application → name it `detroit.dev bot`
3. Bot tab → Reset Token → copy it
4. Enable **Message Content Intent** (required for reading messages)
5. OAuth2 → URL Generator → scopes: `bot`, `applications.commands`
6. Bot permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`, `Create Public Threads`
7. Use generated URL to invite bot to your server

### 2. Environment variables

```bash
cp bot/.env.example bot/.env
# Fill in:
#   DISCORD_TOKEN=your-bot-token
#   GITHUB_TOKEN=ghp_...  (for creating PRs)
#   GITHUB_REPO=detroitdotdev/corpus
#   GROQ_API_KEY=gsk_...  (for /ask command, optional)
```

### 3. Run

```bash
cd bot
pip install -r requirements.txt
python bot.py
```

Or deploy as a service (systemd, Docker, Railway, etc.)

## Commands

| Command | Description |
|---------|------------|
| `/capture [channel] [title]` | Grab last N messages from a channel/thread, format as markdown, create a PR |
| `/ask [question]` | RAG query against the corpus, responds in-channel |
| `/search [query]` | Full-text search, returns top 3 matches with links |
| `/notes` | List recent corpus additions |
