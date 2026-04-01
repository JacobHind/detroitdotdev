# detroit.dev corpus

A shared knowledge base for the [detroit.dev](https://detroit.dev) community. Clone the repo, add notes, and chat with the entire corpus using local AI — no API keys required.

## What is this?

A collection of community-contributed markdown files — meeting notes, podcast transcriptions, research summaries, tutorials, and anything else worth sharing. The tooling lets you:

- **Semantic Search** — Find meaning, not just keywords. "How do we keep fuel available?" finds tritium-breeding content even if you don't use the word "tritium."
- **RAG Chat** — Ask questions and get AI-synthesized answers from the most relevant 5 chunks (not the entire corpus)
- **Local Transcription** — Convert podcasts/videos to markdown + auto-generate Q&A study notes using `faster-whisper` (no API key)
- **Static Publishing** — Render polished, web-readable articles with customizable fonts, themes, and reader controls

## Quick start

```bash
# Clone the repo
git clone https://github.com/detroitdotdev/corpus.git
cd corpus

# Install Python dependencies (includes numpy, faster-whisper)
pip install -r requirements.txt

# Build the semantic search index (run once, then whenever you add docs)
python tools/ingest.py

# Search the corpus semantically
python tools/search.py "how do reactors breed fuel"

# Chat with the corpus (uses local Ollama by default; set OPENAI_API_KEY for OpenAI)
python tools/serve.py
# Then open http://localhost:8888 and use the AI chat sidebar

# Transcribe a podcast (uses faster-whisper locally, no API key)
python tools/transcribe.py https://example.com/podcast.mp3 --qa

# Build the static site
python tools/build_site.py
# Then open site/index.html
```

## How it works

### Semantic Search
The corpus is chunked into semantic pieces (~72 chunks from 8 docs), embedded using `nomic-embed-text` (local Ollama), and stored in a JSON index. Queries are embedded the same way, and results are ranked by cosine similarity — finding meaning rather than keywords.

```bash
python tools/search.py "query"                  # Semantic search (default)
python tools/search.py "query" --fulltext      # Fallback to keyword search
```

### RAG Chat
When you ask a question, the system:
1. Retrieves the 5 most relevant chunks from the semantic index
2. Passes only those chunks (+ history) to the LLM
3. LLM synthesizes an answer grounded in "the corpus"

This scales from 8 docs → 4000 docs without changing infrastructure.

### Local Transcription
Uses `faster-whisper` (4x faster than OpenAI's Whisper, runs on CPU). Model sizes:
- `tiny` (75M params) — ~20 sec for 10 min audio, lower quality
- `small` (244M params) — ~1-2 min for 10 min audio, good for most content
- `medium` (769M params) — ~4-5 min for 10 min audio, near-perfect

```bash
python tools/transcribe.py recording.mp3 --whisper-model small
python tools/transcribe.py recording.mp3 --qa --whisper-model medium  # with Q&A
```

## Project structure

```
corpus/                  # Community-contributed markdown notes
  topics/                # Organized by topic
    ai-ml/
    web-dev/
    systems/
    detroit/
    misc/
  transcripts/           # Podcast/video transcriptions (auto-generated)
  generated/             # AI-generated Q&A and embeddings.json index

tools/                   # Scripts for working with the corpus
  common.py              # Shared utilities (embedding, chunking, RAG retrieval)
  search.py              # Semantic + full-text search
  chat.py                # Chat client (deprecated; use serve.py instead)
  serve.py               # Dev server with RAG chat at /api/chat
  transcribe.py          # Audio/video → transcript → Q&A
  build_site.py          # Render markdown → .pub-style HTML
  ingest.py              # Chunk docs and compute embeddings

templates/               # HTML templates for .pub-style rendering
site/                    # Generated static site (gitignored)
api/chat.py              # Vercel serverless handler (same RAG logic as serve.py)
```

## Infrastructure

| Component | Local? | Cost |
|---|---|---|
| Embeddings (nomic-embed-text) | ✅ Ollama | Free |
| Search index | ✅ JSON + numpy | Free |
| LLM chat | ✅ Ollama, or bring your own | Free or BYOK |
| Transcription (faster-whisper) | ✅ CPU/GPU | Free |
| Hosting | ✅ Static site or Vercel | Free or cheap |

**Zero mandatory API keys.** All tools work with Ollama (local). Optionally bring your own keys to OpenAI/NVIDIA/Groq/etc.

## Contributing notes

1. Fork the repo (or push to a branch if you're an org member)
2. Add a `.md` file under `corpus/topics/<category>/` or `corpus/transcripts/`
3. Use the frontmatter template below
4. Run `python tools/ingest.py` to re-index
5. Open a PR — the build check will run automatically

### Frontmatter template

```yaml
---
title: "Your Note Title"
author: "Your Name"
date: 2026-03-31
tags: [ai, transformers, interpretability]
source: ""  # optional: URL, podcast, book, etc.
---
```

### Add yourself to the community page

```bash
cp corpus/members/_template.md corpus/members/your-name.md
# Edit the file with your info
# Submit a PR
```

Write your content in standard markdown. Code blocks, math (LaTeX), images, and links all work.

### Guidelines

- **One idea per file** — keep notes focused
- **Use descriptive filenames** — `transformer-circuits-framework.md` not `notes.md`
- **Tag generously** — helps search and discovery
- **Credit sources** — link to original material
- **No proprietary content** — respect copyrights

## CI/CD & Branch Protection

### Automatic checks (GitHub Actions)

Every PR runs `.github/workflows/build-check.yml`:
- Installs deps, builds the site, checks for broken internal links
- PR can't merge if the build fails

On merge to `main`, `.github/workflows/deploy.yml` auto-deploys to Vercel.

### Setting up branch protection

Go to **GitHub → Settings → Branches → Add rule** for `main`:

1. **Require a pull request before merging** ✓
2. **Require status checks to pass before merging** ✓ → select "Build Check"
3. **Do not allow bypassing the above settings** ✓ (even admins go through PRs)
4. **Require approvals**: 1 (recommended for a small team)

### Vercel secrets (one-time setup)

Add these in **GitHub → Settings → Secrets → Actions**:
- `VERCEL_TOKEN` — from [vercel.com/account/tokens](https://vercel.com/account/tokens)
- `VERCEL_ORG_ID` — from `.vercel/project.json` after `vercel link`
- `VERCEL_PROJECT_ID` — same file

### Discord bot

The `bot/` directory contains a Discord bot that can capture discussions and populate the corpus. See `bot/README.md` for setup.

## Tooling details

### Search

Full-text search across all markdown files, with optional semantic search (requires embeddings model).

```bash
python tools/search.py "induction heads"
python tools/search.py --semantic "how do transformers learn in-context"
```

### Chat

RAG-powered chat over the corpus. Uses Ollama by default, or set `OPENAI_API_KEY` / `OPENAI_BASE_URL` for any OpenAI-compatible API.

```bash
python tools/chat.py                          # interactive mode
python tools/chat.py -q "summarize the corpus on MLOps"  # single query
```

### Transcribe

Transcribe audio/video and optionally generate Q&A study notes.

```bash
python tools/transcribe.py podcast.mp3
python tools/transcribe.py https://youtube.com/watch?v=... --qa
```

### Publish

Render markdown files into clean, Distill/Anthropic-style HTML articles.

```bash
python tools/build_site.py                    # build all
python tools/build_site.py corpus/topics/ai-ml/my-note.md  # build one
```

## License

Content in `corpus/` is contributed by community members under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Tooling in `tools/` is MIT licensed.
