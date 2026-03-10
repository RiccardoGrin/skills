"""Transcribe audio file(s) using OpenAI Whisper API.

Usage:
    # Single file
    python transcribe_audio.py --input audio.wav --output transcript.txt

    # Chunked files (auto-discovers chunks by video ID)
    python transcribe_audio.py --input-dir transcriptions --video-id VIDEO_ID --output transcript.txt

    # With timestamps
    python transcribe_audio.py --input audio.wav --output transcript.txt --timestamps

Requires OPENAI_API_KEY environment variable or .env file.
"""

import argparse
import os
import re
import sys
from pathlib import Path


def load_api_key() -> str:
    """Load OpenAI API key from environment or .env file."""
    key = os.environ.get('OPENAI_API_KEY', '')
    if not key:
        env_path = Path('.env')
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                stripped = line.strip()
                if stripped.startswith('OPENAI_API_KEY'):
                    key = stripped.partition('=')[2].strip().strip('"').strip("'")
                    break
    if not key:
        print("ERROR: OPENAI_API_KEY not found in environment or .env file", file=sys.stderr)
        sys.exit(1)
    return key


def transcribe_file(client, file_path: str, timestamps: bool = False) -> str:
    """Transcribe a single audio file."""
    with open(file_path, 'rb') as audio_file:
        if timestamps:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
            )
            # Build timestamped text
            lines = []
            for segment in response.segments:
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                text = segment['text'].strip()
                lines.append(f"[{start} -> {end}] {text}")
            return '\n'.join(lines)
        else:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
            )
            return response


def format_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def main():
    parser = argparse.ArgumentParser(description='Transcribe audio with OpenAI Whisper')
    parser.add_argument('--input', help='Path to single audio file')
    parser.add_argument('--input-dir', help='Directory containing chunked audio files')
    parser.add_argument('--video-id', help='Video ID for finding chunked files')
    parser.add_argument('--output', required=True, help='Output transcript file path')
    parser.add_argument('--timestamps', action='store_true', help='Include timestamps')
    args = parser.parse_args()

    if not args.input and not (args.input_dir and args.video_id):
        print("ERROR: Provide --input or both --input-dir and --video-id", file=sys.stderr)
        sys.exit(1)

    api_key = load_api_key()

    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Determine file(s) to transcribe
    if args.input:
        files = [args.input]
    else:
        input_dir = Path(args.input_dir)
        # Find chunks sorted by number
        chunks = sorted(input_dir.glob(f"{args.video_id}_chunk_*.wav"))
        if not chunks:
            # Try single file
            single = input_dir / f"{args.video_id}.wav"
            if single.exists():
                files = [str(single)]
            else:
                print(f"ERROR: No audio files found for video ID {args.video_id}", file=sys.stderr)
                sys.exit(1)
        else:
            files = [str(c) for c in chunks]

    # Transcribe each file
    transcripts = []
    for i, file_path in enumerate(files, 1):
        if len(files) > 1:
            print(f"Transcribing chunk {i}/{len(files)}: {file_path}", file=sys.stderr)
        text = transcribe_file(client, file_path, args.timestamps)
        transcripts.append(text)

    # Combine and save
    full_transcript = '\n\n'.join(transcripts)
    word_count = len(full_transcript.split())

    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(full_transcript)

    print(f"WORDS: {word_count}")
    print(f"OUTPUT: {args.output}")
    print(f"STATUS: OK")


if __name__ == '__main__':
    main()
