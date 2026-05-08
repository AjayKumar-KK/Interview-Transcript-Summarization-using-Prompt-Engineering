"""
Interview Transcript Summarizer
================================

Takes an interview transcript file and uses Gemini to produce a structured
summary with three sections: Topics Covered, Profile, and Candidate Summary.

Usage:
    python summarizer.py path/to/transcript.txt
    python summarizer.py path/to/transcript.txt --output summary.md
    python summarizer.py path/to/transcript.txt --model gemini-2.5-flash

Setup:
    1. pip install -r requirements.txt
    2. Copy .env.example to .env and add your GEMINI_API_KEY.

Built for the intervue.io AI Systems Intern take-home.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ---------------------------------------------------------------------------
# The prompt (this is the v3 / final version — see prompt_iterations.md for
# the evolution and reasoning behind each change).
# ---------------------------------------------------------------------------
PROMPT = """Summarize the following interview transcript by identifying the Topics covered, the candidate Profile with suitable role and seniority plus brief justification, and a 3–6 sentence Candidate summary covering background, strengths, concerns, and overall impression based only on the transcript.\n\nTranscript:\n{transcript}"""

def load_transcript(path: str) -> str:
    """Read a transcript file and return its contents as a stripped string."""
    p = Path(path)
    if not p.exists():
        sys.exit(f"Error: transcript file not found: {path}")
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        sys.exit(f"Error: transcript file is empty: {path}")
    return text


def summarize(transcript: str, model: str = "gemini-2.5-flash") -> str:
    """Send the transcript to Gemini and return the structured summary."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit(
            "Error: GEMINI_API_KEY is not set.\n"
            "Add it to a .env file in this folder, or export it in your shell:\n"
            "    export GEMINI_API_KEY=your_key_here"
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=PROMPT.format(transcript=transcript),
    )
    return (response.text or "").strip()


def main() -> None:
    load_dotenv()  # picks up .env in the current folder

    parser = argparse.ArgumentParser(
        description="Summarize an interview transcript into Topics / Profile / Summary."
    )
    parser.add_argument("transcript", help="Path to a .txt transcript file.")
    parser.add_argument(
        "--output",
        "-o",
        help="Optional path to write the summary to. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model to use (default: gemini-2.5-flash).",
    )
    args = parser.parse_args()

    transcript = load_transcript(args.transcript)
    summary = summarize(transcript, model=args.model)

    if args.output:
        Path(args.output).write_text(summary, encoding="utf-8")
        print(f"Summary written to {args.output}")
    else:
        print(summary)


if __name__ == "__main__":
    main()