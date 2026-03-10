"""Download audio from a YouTube video using yt-dlp.

Usage:
    python download_audio.py --url "https://youtube.com/watch?v=..." --output-dir transcriptions

Outputs audio as WAV file(s). Splits files >25MB into chunks for Whisper API compatibility.
Prints metadata to stdout in KEY: VALUE format.
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def check_dependency(name: str) -> None:
    """Check that a CLI tool is available on PATH, exit with a clear message if not."""
    if shutil.which(name) is None:
        print(f"ERROR: '{name}' is not installed or not on PATH. Install it before running this script.", file=sys.stderr)
        sys.exit(1)


def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    print(f"ERROR: Could not extract video ID from URL: {url}", file=sys.stderr)
    sys.exit(1)


def get_video_info(url: str) -> dict:
    """Fetch video metadata without downloading."""
    result = subprocess.run(
        ['yt-dlp', '--dump-json', '--no-download', url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: Failed to fetch video info: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def download_audio(url: str, output_path: str) -> None:
    """Download audio and convert to WAV."""
    result = subprocess.run(
        [
            'yt-dlp',
            '-x',                          # extract audio
            '--audio-format', 'wav',       # convert to WAV
            '--audio-quality', '0',        # best quality
            '-o', output_path,             # output path
            '--no-playlist',               # single video only
            '--no-warnings',
            url,
        ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: Download failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def get_file_size_mb(path: str) -> float:
    """Get file size in megabytes."""
    return os.path.getsize(path) / (1024 * 1024)


def split_audio(input_path: str, output_dir: str, video_id: str, max_size_mb: float = 24.0) -> list:
    """Split audio file into chunks under max_size_mb using ffmpeg."""
    file_size_mb = get_file_size_mb(input_path)
    if file_size_mb <= max_size_mb:
        return [input_path]

    # Get duration
    result = subprocess.run(
        ['ffmpeg', '-i', input_path, '-f', 'null', '-'],
        capture_output=True, text=True
    )
    duration_match = re.search(r'Duration: (\d+):(\d+):(\d+)', result.stderr)
    if not duration_match:
        print("ERROR: Could not determine audio duration for splitting", file=sys.stderr)
        sys.exit(1)

    hours, minutes, seconds = map(int, duration_match.groups())
    total_seconds = hours * 3600 + minutes * 60 + seconds

    num_chunks = math.ceil(file_size_mb / max_size_mb)
    chunk_duration = total_seconds / num_chunks

    chunk_paths = []
    for i in range(num_chunks):
        start = i * chunk_duration
        chunk_path = os.path.join(output_dir, f"{video_id}_chunk_{i+1:03d}.wav")
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-ss', str(start),
            '-t', str(chunk_duration),
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            chunk_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: Failed to split chunk {i+1}: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        chunk_paths.append(chunk_path)

    # Remove original large file
    os.remove(input_path)
    return chunk_paths


def main():
    parser = argparse.ArgumentParser(description='Download YouTube audio for transcription')
    parser.add_argument('--url', required=True, help='YouTube video URL')
    parser.add_argument('--output-dir', default='transcriptions', help='Output directory')
    args = parser.parse_args()

    check_dependency('yt-dlp')
    check_dependency('ffmpeg')

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    video_id = extract_video_id(args.url)

    # Fetch metadata
    info = get_video_info(args.url)
    title = info.get('title', 'Unknown')
    duration = info.get('duration', 0)

    # Download audio
    output_path = os.path.join(output_dir, f"{video_id}.wav")
    # yt-dlp adds extension, so use template without .wav for yt-dlp
    output_template = os.path.join(output_dir, f"{video_id}.%(ext)s")
    result = subprocess.run(
        [
            'yt-dlp',
            '-x',
            '--audio-format', 'wav',
            '--audio-quality', '0',
            '-o', output_template,
            '--no-playlist',
            '--no-warnings',
            args.url,
        ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: Download failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Check if file needs splitting
    if os.path.exists(output_path):
        file_paths = split_audio(output_path, output_dir, video_id)
    else:
        # yt-dlp may have used a different extension path
        # Look for the file
        candidates = list(Path(output_dir).glob(f"{video_id}.*"))
        if candidates:
            actual_path = str(candidates[0])
            if actual_path != output_path:
                os.rename(actual_path, output_path)
            file_paths = split_audio(output_path, output_dir, video_id)
        else:
            print(f"ERROR: Downloaded file not found in {output_dir}", file=sys.stderr)
            sys.exit(1)

    # Report
    print(f"VIDEO_ID: {video_id}")
    print(f"TITLE: {title}")
    print(f"DURATION: {duration}")
    print(f"FILES: {', '.join(file_paths)}")
    print(f"STATUS: OK")


if __name__ == '__main__':
    main()
