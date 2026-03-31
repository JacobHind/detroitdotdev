import json
import os
import glob
from http.server import BaseHTTPRequestHandler

# Try openai, fall back gracefully
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# ── Corpus loading ──────────────────────────────────────────────
# Reads markdown files from corpus/ at cold-start (cached across invocations)
_corpus_cache = None


def _parse_frontmatter(text):
    """Extract YAML frontmatter and body from markdown text."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text


def load_corpus(max_chars=80_000):
    global _corpus_cache
    if _corpus_cache is not None:
        return _corpus_cache

    root = os.path.join(os.path.dirname(__file__), "..", "corpus")
    if not os.path.isdir(root):
        _corpus_cache = "(No corpus files found)"
        return _corpus_cache

    chunks = []
    total = 0
    for md_path in sorted(glob.glob(os.path.join(root, "**", "*.md"), recursive=True)):
        try:
            text = open(md_path, encoding="utf-8").read()
        except OSError:
            continue
        body = _parse_frontmatter(text)
        rel = os.path.relpath(md_path, root)
        chunk = f"\n{'=' * 40}\nFile: {rel}\n{'=' * 40}\n{body}"
        if total + len(chunk) > max_chars:
            remaining = max_chars - total
            if remaining > 200:
                chunks.append(chunk[:remaining] + "\n...(truncated)")
            break
        chunks.append(chunk)
        total += len(chunk)

    _corpus_cache = "\n".join(chunks) if chunks else "(Empty corpus)"
    return _corpus_cache


# ── LLM client ──────────────────────────────────────────────────
def get_client_and_model(provider_override=None, model_override=None):
    """
    Supports multiple backends via env vars, with optional client overrides.

    NVIDIA Nemotron (default if NVIDIA_API_KEY set):
      NVIDIA_API_KEY=nvapi-xxx

    OpenAI:
      OPENAI_API_KEY=sk-xxx

    Groq (free tier, fast):
      GROQ_API_KEY=gsk_xxx

    OpenRouter (any model):
      OPENROUTER_API_KEY=sk-or-xxx
      OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct

    Any OpenAI-compatible:
      OPENAI_API_KEY=xxx
      OPENAI_BASE_URL=https://your-endpoint/v1
      OPENAI_MODEL=your-model
    """
    provider_configs = {
        "nvidia": {
            "key_env": "NVIDIA_API_KEY",
            "base_url": "https://integrate.api.nvidia.com/v1",
            "default_model": "nvidia/llama-3.1-nemotron-nano-8b-v1",
        },
        "groq": {
            "key_env": "GROQ_API_KEY",
            "base_url": "https://api.groq.com/openai/v1",
            "default_model": "llama-3.3-70b-versatile",
        },
        "openrouter": {
            "key_env": "OPENROUTER_API_KEY",
            "base_url": "https://openrouter.ai/api/v1",
            "default_model": "meta-llama/llama-3-8b-instruct",
        },
        "openai": {
            "key_env": "OPENAI_API_KEY",
            "base_url": None,
            "default_model": "gpt-4o-mini",
        },
    }

    # If client requested a specific provider, try that first
    if provider_override and provider_override in provider_configs:
        cfg = provider_configs[provider_override]
        key = os.environ.get(cfg["key_env"])
        if key:
            kwargs = {"api_key": key}
            if cfg["base_url"]:
                kwargs["base_url"] = cfg["base_url"]
            client = OpenAI(**kwargs)
            model = model_override or cfg["default_model"]
            return client, model

    # Auto-detect: try providers in priority order
    for pname in ["nvidia", "groq", "openrouter", "openai"]:
        cfg = provider_configs[pname]
        key = os.environ.get(cfg["key_env"])
        if key:
            kwargs = {"api_key": key}
            if cfg["base_url"]:
                kwargs["base_url"] = cfg["base_url"]
            # For openai, also check custom base URL
            if pname == "openai":
                custom_base = os.environ.get("OPENAI_BASE_URL")
                if custom_base:
                    kwargs["base_url"] = custom_base
            client = OpenAI(**kwargs)
            model = model_override or os.environ.get(f"{pname.upper()}_MODEL", cfg["default_model"])
            return client, model

    return None, None


# ── Handler ─────────────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if OpenAI is None:
            return self._json({"error": "openai package not installed"}, 500)

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            return self._json({"error": "Invalid JSON"}, 400)

        user_msg = body.get("message", "").strip()
        if not user_msg:
            return self._json({"error": "Empty message"}, 400)

        # Client-requested provider/model overrides
        provider_override = body.get("provider")
        model_override = body.get("model")

        client, model = get_client_and_model(provider_override, model_override)
        if client is None:
            return self._json({
                "error": "No server API key configured. Use BYOK: open Model & Settings in the chat panel and paste your own key (Groq and NVIDIA have free tiers)."
            }, 500)

        selections = body.get("selections", "")
        article_title = body.get("article_title", "")
        history = body.get("history", [])

        # System prompt with corpus
        corpus = load_corpus()
        system = (
            "You are an AI assistant for detroit.dev, a community knowledge base. "
            "You have the full corpus of community notes as context below. "
            "Answer questions clearly and concisely. "
            "Use analogies and examples for technical concepts. "
            "If the user selected text from an article, focus on that.\n\n"
            f"=== CORPUS ===\n{corpus}\n=== END CORPUS ==="
        )

        messages = [{"role": "system", "content": system}]

        # History (last 16 turns)
        for h in history[-16:]:
            role = h.get("role", "")
            content = h.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content[:2000]})

        # Current message with selection context
        current = user_msg
        if selections:
            current = f'[Selected from "{article_title}":\n"{selections[:1000]}"]\n\n{user_msg}'
        elif article_title:
            current = f'[Reading: "{article_title}"]\n\n{user_msg}'
        messages.append({"role": "user", "content": current})

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
            )
            reply = response.choices[0].message.content
            return self._json({"reply": reply, "model": model})
        except Exception as e:
            return self._json({"error": str(e)}, 500)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
