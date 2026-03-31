# detroit.dev corpus

A shared knowledge base for the [detroit.dev](https://detroit.dev) community. Clone the repo, add notes, and chat with the entire corpus using local AI tooling.

## What is this?

A collection of community-contributed markdown files — meeting notes, podcast transcriptions, research summaries, tutorials, and anything else worth sharing. The tooling lets you:

- **Search** across the full corpus
- **Chat** with the corpus using a local LLM (via Ollama or OpenAI-compatible API)
- **Transcribe** podcasts/videos and auto-generate Q&A study notes
- **Publish** polished, web-readable articles from markdown

## Quick start

```bash
# Clone the repo
git clone https://github.com/detroitdotdev/corpus.git
cd corpus

# Install Python dependencies
pip install -r requirements.txt

# Search the corpus
python tools/search.py "transformer circuits"

# Chat with the corpus (requires Ollama or OPENAI_API_KEY)
python tools/chat.py

# Transcribe a podcast and generate Q&A
python tools/transcribe.py https://example.com/podcast.mp3

# Build the static site
python tools/build_site.py
# Then open site/index.html
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
  transcripts/           # Podcast/video transcriptions
  generated/             # AI-generated Q&A and summaries

tools/                   # Scripts for working with the corpus
  search.py              # Full-text + semantic search
  chat.py                # Chat with the corpus via RAG
  transcribe.py          # Audio/video → transcript → Q&A
  build_site.py          # Render markdown → .pub-style HTML
  ingest.py              # Build/update the search index

templates/               # HTML templates for .pub-style rendering
site/                    # Generated static site (gitignored)
```

## Contributing notes

1. Fork the repo (or push to a branch if you're an org member)
2. Add a `.md` file under `corpus/topics/<category>/` or `corpus/transcripts/`
3. Use the frontmatter template below
4. Open a PR — the build check will run automatically

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
