# Contributing to detroit.dev corpus

Thanks for adding to the shared brain. Here's everything you need to know.

## Quick version

1. Clone the repo
2. Add a `.md` file in `corpus/topics/<your-topic>/`
3. Run `python tools/build_site.py` to see it
4. Push a branch, open a PR

That's it. The rest of this doc covers the details.

---

## Setting up your local environment

```bash
# Clone
git clone https://github.com/detroitdotdev/corpus.git
cd corpus

# Create a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Adding a note to the corpus

### 1. Pick (or create) a topic folder

Notes live under `corpus/topics/`. Current topics:

```
corpus/topics/
  ai-ml/              # AI & machine learning
  nuclear-fusion/      # Nuclear fusion research
  web-dev/             # Web development (empty — needs you)
  systems/             # Systems & infrastructure (empty — needs you)
  detroit/             # Detroit community stuff (empty — needs you)
```

Don't see your topic? Create a new folder. Use lowercase with dashes: `corpus/topics/robotics/`, `corpus/topics/game-dev/`, etc.

### 2. Create your markdown file

```bash
# Example
touch corpus/topics/ai-ml/my-awesome-note.md
```

Use a descriptive filename — `attention-mechanisms-explained.md`, not `notes.md`.

### 3. Add frontmatter

Every note starts with YAML frontmatter between `---` markers:

```yaml
---
title: "Your Note Title"
author: "Your Name"
date: 2026-03-31
tags: [ai, attention, transformers]
source: "https://example.com/original-paper"  # optional
---
```

- **title** — shows up on the site index
- **author** — your name or handle
- **date** — when you wrote it (YYYY-MM-DD)
- **tags** — list of tags for search/filtering
- **source** — where the content came from (paper link, podcast URL, book, etc.)

### 4. Write your content

Use standard markdown. Everything works:

```markdown
# Main heading (usually matches title)

## Subheading

Regular paragraphs. **Bold**, *italic*, `inline code`.

- Bullet lists
- Work fine

| Tables | Also | Work |
|--------|------|------|
| Like   | This | Here |

Code blocks with syntax highlighting:

​```python
def hello():
    print("detroit.dev")
​```

Math (LaTeX):
$$E = mc^2$$

> Blockquotes for key quotes from sources

[Links](https://example.com) are encouraged.
```

### 5. Build and preview

```bash
# Build the entire site
python tools/build_site.py

# Serve it locally
cd site && python3 -m http.server 8080
# Open http://localhost:8080
```

Your note should appear on the index page, grouped under its topic.

### 6. Submit a PR

```bash
git checkout -b my-note-topic
git add corpus/topics/your-topic/your-note.md
git commit -m "Add notes on [your topic]"
git push origin my-note-topic
# Open a PR on GitHub
```

The CI build check runs automatically — if the site builds and there are no broken links, you're good to merge.

---

## Adding yourself to the community page

```bash
# Copy the template
cp corpus/members/_template.md corpus/members/your-name.md
```

Edit the frontmatter:

```yaml
---
name: "Your Name"
role: "Member"        # or whatever you want
github: "your-username"
date: 2026-03-31
tags: [member]
title: "Your Name"
---
```

Write whatever you want in the body — bio, interests, projects, links, hot takes. Submit as a PR.

---

## Using the AI tools

### Chat with the corpus

The whole point: ask questions and get answers grounded in community notes.

**Option A — Local with Ollama (no API key needed):**
```bash
# Install Ollama: https://ollama.com
ollama pull nemotron-mini
python tools/chat.py
```

**Option B — With an API key:**
```bash
export GROQ_API_KEY=gsk_...   # free at console.groq.com
python tools/chat.py
```

**Option C — On the website:**
Open any article, click the 💬 button (or press `Ctrl+/`). Expand "Model & Settings" to pick a provider and paste your own API key. Keys stay in your browser — never sent to our server.

### Search the corpus

```bash
python tools/search.py "plasma confinement"
python tools/search.py "how do transformers work"
```

### Transcribe audio/video

```bash
# Requires OPENAI_API_KEY (Whisper API)
export OPENAI_API_KEY=sk-...
python tools/transcribe.py podcast.mp3
python tools/transcribe.py https://youtube.com/watch?v=xyz --qa
```

This generates a markdown transcript + optional Q&A study notes, saved to `corpus/transcripts/`.

### Dev server with live AI chat

```bash
python tools/serve.py
# Open http://localhost:8080
```

This serves the built site AND provides a `/api/chat` endpoint for the in-page AI assistant. Uses Ollama by default.

---

## Reader features on the site

Every article page has:

- **Reader controls** (Aa button, bottom-right) — change font size, font family (including OpenDyslexic), line spacing, width, and theme (light/sepia/dark). Settings persist across visits.
- **AI chat sidebar** (💬 button or Ctrl+/) — highlight text and ask AI about it, or just chat about the article.
- **Table of contents** — auto-generated sidebar from your headings.

---

## Guidelines

- **One idea per file** — keep notes focused and searchable
- **Use descriptive filenames** — `transformer-circuits-framework.md` not `notes.md`
- **Tag generously** — helps search and discovery
- **Credit sources** — link to original papers, talks, books
- **No proprietary content** — respect copyrights; your own notes and summaries are fine
- **Be useful** — write for the person who'll read this in 6 months

## What makes a good note?

- Explains something you learned in your own words
- Has clear structure (headings, bullet points, tables)
- Links to primary sources
- Includes practical details (commands, parameters, code)
- Could teach the concept to a new community member

## License

- Content in `corpus/` → [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (share and adapt with attribution)
- Code in `tools/`, `bot/`, `api/` → MIT

## Questions?

Ask in the detroit.dev Discord or open a GitHub issue.
