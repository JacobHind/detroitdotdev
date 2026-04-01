#!/usr/bin/env python3
"""Dev server: serves the static site and provides /api/chat for the AI sidebar.

Uses Ollama by default. Set OPENAI_API_KEY for OpenAI-compatible APIs.

Usage:
    python tools/serve.py                    # default port 8888
    python tools/serve.py --port 3000        # custom port
    python tools/serve.py --model gpt-4o     # use specific model
    python tools/serve.py --rebuild          # rebuild site before serving
"""

import argparse
import json
import os
import subprocess
import sys
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import iter_corpus_files, corpus_relative, retrieve_context

try:
    from openai import OpenAI
except ImportError:
    print("Install dependencies: pip install -r requirements.txt")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"


def get_client_and_model(model_override: str | None = None):
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        base_url = os.environ.get("OPENAI_BASE_URL")
        client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        model = model_override or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    else:
        client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        model = model_override or "nemotron-mini"
    return client, model


class DevHandler(SimpleHTTPRequestHandler):
    """Serves static files from site/ and handles /api/chat."""

    def __init__(self, *args, model=None, **kwargs):
        self._model = model
        super().__init__(*args, **kwargs)

    def do_POST(self):
        if self.path == "/api/chat":
            self.handle_chat()
        else:
            self.send_error(404)

    def handle_chat(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "Invalid JSON"}, 400)
            return

        user_msg = body.get("message", "").strip()
        if not user_msg:
            self.send_json({"error": "Empty message"}, 400)
            return

        selections = body.get("selections", "")
        article_title = body.get("article_title", "")
        history = body.get("history", [])

        # Build system prompt with relevant context (RAG)
        corpus = retrieve_context(user_msg)
        system = (
            "You are an AI assistant for detroit.dev, a community knowledge base. "
            "You have relevant excerpts from the corpus as context below. "
            "Answer questions clearly and concisely based on the provided context. "
            "When explaining technical concepts, use analogies and examples. "
            "If the user has selected specific text from an article, focus your explanation on that. "
            "If the context doesn't contain enough information, say so.\n\n"
            f"=== RELEVANT CONTEXT ===\n{corpus}\n=== END CONTEXT ==="
        )

        # Build messages
        messages = [{"role": "system", "content": system}]

        # Add recent history (skip the current message which we'll add with context)
        for h in history[:-1]:
            role = h.get("role", "")
            content = h.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

        # Build the current user message with selection context
        current = user_msg
        if selections:
            current = f"[User selected this text from \"{article_title}\":\n\"{selections}\"]\n\n{user_msg}"
        elif article_title:
            current = f"[Reading: \"{article_title}\"]\n\n{user_msg}"

        messages.append({"role": "user", "content": current})

        try:
            client, model = get_client_and_model(self._model)
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            self.send_json({"reply": reply})
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        if "/api/" in (args[0] if args else ""):
            super().log_message(format, *args)


def main():
    parser = argparse.ArgumentParser(description="Dev server with AI chat")
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--model", help="LLM model name")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild site before serving")
    args = parser.parse_args()

    if args.rebuild:
        print("Rebuilding site...")
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_site.py")], check=True)

    if not SITE_DIR.exists():
        print(f"Site directory not found. Run: python tools/build_site.py")
        sys.exit(1)

    os.chdir(SITE_DIR)
    handler = partial(DevHandler, model=args.model)
    server = HTTPServer(("", args.port), handler)

    api_key = os.environ.get("OPENAI_API_KEY")
    backend = "OpenAI" if api_key else "Ollama (localhost:11434)"
    print(f"Serving site at http://localhost:{args.port}")
    print(f"AI chat backend: {backend}")
    print(f"Press Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
