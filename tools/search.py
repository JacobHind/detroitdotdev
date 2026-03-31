#!/usr/bin/env python3
"""Search the corpus with full-text or semantic search.

Usage:
    python tools/search.py "query terms"
    python tools/search.py --semantic "how do transformers learn"
"""

import argparse
import re
import sys
from pathlib import Path

from common import iter_corpus_files, corpus_relative


def fulltext_search(query: str, max_results: int = 10):
    """Simple full-text search: score by number of query-term hits."""
    terms = query.lower().split()
    results = []

    for path, fm, body in iter_corpus_files():
        text = body.lower()
        title = (fm.get("title") or "").lower()
        tags = " ".join(fm.get("tags") or []).lower()
        searchable = f"{title} {tags} {text}"

        score = sum(len(re.findall(re.escape(t), searchable)) for t in terms)
        if score > 0:
            # Grab a snippet around the first match
            snippet = _snippet(body, terms)
            results.append((score, path, fm, snippet))

    results.sort(key=lambda x: -x[0])
    return results[:max_results]


def _snippet(body: str, terms: list[str], context: int = 120) -> str:
    """Extract a text snippet around the first matching term."""
    lower = body.lower()
    for t in terms:
        idx = lower.find(t)
        if idx >= 0:
            start = max(0, idx - context // 2)
            end = min(len(body), idx + len(t) + context // 2)
            s = body[start:end].replace("\n", " ").strip()
            if start > 0:
                s = "..." + s
            if end < len(body):
                s = s + "..."
            return s
    return body[:context].replace("\n", " ").strip() + "..."


def print_results(results):
    if not results:
        print("No results found.")
        return
    for i, (score, path, fm, snippet) in enumerate(results, 1):
        title = fm.get("title", path.stem)
        rel = corpus_relative(path)
        print(f"\n{'─' * 60}")
        print(f"  {i}. {title}")
        print(f"     {rel}")
        if fm.get("tags"):
            print(f"     tags: {', '.join(fm['tags'])}")
        print(f"     {snippet}")
    print(f"\n{'─' * 60}")
    print(f"  {len(results)} result(s)")


def main():
    parser = argparse.ArgumentParser(description="Search the detroit.dev corpus")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--semantic", action="store_true", help="Use semantic search (requires embeddings)")
    parser.add_argument("-n", "--max-results", type=int, default=10)
    args = parser.parse_args()

    if args.semantic:
        print("Semantic search requires an embeddings index. Run `python tools/ingest.py` first.")
        print("Falling back to full-text search.\n")

    results = fulltext_search(args.query, args.max_results)
    print_results(results)


if __name__ == "__main__":
    main()
