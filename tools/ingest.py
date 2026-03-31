#!/usr/bin/env python3
"""Build a search index for semantic search (future use).

Usage:
    python tools/ingest.py
"""

from common import iter_corpus_files, corpus_relative


def main():
    print("Indexing corpus files...\n")
    count = 0
    for path, fm, body in iter_corpus_files():
        rel = corpus_relative(path)
        title = fm.get("title", path.stem)
        tags = fm.get("tags", [])
        word_count = len(body.split())
        print(f"  {rel}")
        print(f"    title: {title} | tags: {', '.join(tags)} | {word_count} words")
        count += 1

    print(f"\n{count} file(s) indexed.")
    print("\nNote: Semantic search with embeddings is not yet implemented.")
    print("For now, use `python tools/search.py` for full-text search.")


if __name__ == "__main__":
    main()
