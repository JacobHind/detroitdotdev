# Contributing to detroit.dev

Everything you need to know about adding to the knowledge base — whether you're writing your first note or reviewing PRs as a moderator.

---

## For contributors

### The 5-minute version

1. Clone the repo and set up your environment
2. Create a `.md` file in the right folder
3. Add frontmatter (title, author, date, tags)
4. Open a PR

That's it. A moderator will review and merge.

### Setting up locally

```bash
git clone https://github.com/JacobHind/detroitdotdev.git
cd detroitdotdev
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Adding a note

Notes live under `corpus/topics/`. Pick an existing folder or create one:

```
corpus/topics/
  ai-ml/              AI & machine learning
  nuclear-fusion/      Nuclear fusion research
  web-dev/             Web development
  systems/             Systems & infrastructure
  detroit/             Detroit community topics
  NIST/                Standards & frameworks
  Quantum/             Quantum computing
  misc/                Everything else
```

New topic? Create a folder. Use lowercase with dashes: `corpus/topics/robotics/`, `corpus/topics/game-dev/`.

```bash
# Create your note
touch corpus/topics/ai-ml/attention-mechanisms-explained.md
```

Use a descriptive filename — `attention-mechanisms-explained.md`, not `notes.md`.

### Frontmatter

Every note starts with YAML frontmatter:

```yaml
---
title: "Your Note Title"
author: "Your Name"
date: 2026-04-01
tags: [ai, attention, transformers]
source: "https://arxiv.org/abs/..."
---
```

| Field | Required | Description |
|---|---|---|
| `title` | Yes | Displayed on the site index and in search results |
| `author` | Yes | Your name or handle |
| `date` | Yes | When you wrote it (YYYY-MM-DD) |
| `tags` | Yes | List of tags — be generous, these power search and filtering |
| `source` | No | Where the content came from (paper, podcast, book, URL) |

### Writing your content

Standard markdown. Everything works:

- Headings (`## Section`)
- Code blocks with syntax highlighting
- Tables, bullet/numbered lists
- Math (LaTeX): `$E = mc^2$` inline, `$$` blocks
- Blockquotes for key quotes from sources
- Links and images

### What makes a good note

- **Explains something in your own words** — don't just paste; process and restate
- **Has clear structure** — headings break up the content, each section has a point
- **Links to primary sources** — papers, talks, docs, code
- **Includes practical details** — commands, parameters, code snippets, real examples
- **Could teach someone new** — write for the person who'll read this in 6 months
- **One idea per file** — focused beats comprehensive. Two clear notes > one messy one

### Transcribing audio/video

Got a podcast episode or talk worth preserving?

```bash
python tools/transcribe.py recording.mp3 --qa --whisper-model small
```

This creates a markdown transcript with auto-generated Q&A study notes. Output goes to `corpus/transcripts/`. Review and clean up before submitting.

### Adding yourself to the community page

```bash
cp corpus/members/_template.md corpus/members/your-name.md
```

Edit the frontmatter and write whatever you want — bio, interests, projects, hot takes.

### Previewing your changes

```bash
python tools/build_site.py       # build the static site
python tools/serve.py            # serve at http://localhost:8888

# Or just rebuild the search index to test your content is indexed
python tools/ingest.py
python tools/search.py "your topic"
```

### Submitting your PR

```bash
git checkout -b add/your-topic-name
git add corpus/topics/your-topic/your-note.md
git commit -m "add: notes on [your topic]"
git push origin add/your-topic-name
```

Open a PR on GitHub. CI runs automatically. A moderator will review.

---

## For moderators

This section is for people reviewing PRs, managing the corpus, and keeping the knowledge base healthy. If you've been given moderator access, this is your playbook.

### Your job

You're a librarian, not a gatekeeper. The goal is to help people get their knowledge into the corpus in a form that's useful to others. Merge fast, fix small issues yourself, and only push back when something genuinely doesn't belong.

### Reviewing content PRs

When someone opens a PR with a new note, check:

**Must-have (block merge if missing):**
- [ ] Frontmatter is present and valid (title, author, date, tags)
- [ ] File is in the right folder under `corpus/topics/` or `corpus/transcripts/`
- [ ] Filename is descriptive (not `notes.md` or `untitled.md`)
- [ ] Content is original writing or properly attributed summary (not copy-pasted copyrighted material)
- [ ] No secrets, API keys, or personal information that shouldn't be public

**Nice-to-have (suggest but don't block):**
- [ ] Tags are relevant and consistent with existing tags in the corpus
- [ ] Source link is included if the note summarizes external material
- [ ] Headings create a logical structure
- [ ] Content is substantial enough to be useful (more than a few sentences)

**Don't worry about:**
- Grammar, spelling, formatting polish — imperfect knowledge > no knowledge
- Whether you personally find the topic interesting
- Whether similar content exists — different perspectives are valuable

### Handling common PR scenarios

**Good note, small issues (typo in frontmatter, wrong folder):**
Fix it yourself and merge. Leave a friendly comment explaining what you changed.

**Low-effort dump (pasted text wall, no structure, no attribution):**
Comment with specific feedback: "This would be really useful if you could break it into sections with headings and link to where you found this." Don't close — give them a chance to improve.

**Off-topic or spam:**
Close with a brief explanation. Be direct but not rude.

**Duplicate of existing content:**
Check if the new note adds anything. Different angle on the same topic? Merge it. Near-identical? Point to the existing note and suggest they add to it instead.

**Bot-captured Discord threads (`/capture`):**
These come in as raw conversation transcripts. Review for:
- Is the conversation actually substantive? Not every chat is worth preserving.
- Consider editing the title to be descriptive.
- If it's good, merge as-is — raw discussions have value even without polish.

### Managing the corpus structure

**Creating new topic folders:**
Anyone can propose them via PR. As a moderator, consider:
- Is this genuinely a new topic, or does it fit under an existing folder?
- Use lowercase with dashes: `corpus/topics/hardware-hacking/`
- Don't create empty folders speculatively — wait until there's content to put in them

**Moving or renaming files:**
If a note is in the wrong folder or has a bad filename, move it yourself:
```bash
git mv corpus/topics/misc/fusion-stuff.md corpus/topics/nuclear-fusion/tritium-handling.md
```
Update any internal links, rebuild the index, and note the change in the commit message.

**Archiving outdated content:**
Don't delete — knowledge has long tails. If something is outdated, add a note at the top:
```markdown
> **Note (2026-04-01):** This was written about X v1.0. Much has changed since — see [updated-note.md](updated-note.md) for current information.
```

### Running the tools

As a moderator, you should be comfortable with:

```bash
# Rebuild the search index after merging new content
python tools/ingest.py

# Verify new content is searchable
python tools/search.py "topic from the new PR"

# Build and check the site
python tools/build_site.py
python tools/serve.py
```

After merging a batch of PRs, rebuild the index and push the updated site. The embedding index (`corpus/generated/embeddings.json`) is gitignored — it's rebuilt on each machine.

### Moderator checklist for a typical week

- [ ] Review and merge (or give feedback on) open PRs within 48 hours
- [ ] Run `python tools/ingest.py` after merging new content to keep search fresh
- [ ] Spot-check that `/ask` and `/search` (Discord or web) return sensible results for new content
- [ ] If someone's been active in Discord but hasn't contributed a note, nudge them: "That explanation you gave about X was great — want to turn it into a corpus note?"

### Inviting new moderators

When the community grows, you'll need more moderators. Look for people who:
- Contribute regularly and write well-structured notes
- Help others in Discord (answering questions, sharing resources)
- Understand the purpose of the project (knowledge preservation, not content farming)

Add them as collaborators on GitHub with write access.

---

## Content guidelines

These apply to everyone — contributors and moderators.

- **One idea per file** — focused and searchable
- **Descriptive filenames** — `transformer-circuits-framework.md`, not `notes.md`
- **Tag generously** — powers search and discovery
- **Credit sources** — link to original papers, talks, books, docs
- **No proprietary content** — respect copyrights; your own notes and summaries are fine
- **Be useful** — write for the next person, not for yourself

## Reader features

Every published article on the site includes:
- **Reader controls** (Aa button) — font size, font family (including OpenDyslexic), line spacing, width, theme (light/sepia/dark)
- **AI chat sidebar** (💬 or Ctrl+/) — highlight text and ask about it, or chat about the whole article
- **Table of contents** — auto-generated from your headings

## License

- **Content** in `corpus/` → [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (share and adapt with attribution)
- **Code** in `tools/`, `bot/`, `api/` → [MIT](LICENSE)

## Questions?

Ask in the detroit.dev Discord or open a [GitHub issue](https://github.com/JacobHind/detroitdotdev/issues).
