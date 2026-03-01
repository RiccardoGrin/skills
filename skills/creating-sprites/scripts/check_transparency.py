#!/usr/bin/env python3
"""Verify PNG transparency programmatically.

AI models sometimes fake transparency with a checkerboard pattern.
This script checks whether an image has real alpha-channel transparency
and reports stats the agent can parse.
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


def check_checkerboard(img: Image.Image, sample_step: int = 8) -> bool:
    """Detect regular alternating transparent/opaque pattern suggesting fake transparency."""
    if img.mode not in ("RGBA", "LA", "PA"):
        return False

    width, height = img.size
    pixels = img.load()
    alpha_idx = {"RGBA": 3, "LA": 1, "PA": 1}[img.mode]

    mismatches = 0
    total = 0

    for y in range(0, height, sample_step):
        for x in range(0, width, sample_step):
            px = pixels[x, y]
            is_transparent = px[alpha_idx] < 10
            # In a checkerboard, transparency alternates with grid position parity
            expected_transparent = (x // sample_step + y // sample_step) % 2 == 0
            if is_transparent == expected_transparent:
                total += 1
            else:
                mismatches += 1
                total += 1

    if total == 0:
        return False

    # If >40% of sampled pixels match a checkerboard pattern, flag it
    match_rate = (total - mismatches) / total
    return match_rate > 0.40


def check_transparency(input_path: str, threshold: float = 10.0) -> bool:
    """Check if image has real transparency. Returns True if it passes."""
    path = Path(input_path)
    name = path.name

    # Check file extension
    if path.suffix.lower() not in (".png",):
        print(f"FILE: {name}")
        print(f"FORMAT: {path.suffix.upper().lstrip('.')}")
        print("ALPHA_CHANNEL: no")
        print("TRANSPARENT_PIXELS: 0%")
        print("CHECKERBOARD_DETECTED: n/a")
        print("RESULT: FAIL (not a PNG, cannot have transparency)")
        return False

    img = Image.open(input_path)

    has_alpha = img.mode in ("RGBA", "LA", "PA")
    if not has_alpha:
        print(f"FILE: {name}")
        print("FORMAT: PNG")
        print("ALPHA_CHANNEL: no")
        print("TRANSPARENT_PIXELS: 0%")
        print("CHECKERBOARD_DETECTED: n/a")
        print("RESULT: FAIL (no alpha channel)")
        return False

    # Count transparent pixels
    pixels = img.load()
    width, height = img.size
    alpha_idx = {"RGBA": 3, "LA": 1, "PA": 1}[img.mode]
    total_pixels = width * height
    transparent_count = 0

    for y in range(height):
        for x in range(width):
            if pixels[x, y][alpha_idx] < 10:
                transparent_count += 1

    transparent_pct = (transparent_count / total_pixels) * 100

    # Check for checkerboard
    is_checkerboard = check_checkerboard(img)

    passed = transparent_pct >= threshold and not is_checkerboard

    print(f"FILE: {name}")
    print("FORMAT: PNG")
    print("ALPHA_CHANNEL: yes")
    print(f"TRANSPARENT_PIXELS: {transparent_pct:.1f}%")
    print(f"CHECKERBOARD_DETECTED: {'yes' if is_checkerboard else 'no'}")
    print(f"RESULT: {'PASS' if passed else 'FAIL'}")

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify PNG transparency")
    parser.add_argument("--input", required=True, help="Path to image file")
    parser.add_argument("--threshold", type=float, default=10.0,
                        help="Minimum %% of transparent pixels to pass (default: 10)")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    passed = check_transparency(args.input, args.threshold)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
