#!/usr/bin/env python3
"""Transcribe audio/video and optionally generate Q&A study notes.

Uses OpenAI Whisper API by default. Set OPENAI_API_KEY.

Usage:
    python tools/transcribe.py recording.mp3
    python tools/transcribe.py recording.mp3 --qa
    python tools/transcribe.py https://example.com/podcast.mp3 --qa
"""

import argparse
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Install dependencies: pip install -r requirements.txt")
    sys.exit(1)

CORPUS_DIR = Path(__file__).resolve().parent.parent / "corpus"


def download_if_url(source: str) -> Path:
    """If source is a URL, download it to a temp file. Otherwise return as Path."""
    if source.startswith("http://") or source.startswith("https://"):
        import httpx
        print(f"Downloading {source}...")
        with httpx.stream("GET", source, follow_redirects=True) as r:
            r.raise_for_status()
            # Determine extension from URL or content-type
            ext = Path(source.split("?")[0]).suffix or ".mp3"
            tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
            for chunk in r.iter_bytes(chunk_size=8192):
                tmp.write(chunk)
            tmp.close()
            print(f"Saved to {tmp.name}")
            return Path(tmp.name)
    return Path(source)


def transcribe(audio_path: Path, client: OpenAI) -> str:
    """Transcribe audio using OpenAI Whisper API."""
    print(f"Transcribing {audio_path.name}...")
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(model="whisper-1", file=f)
    return result.text


def generate_qa(transcript: str, client: OpenAI, model: str = "gpt-4o-mini") -> str:
    """Generate Q&A study notes from a transcript."""
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
    parser.add_argument("--model", default="gpt-4o-mini", help="Model for Q&A generation")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY required for transcription.")
        print("Set it: export OPENAI_API_KEY=sk-...")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    audio_path = download_if_url(args.source)

    transcript = transcribe(audio_path, client)
    qa_content = generate_qa(transcript, client, args.model) if args.qa else None
    save_transcript(transcript, args.source, qa_content)


if __name__ == "__main__":
    main()
