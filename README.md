# detroit.dev

**A community knowledge base that remembers everything.**

detroit.dev is an open, AI-powered knowledge base built and maintained by the [detroit.dev](https://detroit.dev) community. Members contribute markdown notes on any topic — research summaries, meeting notes, podcast transcriptions, tutorials — and the system makes all of it searchable, queryable, and accessible from the web, Discord, or the command line.

Ask a question in plain English. Get an answer grounded in what the community actually wrote.

---

## Why this exists

Knowledge dies in chat scroll. Good conversations happen in Discord, someone explains something well in a meeting, a podcast covers exactly the right topic — and then it's gone. detroit.dev captures that knowledge into a permanent, searchable, AI-queryable corpus that the whole community can build on.

## What you can do with it

| | |
|---|---|
| **Search** | Semantic search across the entire corpus. "How do we keep fuel available?" matches tritium-breeding content — no exact keywords needed. |
| **Ask** | Chat with the corpus. The AI retrieves the 5 most relevant chunks and synthesizes an answer grounded in community knowledge. |
| **Capture** | Transcribe podcasts, record meeting notes, save Discord threads — all become searchable corpus entries. |
| **Read** | Every note renders as a clean, readable article with adjustable fonts, themes, and a table of contents. |
| **Contribute** | Add a markdown file, open a PR, and your knowledge is part of the shared brain. |

## Quick start

```bash
git clone https://github.com/JacobHind/detroitdotdev.git
cd detroitdotdev
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Build the search index

```bash
# Requires Ollama running locally (https://ollama.com)
ollama pull nomic-embed-text
python tools/ingest.py
```

### Search and chat

```bash
python tools/search.py "how do reactors breed fuel"
python tools/serve.py          # opens http://localhost:8888 with AI chat sidebar
```

### Transcribe audio

```bash
python tools/transcribe.py recording.mp3 --qa    # local, no API key needed
```

### Build the static site

```bash
python tools/build_site.py     # renders corpus → site/
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Interfaces                           │
│  Web reader (/site)  │  Discord bot (/bot)  │  CLI tools   │
└──────────┬───────────┴──────────┬───────────┴──────┬───────┘
           │                      │                  │
           ▼                      ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     RAG Engine (common.py)                   │
│  Chunk docs → Embed → Index → Retrieve → LLM answer         │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Corpus (/corpus)                        │
│  Markdown files organized by topic, contributed by members   │
└─────────────────────────────────────────────────────────────┘
```

### How search and chat work

1. **Ingest** — `ingest.py` splits every markdown file into semantic chunks (~800 words each, split at headers), embeds them with `nomic-embed-text`, and saves the vectors to a JSON index.
2. **Search** — `search.py` embeds your query with the same model and ranks chunks by cosine similarity.
3. **Chat** — `serve.py` / `api/chat.py` / Discord bot retrieve the top 5 chunks for your question, pass them to an LLM as context, and return a grounded answer.

### Project structure

```
corpus/                  Community-contributed markdown notes
  topics/                Organized by topic (ai-ml, nuclear-fusion, web-dev, etc.)
  members/               Community member pages
  transcripts/           Podcast/video transcriptions
  generated/             Embedding index (auto-generated, gitignored)

tools/                   The engine
  common.py              Chunking, embedding, vector search, RAG retrieval
  ingest.py              Build the semantic search index
  search.py              CLI semantic search
  serve.py               Dev server with RAG chat at /api/chat
  transcribe.py          Audio/video → markdown + Q&A (faster-whisper, local)
  build_site.py          Render markdown → readable HTML articles
  chat.py                Standalone chat client

bot/                     Discord bot (see bot/README.md)
  bot.py                 /ask, /search, /capture, /notes commands

api/chat.py              Vercel serverless endpoint (production)
templates/               HTML templates for the static site
site/                    Generated static site output
```

## Infrastructure

| Component | How it runs | Cost |
|---|---|---|
| Embeddings | nomic-embed-text via Ollama (local) | Free |
| Vector index | JSON file + numpy cosine similarity | Free |
| LLM | Ollama (local), or Groq / OpenRouter / OpenAI | Free or BYOK |
| Transcription | faster-whisper on CPU (local) | Free |
| Discord bot | Any server / VPS / Railway | Free–$5/mo |
| Website | Vercel (static + serverless) | Free tier |

**Zero mandatory API keys.** Everything runs locally with Ollama. Optionally set `GROQ_API_KEY`, `OPENAI_API_KEY`, or `OPENROUTER_API_KEY` for cloud LLMs.

## Discord bot

The bot brings the entire knowledge base into your Discord server:

| Command | What it does |
|---|---|
| `/ask [question]` | RAG-powered Q&A — retrieves relevant chunks, sends to LLM, answers in-channel |
| `/search [query]` | Semantic search — top 5 results with relevance scores and previews |
| `/capture [title]` | Save recent channel messages as a corpus note (creates a GitHub PR) |
| `/notes` | List recent corpus additions |

Setup: see [bot/README.md](bot/README.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide. The short version:

1. Add a `.md` file under `corpus/topics/<category>/`
2. Include frontmatter (title, author, date, tags)
3. Run `python tools/ingest.py` to re-index
4. Open a PR

**Moderators:** CONTRIBUTING.md has a dedicated section on content review, quality standards, and how to manage the corpus.

## License

- **Content** (`corpus/`) — [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (share and adapt with attribution)
- **Code** (`tools/`, `bot/`, `api/`) — [MIT](LICENSE)
