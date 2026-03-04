#!/usr/bin/env python3
"""Generate pixel-art sprite candidates using OpenAI's gpt-image-1.5 model.

Produces multiple candidates via separate API calls (one sprite per image).
Each candidate is saved as a numbered PNG in the output directory.
Supports reference images for style matching and native transparent backgrounds.
"""
from __future__ import annotations

import argparse
import base64
import os
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai is not installed.")
    print("Run: pip install -r scripts/requirements.txt")
    sys.exit(1)


def load_dotenv() -> None:
    """Load .env file from current directory into os.environ if it exists."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def generate_candidates(
    prompt: str,
    output_dir: str,
    references: list[str] | None = None,
    count: int = 4,
    model: str = "gpt-image-1.5",
    api_key: str | None = None,
    size: str = "1024x1024",
    quality: str = "medium",
    name: str = "candidate",
) -> int:
    """Generate sprite candidates. Returns count of successfully generated images."""
    if not api_key:
        load_dotenv()
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        print("ERROR: No API key found. Checked: --api-key flag, OPENAI_API_KEY env var, .env file in current directory.")
        print("Then either:")
        print("  1. Create a .env file with: OPENAI_API_KEY=your-key-here")
        print("  2. Export it: export OPENAI_API_KEY=your-key-here")
        print("  3. Pass it: --api-key your-key-here")
        sys.exit(1)

    client = OpenAI(api_key=key)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Validate reference paths
    valid_refs = []
    if references:
        for ref_path in references:
            if not Path(ref_path).exists():
                print(f"WARNING: Reference not found, skipping: {ref_path}")
            else:
                valid_refs.append(ref_path)

    use_edit = len(valid_refs) > 0

    if use_edit:
        print(f"Using images.edit with {len(valid_refs)} reference image(s)")
    else:
        print("Using images.generate (no reference images)")

    success = 0
    for i in range(count):
        candidate_num = i + 1
        print(f"Generating candidate {candidate_num}/{count}...", end=" ", flush=True)

        try:
            if use_edit:
                # Pass reference images via images.edit endpoint
                image_files = [open(ref, "rb") for ref in valid_refs]
                try:
                    response = client.images.edit(
                        model=model,
                        image=image_files,
                        prompt=prompt,
                        n=1,
                        size=size,
                        quality=quality,
                        background="transparent",
                    )
                finally:
                    for f in image_files:
                        f.close()
            else:
                # No references — use images.generate with native transparency
                response = client.images.generate(
                    model=model,
                    prompt=prompt,
                    n=1,
                    size=size,
                    quality=quality,
                    background="transparent",
                    output_format="png",
                )

            result = response.data[0]
            filename = out / f"{name}_{candidate_num:03d}.png"

            if result.b64_json:
                image_data = base64.b64decode(result.b64_json)
                with open(filename, "wb") as f:
                    f.write(image_data)
                success += 1
                print(f"saved -> {filename}")
            elif result.url:
                import urllib.request
                urllib.request.urlretrieve(result.url, str(filename))
                success += 1
                print(f"saved -> {filename}")
            else:
                print("SKIP (no image data in response)")

        except Exception as e:
            print(f"ERROR: {e}")

        # Brief delay between calls to avoid rate limiting
        if candidate_num < count:
            time.sleep(1)

    print(f"\nGenerated {success}/{count} candidates in {output_dir}")
    return success


def main():
    parser = argparse.ArgumentParser(description="Generate pixel-art sprite candidates via OpenAI gpt-image-1.5")
    parser.add_argument("--prompt", required=True, help="Generation prompt")
    parser.add_argument("--output-dir", required=True, help="Output directory for candidates")
    parser.add_argument("--reference", action="append", default=[], help="Path to upscaled reference image (repeatable)")
    parser.add_argument("--count", type=int, default=4, help="Number of candidates to generate (default: 4)")
    parser.add_argument("--model", default="gpt-image-1.5",
                        help="OpenAI image model ID (default: gpt-image-1.5)")
    parser.add_argument("--api-key", default=None, help="OpenAI API key (default: OPENAI_API_KEY env var)")
    parser.add_argument("--size", default="1024x1024",
                        choices=["1024x1024", "1536x1024", "1024x1536", "auto"],
                        help="Generation resolution (default: 1024x1024)")
    parser.add_argument("--quality", default="medium",
                        choices=["low", "medium", "high"],
                        help="Image quality (default: medium)")
    parser.add_argument("--name", default="candidate",
                        help="Base name for output files (default: candidate). "
                             "E.g. --name slime produces slime_001.png")
    args = parser.parse_args()

    generate_candidates(
        prompt=args.prompt,
        output_dir=args.output_dir,
        references=args.reference,
        count=args.count,
        model=args.model,
        api_key=args.api_key,
        size=args.size,
        quality=args.quality,
        name=args.name,
    )


if __name__ == "__main__":
    main()
