#!/usr/bin/env python3
"""Search the corpus with semantic or full-text search.

Usage:
    python tools/search.py "how does tritium breeding work"
    python tools/search.py --fulltext "tritium breeding"
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import iter_corpus_files, corpus_relative, semantic_search, load_index


def fulltext_search(query: str, max_results: int = 10):
    """Fallback full-text search: score by number of query-term hits."""
    terms = query.lower().split()
    results = []

    for path, fm, body in iter_corpus_files():
        text = body.lower()
        title = (fm.get("title") or "").lower()
        tags = " ".join(fm.get("tags") or []).lower()
        searchable = f"{title} {tags} {text}"

        score = sum(len(re.findall(re.escape(t), searchable)) for t in terms)
        if score > 0:
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


def print_semantic_results(results):
    if not results:
        print("No results found.")
        return
    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n{'─' * 60}")
        print(f"  {i}. {chunk['title']} > {chunk['section']}  (score: {score:.3f})")
        print(f"     {chunk['source']}")
        if chunk.get("tags"):
            print(f"     tags: {', '.join(chunk['tags'])}")
        # Show first 200 chars of chunk text
        preview = chunk["text"][:200].replace("\n", " ").strip()
        if len(chunk["text"]) > 200:
            preview += "..."
        print(f"     {preview}")
    print(f"\n{'─' * 60}")
    print(f"  {len(results)} result(s)")


def print_fulltext_results(results):
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
    parser.add_argument("--fulltext", action="store_true", help="Use keyword search instead of semantic")
    parser.add_argument("-n", "--max-results", type=int, default=5)
    args = parser.parse_args()

    if args.fulltext:
        results = fulltext_search(args.query, args.max_results)
        print_fulltext_results(results)
        return

    # Default: semantic search
    index = load_index()
    if index is None:
        print("No embedding index found. Run `python tools/ingest.py` first.")
        print("Falling back to full-text search.\n")
        results = fulltext_search(args.query, args.max_results)
        print_fulltext_results(results)
        return

    results = semantic_search(args.query, top_k=args.max_results)
    print_semantic_results(results)


if __name__ == "__main__":
    main()
