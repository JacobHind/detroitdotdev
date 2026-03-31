"""Shared utilities for corpus tools."""

import os
import re
import yaml
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"


def iter_corpus_files():
    """Yield (path, frontmatter_dict, body_text) for every .md file in the corpus."""
    for md_path in sorted(CORPUS_DIR.rglob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        yield md_path, fm, body


def parse_frontmatter(text: str):
    """Split a markdown file into (frontmatter_dict, body_str)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if match:
        try:
            fm = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            fm = {}
        body = text[match.end():]
    else:
        fm = {}
        body = text
    return fm, body


def corpus_relative(path: Path) -> str:
    """Return the path relative to the corpus root."""
    try:
        return str(path.relative_to(CORPUS_DIR))
    except ValueError:
        return str(path)
