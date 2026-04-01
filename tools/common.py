"""Shared utilities for corpus tools."""

import json
import os
import re
import yaml
import numpy as np
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"
INDEX_DIR = Path(__file__).resolve().parent.parent / "corpus" / "generated"
INDEX_FILE = INDEX_DIR / "embeddings.json"


def iter_corpus_files():
    """Yield (path, frontmatter_dict, body_text) for every .md file in the corpus."""
    for md_path in sorted(CORPUS_DIR.rglob("*.md")):
        # Skip template files and generated dir
        if md_path.name.startswith("_"):
            continue
        if "generated" in md_path.relative_to(CORPUS_DIR).parts:
            continue
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


# ── Chunking ────────────────────────────────────────────────────

def chunk_document(path: Path, fm: dict, body: str, max_chunk: int = 800) -> list[dict]:
    """Split a markdown document into semantic chunks by headers.

    Each chunk gets metadata (source file, title, section heading).
    Chunks larger than max_chunk words are split further at paragraph boundaries.
    """
    title = fm.get("title", path.stem)
    rel = corpus_relative(path)
    tags = fm.get("tags", [])

    # Split on markdown headers (##, ###, etc.)
    sections = re.split(r"(?m)^(#{1,4}\s+.+)$", body)

    chunks = []
    current_heading = title

    i = 0
    while i < len(sections):
        part = sections[i].strip()
        if re.match(r"^#{1,4}\s+", part):
            current_heading = re.sub(r"^#+\s*", "", part).strip()
            i += 1
            continue

        if not part:
            i += 1
            continue

        # Split oversized sections at paragraph boundaries
        for sub in _split_paragraphs(part, max_chunk):
            chunks.append({
                "source": rel,
                "title": title,
                "section": current_heading,
                "tags": tags,
                "text": sub.strip(),
            })
        i += 1

    # If no chunks were created (no headers), chunk the whole body
    if not chunks and body.strip():
        for sub in _split_paragraphs(body.strip(), max_chunk):
            chunks.append({
                "source": rel,
                "title": title,
                "section": title,
                "tags": tags,
                "text": sub.strip(),
            })

    return chunks


def _split_paragraphs(text: str, max_words: int) -> list[str]:
    """Split text into pieces of roughly max_words, breaking at paragraph boundaries."""
    paragraphs = re.split(r"\n\s*\n", text)
    pieces = []
    current = []
    current_len = 0

    for para in paragraphs:
        words = len(para.split())
        if current_len + words > max_words and current:
            pieces.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += words

    if current:
        pieces.append("\n\n".join(current))
    return pieces


# ── Embedding ───────────────────────────────────────────────────

def get_embedding_client():
    """Return an OpenAI client configured for embeddings.

    Priority: OPENAI_API_KEY > NVIDIA_API_KEY > Ollama (local).
    """
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        base_url = os.environ.get("OPENAI_BASE_URL")
        model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
        client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        return client, model

    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    if nvidia_key:
        client = OpenAI(api_key=nvidia_key, base_url="https://integrate.api.nvidia.com/v1")
        model = os.environ.get("EMBEDDING_MODEL", "nvidia/nv-embedqa-e5-v5")
        return client, model

    # Fallback: local Ollama
    client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    model = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")
    return client, model


def embed_texts(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    """Embed a list of texts, returns list of vectors."""
    client, model = get_embedding_client()
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(input=batch, model=model)
        all_embeddings.extend([d.embedding for d in resp.data])
    return all_embeddings


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]


# ── Vector index (JSON file) ───────────────────────────────────

def save_index(chunks: list[dict], embeddings: list[list[float]]):
    """Save chunks + embeddings to a JSON index file."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "chunks": chunks,
        "embeddings": embeddings,
    }
    INDEX_FILE.write_text(json.dumps(data), encoding="utf-8")


def load_index() -> tuple[list[dict], np.ndarray] | None:
    """Load the embedding index. Returns (chunks, embeddings_matrix) or None."""
    if not INDEX_FILE.exists():
        return None
    data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    chunks = data["chunks"]
    embeddings = np.array(data["embeddings"], dtype=np.float32)
    return chunks, embeddings


def semantic_search(query: str, top_k: int = 5) -> list[tuple[dict, float]]:
    """Search the index for chunks most similar to the query.

    Returns list of (chunk_dict, similarity_score) sorted by relevance.
    """
    index = load_index()
    if index is None:
        return []
    chunks, matrix = index

    query_vec = np.array(embed_query(query), dtype=np.float32)

    # Cosine similarity (vectors are typically normalized, but normalize anyway)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normed = matrix / norms
    q_norm = query_vec / (np.linalg.norm(query_vec) or 1)

    scores = normed @ q_norm
    top_idx = np.argsort(scores)[::-1][:top_k]

    return [(chunks[i], float(scores[i])) for i in top_idx]


def retrieve_context(query: str, top_k: int = 5) -> str:
    """Retrieve relevant chunks as a formatted context string for the LLM."""
    results = semantic_search(query, top_k=top_k)
    if not results:
        # Fallback: load entire corpus (old behavior, for when no index exists)
        return _fallback_corpus_context()

    parts = []
    for chunk, score in results:
        header = f"[Source: {chunk['source']} | Section: {chunk['section']} | Relevance: {score:.2f}]"
        parts.append(f"{header}\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)


def _fallback_corpus_context(max_chars: int = 80_000) -> str:
    """Load the entire corpus as a string (fallback when no index exists)."""
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
