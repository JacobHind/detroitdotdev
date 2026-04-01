#!/usr/bin/env python3
"""detroit.dev Discord bot — search and chat with the corpus from Discord.

Commands:
  /ask [question]    — RAG-powered Q&A against the corpus
  /search [query]    — semantic search, returns top results
  /capture [title]   — save recent messages as a corpus note (creates a GitHub PR)
  /notes             — list recent corpus additions
"""

import base64
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import discord
import httpx
from discord import app_commands
from dotenv import load_dotenv

# ── Import the RAG engine from tools/common.py ─────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from common import semantic_search, retrieve_context

load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "JacobHind/detroitdotdev")
NOTIFY_CHANNEL = os.environ.get("NOTIFICATION_CHANNEL_ID", "")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# ── LLM client (same multi-provider pattern as serve.py) ───────

def get_llm_client():
    """Return (OpenAI-client, model) using the best available provider.

    Priority: GROQ_API_KEY > OPENROUTER_API_KEY > OPENAI_API_KEY > Ollama.
    """
    from openai import OpenAI

    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        return OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1"), \
               os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        return OpenAI(api_key=openrouter_key, base_url="https://openrouter.ai/api/v1"), \
               os.environ.get("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct")

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        base_url = os.environ.get("OPENAI_BASE_URL")
        c = OpenAI(api_key=openai_key, base_url=base_url) if base_url else OpenAI(api_key=openai_key)
        return c, os.environ.get("LLM_MODEL", "gpt-4o-mini")

    # Fallback: local Ollama
    return OpenAI(base_url="http://localhost:11434/v1", api_key="ollama"), \
           os.environ.get("LLM_MODEL", "qwen3:4b")


# ── Helpers ─────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60].strip("-")


def messages_to_markdown(messages: list[discord.Message], title: str) -> str:
    """Format a list of Discord messages as a corpus markdown note."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    authors = sorted(set(m.author.display_name for m in messages))

    lines = [
        "---",
        f'title: "{title}"',
        f'author: "{", ".join(authors)}"',
        f"date: {today}",
        f"tags: [discord, discussion]",
        f'source: "Discord #{messages[0].channel.name}"',
        "---",
        "",
        f"# {title}",
        "",
        f"*Captured from Discord #{messages[0].channel.name} on {today}.*",
        "",
    ]

    for msg in messages:
        ts = msg.created_at.strftime("%H:%M")
        lines.append(f"**{msg.author.display_name}** ({ts}):")
        lines.append(msg.content)
        lines.append("")

    return "\n".join(lines)


async def create_github_pr(title: str, content: str, slug: str) -> str | None:
    """Create a branch, commit, and PR on GitHub with the captured note."""
    if not GITHUB_TOKEN:
        return None

    branch = f"bot/capture-{slug}-{int(datetime.now().timestamp())}"
    file_path = f"corpus/topics/detroit/{slug}.md"

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    api = f"https://api.github.com/repos/{GITHUB_REPO}"

    async with httpx.AsyncClient() as http:
        # Get default branch SHA
        r = await http.get(f"{api}/git/ref/heads/main", headers=headers)
        if r.status_code != 200:
            return None
        main_sha = r.json()["object"]["sha"]

        # Create branch
        r = await http.post(
            f"{api}/git/refs",
            headers=headers,
            json={"ref": f"refs/heads/{branch}", "sha": main_sha},
        )
        if r.status_code not in (200, 201):
            return None

        # Create file
        r = await http.put(
            f"{api}/contents/{file_path}",
            headers=headers,
            json={
                "message": f"bot: capture \"{title}\" from Discord",
                "content": base64.b64encode(content.encode()).decode(),
                "branch": branch,
            },
        )
        if r.status_code not in (200, 201):
            return None

        # Create PR
        r = await http.post(
            f"{api}/pulls",
            headers=headers,
            json={
                "title": f"📝 Discord capture: {title}",
                "body": (
                    f"Captured from Discord by the detroit.dev bot.\n\n"
                    f"**Messages**: {len(content.splitlines())} lines\n\n"
                    f"*Auto-generated — please review before merging.*"
                ),
                "head": branch,
                "base": "main",
            },
        )
        if r.status_code in (200, 201):
            return r.json()["html_url"]

    return None


def ask_corpus(question: str) -> str:
    """RAG query: retrieve relevant chunks, send to LLM, return answer."""
    context = retrieve_context(question, top_k=5)

    system = (
        "You are the detroit.dev assistant. Answer questions based on the "
        "knowledge base excerpts provided below. Be concise and helpful. "
        "If the context doesn't cover the question, say so honestly.\n\n"
        f"=== RELEVANT CONTEXT ===\n{context}\n=== END CONTEXT ==="
    )

    try:
        llm, model = get_llm_client()
        resp = llm.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": question},
            ],
            max_tokens=600,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"LLM error: {e}"


# ── Slash Commands ──────────────────────────────────────────────


@tree.command(name="ask", description="Ask a question answered from the corpus")
@app_commands.describe(question="Your question")
async def ask_command(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    answer = ask_corpus(question)
    # Discord has a 2000 char limit
    if len(answer) > 1900:
        answer = answer[:1900] + "…"
    await interaction.followup.send(f"**Q:** {question}\n\n{answer}")


@tree.command(name="search", description="Semantic search across the corpus")
@app_commands.describe(query="What are you looking for?")
async def search_command(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)

    results = semantic_search(query, top_k=5)

    if not results:
        await interaction.followup.send(
            "No results — the search index may not be built yet. "
            "Run `python tools/ingest.py` on the server."
        )
        return

    lines = [f"🔍 **Results for:** {query}\n"]
    for i, (chunk, score) in enumerate(results, 1):
        source = chunk["source"]
        section = chunk["section"]
        preview = chunk["text"][:200].replace("\n", " ")
        if len(chunk["text"]) > 200:
            preview += "…"
        lines.append(f"**{i}. {section}** ({score:.0%} match)")
        lines.append(f"   *{source}*")
        lines.append(f"   {preview}\n")

    reply = "\n".join(lines)
    if len(reply) > 1900:
        reply = reply[:1900] + "\n…"
    await interaction.followup.send(reply)


@tree.command(name="capture", description="Capture recent messages as a corpus note")
@app_commands.describe(
    title="Title for the note",
    count="Number of messages to capture (default: 30, max: 100)",
)
async def capture_command(
    interaction: discord.Interaction, title: str, count: int = 30
):
    await interaction.response.defer(thinking=True)

    count = min(count, 100)
    messages = []
    async for msg in interaction.channel.history(limit=count):
        if not msg.author.bot and msg.content.strip():
            messages.append(msg)

    if not messages:
        await interaction.followup.send("No messages to capture.")
        return

    messages.reverse()  # Chronological order
    slug = slugify(title)
    md = messages_to_markdown(messages, title)

    pr_url = await create_github_pr(title, md, slug)

    if pr_url:
        await interaction.followup.send(
            f"✅ Captured **{len(messages)} messages** as \"{title}\"\n"
            f"📝 PR created: {pr_url}\n"
            f"Review and merge to add to the corpus."
        )
    elif GITHUB_TOKEN:
        await interaction.followup.send(
            f"⚠️ Captured {len(messages)} messages but failed to create PR. "
            f"Check the bot's GitHub token permissions."
        )
    else:
        # No GitHub token — just show a preview
        preview = md[:1500] + ("\n..." if len(md) > 1500 else "")
        await interaction.followup.send(
            f"📝 Preview of \"{title}\" ({len(messages)} messages):\n```md\n{preview}\n```\n"
            f"*Set GITHUB_TOKEN in bot/.env to auto-create PRs.*"
        )


@tree.command(name="notes", description="List recent corpus additions")
async def notes_command(interaction: discord.Interaction):
    """List recent commits that added corpus files."""
    if not GITHUB_TOKEN:
        await interaction.response.send_message(
            "Set GITHUB_TOKEN to list recent notes."
        )
        return

    await interaction.response.defer(thinking=True)

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    api = f"https://api.github.com/repos/{GITHUB_REPO}"

    async with httpx.AsyncClient() as http:
        r = await http.get(
            f"{api}/commits",
            headers=headers,
            params={"path": "corpus/", "per_page": 5},
        )
        if r.status_code != 200:
            await interaction.followup.send("Failed to fetch recent notes.")
            return

        commits = r.json()
        if not commits:
            await interaction.followup.send("No recent corpus changes.")
            return

        lines = ["**Recent corpus updates:**"]
        for c in commits:
            msg = c["commit"]["message"].split("\n")[0][:80]
            date = c["commit"]["author"]["date"][:10]
            url = c["html_url"]
            lines.append(f"• [{date}] [{msg}]({url})")

        await interaction.followup.send("\n".join(lines))


# ── Events ──────────────────────────────────────────────────────


@client.event
async def on_ready():
    await tree.sync()
    print(f"detroit.dev bot online as {client.user} — {len(tree.get_commands())} commands synced")


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
