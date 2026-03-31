#!/usr/bin/env python3
"""Chat with the corpus using RAG.

Uses Ollama by default. Set OPENAI_API_KEY and optionally OPENAI_BASE_URL
for any OpenAI-compatible API (OpenAI, Together, Groq, etc).

Usage:
    python tools/chat.py                              # interactive
    python tools/chat.py -q "summarize the AI notes"  # single query
    python tools/chat.py --model gpt-4o               # specify model
"""

import argparse
import sys
from pathlib import Path

from common import iter_corpus_files, corpus_relative

try:
    from openai import OpenAI
except ImportError:
    print("Install dependencies: pip install -r requirements.txt")
    sys.exit(1)

import os

DEFAULT_OLLAMA_MODEL = "nemotron-mini"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def load_corpus_context(max_chars: int = 100_000) -> str:
    """Load corpus files into a single context string, truncating if needed."""
    chunks = []
    total = 0
    for path, fm, body in iter_corpus_files():
        rel = corpus_relative(path)
        title = fm.get("title", path.stem)
        header = f"\n{'=' * 40}\nFile: {rel}\nTitle: {title}\n{'=' * 40}\n"
        chunk = header + body
        if total + len(chunk) > max_chars:
            remaining = max_chars - total
            if remaining > 200:
                chunks.append(chunk[:remaining] + "\n...(truncated)")
            break
        chunks.append(chunk)
        total += len(chunk)
    return "\n".join(chunks)


def get_client_and_model(model_override: str | None = None):
    """Return (OpenAI client, model_name) based on env vars."""
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")

    if api_key:
        client = OpenAI(api_key=api_key, base_url=base_url)
        model = model_override or DEFAULT_OPENAI_MODEL
    else:
        # Default to Ollama
        client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
        model = model_override or DEFAULT_OLLAMA_MODEL

    return client, model


def chat(client, model: str, corpus_context: str, query: str, history: list) -> str:
    """Send a query with corpus context and return the response."""
    system_msg = (
        "You are a helpful assistant for the detroit.dev community. "
        "Answer questions based on the following corpus of community notes. "
        "If the answer isn't in the corpus, say so. Cite specific files when possible.\n\n"
        "--- CORPUS START ---\n"
        f"{corpus_context}\n"
        "--- CORPUS END ---"
    )

    messages = [{"role": "system", "content": system_msg}]
    messages.extend(history)
    messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Chat with the detroit.dev corpus")
    parser.add_argument("-q", "--query", help="Single query (non-interactive)")
    parser.add_argument("--model", help="Model name override")
    args = parser.parse_args()

    print("Loading corpus...")
    corpus_context = load_corpus_context()
    file_count = sum(1 for _ in iter_corpus_files())
    print(f"Loaded {file_count} file(s) into context.\n")

    client, model = get_client_and_model(args.model)
    print(f"Using model: {model}")

    if args.query:
        response = chat(client, model, corpus_context, args.query, [])
        print(f"\n{response}")
        return

    # Interactive mode
    print("Type your questions below. Type 'quit' or Ctrl+C to exit.\n")
    history = []
    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not query or query.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        response = chat(client, model, corpus_context, query, history)
        print(f"\nAssistant: {response}\n")
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
