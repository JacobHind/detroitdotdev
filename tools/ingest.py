#!/usr/bin/env python3
"""Build the semantic search index: chunk documents and compute embeddings.

Usage:
    python tools/ingest.py              # build full index
    python tools/ingest.py --dry-run    # show chunks without embedding
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import iter_corpus_files, corpus_relative, chunk_document, embed_texts, save_index


def main():
    parser = argparse.ArgumentParser(description="Build the semantic search index")
    parser.add_argument("--dry-run", action="store_true", help="Show chunks without computing embeddings")
    args = parser.parse_args()

    print("Chunking corpus files...\n")
    all_chunks = []
    for path, fm, body in iter_corpus_files():
        rel = corpus_relative(path)
        chunks = chunk_document(path, fm, body)
        print(f"  {rel}: {len(chunks)} chunk(s)")
        all_chunks.extend(chunks)

    print(f"\n{len(all_chunks)} total chunk(s) from corpus.\n")

    if args.dry_run:
        for i, c in enumerate(all_chunks):
            words = len(c["text"].split())
            print(f"  [{i}] {c['source']} > {c['section']} ({words} words)")
        print("\nDry run complete. No embeddings computed.")
        return

    if not all_chunks:
        print("No chunks to embed.")
        return

    print("Computing embeddings...")
    texts = [f"{c['title']} - {c['section']}\n{c['text']}" for c in all_chunks]
    embeddings = embed_texts(texts)
    print(f"  Got {len(embeddings)} embedding(s), dim={len(embeddings[0])}")

    save_index(all_chunks, embeddings)
    print(f"\nIndex saved. Run `python tools/search.py \"your query\"` to search.")


if __name__ == "__main__":
    main()
