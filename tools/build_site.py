#!/usr/bin/env python3
"""Build the static site: render corpus markdown into .pub-style HTML.

Usage:
    python tools/build_site.py                          # build all
    python tools/build_site.py corpus/topics/ai-ml/x.md # build one file
"""

import argparse
import shutil
import sys
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension

from common import iter_corpus_files, corpus_relative, parse_frontmatter, CORPUS_DIR

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
TEMPLATES_DIR = ROOT / "templates"


def build_html(body: str, fm: dict) -> str:
    """Convert markdown body to HTML and wrap in template."""
    md = markdown.Markdown(
        extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(css_class="highlight", guess_lang=False),
            TableExtension(),
            TocExtension(permalink=True),
            "markdown.extensions.smarty",
        ]
    )
    content_html = md.convert(body)
    toc_html = md.toc

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("article.html")

    return template.render(
        title=fm.get("title", "Untitled"),
        author=fm.get("author", ""),
        date=fm.get("date", ""),
        tags=fm.get("tags", []),
        source=fm.get("source", ""),
        content=content_html,
        toc=toc_html,
    )


def build_index(articles: list[dict], grouped: dict, members: list[dict]) -> str:
    """Build the index page listing all articles grouped by topic."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("index.html")
    return template.render(articles=articles, grouped=grouped, members=members)


def build_file(md_path: Path):
    """Build a single markdown file into HTML."""
    text = md_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    html = build_html(body, fm)

    rel = corpus_relative(md_path)
    out_path = SITE_DIR / Path(rel).with_suffix(".html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path


def build_all():
    """Build the entire site."""
    # Clean output
    if SITE_DIR.exists():
        for item in SITE_DIR.iterdir():
            if item.name == ".gitkeep":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    articles = []
    for path, fm, body in iter_corpus_files():
        # Skip member profiles from article listing
        rel_path = corpus_relative(path)
        if rel_path.startswith("members/"):
            continue
        out = build_file(path)
        rel_html = str(out.relative_to(SITE_DIR))
        # Extract topic from path (e.g., "topics/nuclear-fusion/foo.md" → "nuclear-fusion")
        parts = Path(rel_path).parts
        topic = parts[1] if len(parts) > 2 and parts[0] == "topics" else "misc"
        articles.append({
            "title": fm.get("title", path.stem),
            "author": fm.get("author", ""),
            "date": str(fm.get("date", "")),
            "tags": fm.get("tags", []),
            "href": rel_html,
            "topic": topic,
        })
        print(f"  Built: {rel_html}")

    # Build member pages
    members = []
    members_dir = CORPUS_DIR / "members"
    if members_dir.exists():
        for mpath in sorted(members_dir.glob("*.md")):
            if mpath.stem.startswith("_"):
                continue  # Skip templates
            text = mpath.read_text(encoding="utf-8")
            mfm, mbody = parse_frontmatter(text)
            out = build_file(mpath)
            rel_html = str(out.relative_to(SITE_DIR))
            members.append({
                "name": mfm.get("name", mpath.stem),
                "role": mfm.get("role", ""),
                "github": mfm.get("github", ""),
                "href": rel_html,
            })
            print(f"  Built member: {rel_html}")

    # Group articles by topic
    from collections import OrderedDict
    topic_labels = {
        "ai-ml": "AI & Machine Learning",
        "nuclear-fusion": "Nuclear Fusion",
        "web-dev": "Web Development",
        "systems": "Systems & Infrastructure",
        "detroit": "Detroit",
        "misc": "Miscellaneous",
    }
    grouped = OrderedDict()
    for a in sorted(articles, key=lambda x: x.get("date", ""), reverse=True):
        t = a["topic"]
        label = topic_labels.get(t, t.replace("-", " ").title())
        grouped.setdefault(label, []).append(a)

    # Build index
    index_html = build_index(articles, grouped, members)
    (SITE_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"\nBuilt {len(articles)} article(s) + {len(members)} member(s) + index.html into site/")


def main():
    parser = argparse.ArgumentParser(description="Build the .pub-style static site")
    parser.add_argument("file", nargs="?", help="Build a single file (optional)")
    args = parser.parse_args()

    if not TEMPLATES_DIR.exists():
        print(f"Error: templates directory not found at {TEMPLATES_DIR}")
        sys.exit(1)

    if args.file:
        out = build_file(Path(args.file))
        print(f"Built: {out}")
    else:
        build_all()


if __name__ == "__main__":
    main()
