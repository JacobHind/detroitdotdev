#!/usr/bin/env python3
"""detroit.dev Discord bot — captures discussions into the corpus.

Commands:
  /capture [title] — save recent messages from this channel as a corpus note (creates a GitHub PR)
  /ask [question]  — ask a question answered from the corpus
  /search [query]  — search the corpus
  /notes           — list recent corpus additions
"""

import os
import re
from datetime import datetime, timezone

import discord
import httpx
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "detroitdotdev/corpus")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
NOTIFY_CHANNEL = os.environ.get("NOTIFICATION_CHANNEL_ID", "")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


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
        import base64

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
                "body": f"Captured from Discord by the detroit.dev bot.\n\n**Messages**: {len(content.splitlines())} lines\n\n*Auto-generated — please review before merging.*",
                "head": branch,
                "base": "main",
            },
        )
        if r.status_code in (200, 201):
            return r.json()["html_url"]

    return None


async def ask_corpus(question: str) -> str:
    """Ask a question using the site's API (or Groq directly)."""
    if GROQ_API_KEY:
        async with httpx.AsyncClient(timeout=30) as http:
            r = await http.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are the detroit.dev assistant. Answer questions concisely based on your knowledge. If you don't know, say so.",
                        },
                        {"role": "user", "content": question},
                    ],
                    "max_tokens": 512,
                },
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            return f"API error: {r.status_code}"

    return "No AI backend configured. Set GROQ_API_KEY in bot/.env"


# ── Slash Commands ──────────────────────────────────────────────


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


@tree.command(name="ask", description="Ask a question answered from the corpus")
@app_commands.describe(question="Your question")
async def ask_command(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    answer = await ask_corpus(question)
    # Discord has a 2000 char limit
    if len(answer) > 1900:
        answer = answer[:1900] + "…"
    await interaction.followup.send(f"**Q:** {question}\n\n{answer}")


@tree.command(name="search", description="Search the corpus")
@app_commands.describe(query="Search query")
async def search_command(interaction: discord.Interaction, query: str):
    await interaction.response.send_message(
        f"🔍 Search isn't wired to the live corpus yet. "
        f"Use the site: https://detroit.dev\n"
        f"Or locally: `python tools/search.py \"{query}\"`"
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
