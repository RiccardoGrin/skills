#!/usr/bin/env python3
"""Nearest-neighbor upscale tiny pixel-art sprites for use as AI reference images.

Small sprites (32x32, etc.) are too tiny for AI models to interpret.
This script upscales them to 500-1024px using nearest-neighbor interpolation,
preserving pixel-art crispness without introducing blur.
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is not installed.")
    print("Run: pip install -r scripts/requirements.txt")
    sys.exit(1)


def find_multiplier(max_dim: int, min_size: int, max_size: int) -> int:
    """Find the largest integer multiplier that keeps max_dim * m within bounds."""
    if max_dim >= min_size:
        return 1

    best_m = 1
    for m in range(1, max_size // max_dim + 1):
        if max_dim * m <= max_size:
            best_m = m
        else:
            break

    if max_dim * best_m < min_size and best_m > 1:
        pass  # best effort — still better than 1x

    return best_m


def upscale(input_path: str, output_path: str, min_size: int = 500, max_size: int = 1024) -> None:
    img = Image.open(input_path)
    width, height = img.size
    max_dim = max(width, height)

    m = find_multiplier(max_dim, min_size, max_size)

    if m == 1 and max_dim < min_size:
        print(f"WARNING: {width}x{height} — no integer multiplier fits {min_size}-{max_size}px range, using 1x")

    new_w = width * m
    new_h = height * m
    upscaled = img.resize((new_w, new_h), Image.NEAREST)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    upscaled.save(output_path, "PNG")
    print(f"Upscaled {width}x{height} -> {new_w}x{new_h} (multiplier: {m}x)")


def main():
    parser = argparse.ArgumentParser(description="Nearest-neighbor upscale pixel-art sprites for reference use")
    parser.add_argument("--input", required=True, help="Path to input sprite image")
    parser.add_argument("--output", required=True, help="Path to save upscaled image")
    parser.add_argument("--min-size", type=int, default=500, help="Minimum target dimension (default: 500)")
    parser.add_argument("--max-size", type=int, default=1024, help="Maximum target dimension (default: 1024)")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    upscale(args.input, args.output, args.min_size, args.max_size)


if __name__ == "__main__":
    main()
