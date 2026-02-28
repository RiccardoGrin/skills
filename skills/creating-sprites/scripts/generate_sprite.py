#!/usr/bin/env python3
"""Generate pixel-art sprite candidates using Gemini native image generation.

Produces multiple candidates via separate API calls (one sprite per image).
Each candidate is saved as a numbered PNG in the output directory.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: google-genai is not installed.")
    print("Run: pip install -r scripts/requirements.txt")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is not installed.")
    print("Run: pip install -r scripts/requirements.txt")
    sys.exit(1)


def load_reference_image(path: str) -> Image.Image:
    """Load an image file as a PIL Image for the Gemini SDK."""
    return Image.open(path)


def generate_candidates(
    prompt: str,
    output_dir: str,
    references: list[str] | None = None,
    count: int = 4,
    model: str = "gemini-3.1-flash-image-preview",
    api_key: str | None = None,
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
) -> int:
    """Generate sprite candidates. Returns count of successfully generated images."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        print("ERROR: No API key. Set GEMINI_API_KEY env var or pass --api-key.")
        sys.exit(1)

    client = genai.Client(api_key=key)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Build contents: reference images first, then text prompt
    contents = []
    if references:
        for ref_path in references:
            if not Path(ref_path).exists():
                print(f"WARNING: Reference not found, skipping: {ref_path}")
                continue
            contents.append(load_reference_image(ref_path))

    contents.append(prompt)

    # Configure for image generation
    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size,
        ),
    )

    success = 0
    for i in range(count):
        candidate_num = i + 1
        print(f"Generating candidate {candidate_num}/{count}...", end=" ", flush=True)

        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

            # Find image part in response
            image = None
            for part in response.parts:
                if part.inline_data:
                    image = part.as_image()
                    break

            if image is None:
                print("SKIP (no image in response)")
                continue

            # Save candidate
            filename = out / f"candidate_{candidate_num:03d}.png"
            image.save(str(filename))

            success += 1
            print(f"saved -> {filename}")

        except Exception as e:
            print(f"ERROR: {e}")

        # Brief delay between calls to avoid rate limiting
        if candidate_num < count:
            time.sleep(1)

    print(f"\nGenerated {success}/{count} candidates in {output_dir}")
    return success


def main():
    parser = argparse.ArgumentParser(description="Generate pixel-art sprite candidates via Gemini")
    parser.add_argument("--prompt", required=True, help="Generation prompt")
    parser.add_argument("--output-dir", required=True, help="Output directory for candidates")
    parser.add_argument("--reference", action="append", default=[], help="Path to upscaled reference image (repeatable)")
    parser.add_argument("--count", type=int, default=4, help="Number of candidates to generate (default: 4)")
    parser.add_argument("--model", default="gemini-3.1-flash-image-preview",
                        help="Gemini model ID")
    parser.add_argument("--api-key", default=None, help="Gemini API key (default: GEMINI_API_KEY env var)")
    parser.add_argument("--aspect-ratio", default="1:1", help="Aspect ratio (default: 1:1)")
    parser.add_argument("--image-size", default="1K",
                        choices=["512px", "1K", "2K", "4K"],
                        help="Generation resolution (default: 1K)")
    args = parser.parse_args()

    generate_candidates(
        prompt=args.prompt,
        output_dir=args.output_dir,
        references=args.reference,
        count=args.count,
        model=args.model,
        api_key=args.api_key,
        aspect_ratio=args.aspect_ratio,
        image_size=args.image_size,
    )


if __name__ == "__main__":
    main()
