#!/usr/bin/env python3
"""Transcribe audio/video and optionally generate Q&A study notes.

Uses faster-whisper locally (no API key needed).
Falls back to OpenAI Whisper API if OPENAI_API_KEY is set and --api flag is used.

Usage:
    python tools/transcribe.py recording.mp3
    python tools/transcribe.py recording.mp3 --qa
    python tools/transcribe.py https://example.com/podcast.mp3 --qa
    python tools/transcribe.py recording.mp3 --whisper-model medium
    python tools/transcribe.py recording.mp3 --api   # use OpenAI API instead
"""

import argparse
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"


def download_if_url(source: str) -> Path:
    """If source is a URL, download it to a temp file. Otherwise return as Path."""
    if source.startswith("http://") or source.startswith("https://"):
        import httpx
        print(f"Downloading {source}...")
        with httpx.stream("GET", source, follow_redirects=True) as r:
            r.raise_for_status()
            ext = Path(source.split("?")[0]).suffix or ".mp3"
            tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
            for chunk in r.iter_bytes(chunk_size=8192):
                tmp.write(chunk)
            tmp.close()
            print(f"Saved to {tmp.name}")
            return Path(tmp.name)
    return Path(source)


def transcribe_local(audio_path: Path, model_size: str = "small") -> str:
    """Transcribe audio using faster-whisper (local, no API key)."""
    from faster_whisper import WhisperModel

    print(f"Loading whisper model ({model_size})...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print(f"Transcribing {audio_path.name}...")
    segments, info = model.transcribe(str(audio_path), beam_size=5)

    print(f"Detected language: {info.language} (probability {info.language_probability:.2f})")

    texts = []
    for segment in segments:
        texts.append(segment.text.strip())

    return " ".join(texts)


def transcribe_api(audio_path: Path) -> str:
    """Transcribe audio using OpenAI Whisper API (requires OPENAI_API_KEY)."""
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: --api requires OPENAI_API_KEY.")
        print("Set it: export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    print(f"Transcribing {audio_path.name} via OpenAI API...")
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(model="whisper-1", file=f)
    return result.text


def generate_qa(transcript: str, model: str = "gpt-4o-mini") -> str:
    """Generate Q&A study notes from a transcript using an LLM."""
    # Try to get any available LLM client
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        # Fallback to Ollama
        client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        model = os.environ.get("OLLAMA_MODEL", "nemotron-mini")

    print("Generating Q&A...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a study assistant. Given a transcript, generate:\n"
                    "1. A concise summary (2-3 paragraphs)\n"
                    "2. 5-10 key questions and detailed answers based on the content\n"
                    "3. Key takeaways as bullet points\n\n"
                    "Format everything in clean markdown."
                ),
            },
            {"role": "user", "content": f"Transcript:\n\n{transcript}"},
        ],
    )
    return response.choices[0].message.content


def save_transcript(transcript: str, source: str, qa_content: str | None = None):
    """Save transcript (and optional Q&A) as markdown files."""
    slug = re.sub(r"[^\w\-]", "-", Path(source.split("?")[0]).stem.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    today = date.today().isoformat()

    # Save transcript
    tx_dir = CORPUS_DIR / "transcripts"
    tx_dir.mkdir(parents=True, exist_ok=True)
    tx_path = tx_dir / f"{slug}.md"

    frontmatter = (
        f"---\n"
        f'title: "Transcript: {slug}"\n'
        f"date: {today}\n"
        f"tags: [transcript]\n"
        f'source: "{source}"\n'
        f"---\n\n"
    )
    tx_path.write_text(frontmatter + transcript, encoding="utf-8")
    print(f"Saved transcript: {tx_path}")

    # Save Q&A
    if qa_content:
        qa_dir = CORPUS_DIR / "generated"
        qa_dir.mkdir(parents=True, exist_ok=True)
        qa_path = qa_dir / f"{slug}-qa.md"

        qa_frontmatter = (
            f"---\n"
            f'title: "Q&A: {slug}"\n'
            f"date: {today}\n"
            f"tags: [generated, qa]\n"
            f'source: "{source}"\n'
            f"---\n\n"
        )
        qa_path.write_text(qa_frontmatter + qa_content, encoding="utf-8")
        print(f"Saved Q&A: {qa_path}")


def main():
    parser = argparse.ArgumentParser(description="Transcribe audio/video for the corpus")
    parser.add_argument("source", help="Path or URL to audio/video file")
    parser.add_argument("--qa", action="store_true", help="Also generate Q&A study notes")
    parser.add_argument("--api", action="store_true", help="Use OpenAI Whisper API instead of local")
    parser.add_argument("--whisper-model", default="small",
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        help="Local whisper model size (default: small)")
    parser.add_argument("--model", default="gpt-4o-mini", help="LLM model for Q&A generation")
    args = parser.parse_args()

    audio_path = download_if_url(args.source)

    if args.api:
        transcript = transcribe_api(audio_path)
    else:
        transcript = transcribe_local(audio_path, args.whisper_model)

    qa_content = generate_qa(transcript, args.model) if args.qa else None
    save_transcript(transcript, args.source, qa_content)


if __name__ == "__main__":
    main()
