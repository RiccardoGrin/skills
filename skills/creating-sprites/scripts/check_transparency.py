#!/usr/bin/env python3
"""Verify PNG transparency programmatically.

AI models sometimes fake transparency with a checkerboard pattern.
This script checks whether an image has real alpha-channel transparency
and reports stats the agent can parse.
"""

import argparse
import math
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is not installed.")
    print("Run: pip install -r scripts/requirements.txt")
    sys.exit(1)


def _color_distance(c1: tuple, c2: tuple) -> float:
    """Euclidean distance between two RGB tuples."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3])))


def _parse_hex_color(hex_str: str) -> tuple:
    """Parse hex color string (with or without #) to RGB tuple."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        raise ValueError(f"Invalid hex color: #{hex_str}")
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))


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


def check_chroma_fringe(
    img: Image.Image, chroma_color: tuple, tolerance: float = 68.0, threshold_pct: float = 5.0
) -> tuple[int, float, bool]:
    """Detect leftover chroma-colored pixels along transparency edges.

    Scans edge-adjacent opaque pixels (alpha > 128) for color similarity to the
    chroma color. Default tolerance of 68 matches the fringe cleaning range used
    by process_sprite.py (45 * 1.5 = 67.5).

    Returns (fringe_count, fringe_percentage, has_fringe).
    """
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    edge_opaque_count = 0
    fringe_count = 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue

            has_transparent_neighbor = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if pixels[nx, ny][3] == 0:
                            has_transparent_neighbor = True
                            break
                if has_transparent_neighbor:
                    break

            if has_transparent_neighbor:
                edge_opaque_count += 1
                if a > 128:
                    dist = _color_distance((r, g, b), chroma_color)
                    if dist <= tolerance:
                        fringe_count += 1

    if edge_opaque_count == 0:
        return (0, 0.0, False)

    fringe_pct = (fringe_count / edge_opaque_count) * 100
    return (fringe_count, fringe_pct, fringe_pct > threshold_pct)


def check_transparency(
    input_path: str, threshold: float = 10.0,
    chroma_color: tuple | None = None, fringe_threshold: float = 5.0,
) -> bool:
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

    # Optional chroma fringe detection
    if chroma_color is not None:
        fringe_count, fringe_pct, has_fringe = check_chroma_fringe(
            img, chroma_color, threshold_pct=fringe_threshold,
        )
        print(f"FRINGE_PIXELS: {fringe_count} ({fringe_pct:.1f}% of edge pixels)")
        print(f"FRINGE_RESULT: {'FAIL' if has_fringe else 'PASS'}")
        if has_fringe:
            passed = False

    print(f"RESULT: {'PASS' if passed else 'FAIL'}")

    return passed


def main():
    parser = argparse.ArgumentParser(description="Verify PNG transparency")
    parser.add_argument("--input", required=True, help="Path to image file")
    parser.add_argument("--threshold", type=float, default=10.0,
                        help="Minimum %% of transparent pixels to pass (default: 10)")
    parser.add_argument("--chroma-color", default=None,
                        help="Hex color to check for fringe artifacts (e.g. FF00FF)")
    parser.add_argument("--fringe-threshold", type=float, default=5.0,
                        help="Max %% of edge pixels that can be chroma-colored before failing (default: 5)")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    chroma = _parse_hex_color(args.chroma_color) if args.chroma_color else None
    passed = check_transparency(args.input, args.threshold, chroma, args.fringe_threshold)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
