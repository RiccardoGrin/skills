#!/usr/bin/env python3
"""Process AI-generated sprites into game-ready assets.

Subcommands:
  remove-bg   — Remove solid-color background via chromakey
  downscale   — Nearest-neighbor resize to target sprite dimensions
  crop        — Trim transparent pixels per crop mode (bottom-anchor, center, none)
  pipeline    — Run all steps in sequence
"""
from __future__ import annotations

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


# ── remove-bg ──────────────────────────────────────────────────────────────

def color_distance(c1: tuple, c2: tuple) -> float:
    """Euclidean distance between two RGB tuples."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3])))


def remove_bg(img: Image.Image, chroma_color: tuple, tolerance: int = 45) -> Image.Image:
    """Remove chromakey background color, replacing matched pixels with transparency."""
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    # First pass: remove chroma pixels
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if color_distance((r, g, b), chroma_color) <= tolerance:
                pixels[x, y] = (0, 0, 0, 0)

    # Fringe-cleaning pass: soften opaque pixels adjacent to newly-transparent ones
    # that are close to the chroma color (prevents colored halos)
    cleaned = img.copy()
    cleaned_pixels = cleaned.load()
    fringe_tolerance = tolerance * 1.5

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue

            # Check if any neighbor is transparent
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
                dist = color_distance((r, g, b), chroma_color)
                if dist <= fringe_tolerance:
                    # Fade out based on proximity to chroma color
                    fade = max(0, int(255 * (dist / fringe_tolerance)))
                    cleaned_pixels[x, y] = (r, g, b, fade)

    return cleaned


def detect_chroma_fringe(
    img: Image.Image, chroma_color: tuple, tolerance: int = 45, threshold_pct: float = 5.0
) -> tuple[int, float, bool]:
    """Detect leftover chroma-colored pixels along transparency edges.

    Scans edge-adjacent opaque pixels (alpha > 128) within the fringe cleaning
    range (tolerance * 1.5) — matching what remove_bg's fringe pass targets.
    If these pixels survived with high alpha, fringe cleaning didn't catch them.

    Returns (fringe_count, fringe_percentage, has_fringe).
    fringe_percentage is relative to total edge-adjacent opaque pixels.
    has_fringe is True if fringe_percentage > threshold_pct.
    """
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size
    fringe_tolerance = tolerance * 1.5

    edge_opaque_count = 0
    fringe_count = 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue

            # Check if any neighbor is transparent
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
                # Only flag pixels that are still mostly opaque AND close to chroma
                if a > 128:
                    dist = color_distance((r, g, b), chroma_color)
                    if dist <= fringe_tolerance:
                        fringe_count += 1

    if edge_opaque_count == 0:
        return (0, 0.0, False)

    fringe_pct = (fringe_count / edge_opaque_count) * 100
    return (fringe_count, fringe_pct, fringe_pct > threshold_pct)


# ── downscale ──────────────────────────────────────────────────────────────

def downscale(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """Nearest-neighbor resize to target dimensions."""
    original = img.size
    result = img.resize((target_width, target_height), Image.NEAREST)
    print(f"  Downscaled {original[0]}x{original[1]} -> {target_width}x{target_height}")
    return result


# ── crop ───────────────────────────────────────────────────────────────────

def crop_sprite(img: Image.Image, crop_mode: str) -> Image.Image:
    """Crop transparent pixels based on crop mode."""
    if crop_mode in ("center", "none"):
        print(f"  Crop ({crop_mode}): no change")
        return img.copy()

    if crop_mode == "bottom-anchor":
        img = img.convert("RGBA")
        bbox = img.getbbox()
        if bbox is None:
            print("  Crop (bottom-anchor): image is fully transparent, no change")
            return img.copy()

        left, top, right, bottom = bbox
        original = img.size
        # Crop to content on all sides — ensures sprite touches the bottom edge
        cropped = img.crop((left, top, right, bottom))
        print(f"  Crop (bottom-anchor): {original[0]}x{original[1]} -> {cropped.size[0]}x{cropped.size[1]}")
        return cropped

    print(f"  Crop: unknown mode '{crop_mode}', no change")
    return img.copy()


# ── pipeline ───────────────────────────────────────────────────────────────

def run_pipeline(
    input_path: str,
    output_path: str,
    target_width: int,
    target_height: int,
    crop_mode: str = "none",
    chroma_color: tuple | None = None,
    tolerance: int = 45,
) -> None:
    """Run full processing pipeline: remove-bg -> downscale -> crop."""
    original = Image.open(input_path).convert("RGBA")
    img = original.copy()
    print(f"Pipeline: {Path(input_path).name}")

    # Step 1: Remove background (if chromakey)
    if chroma_color is not None:
        print(f"  Removing background (chroma: #{chroma_color[0]:02x}{chroma_color[1]:02x}{chroma_color[2]:02x}, tolerance: {tolerance})")
        img = remove_bg(img, chroma_color, tolerance)

        # Step 1b: Check for leftover chroma fringe and auto-retry with higher tolerance
        fringe_count, fringe_pct, has_fringe = detect_chroma_fringe(img, chroma_color, tolerance)
        print(f"  Fringe check: {fringe_count} fringe pixels ({fringe_pct:.1f}% of edge pixels) — {'DETECTED' if has_fringe else 'CLEAN'}")

        if has_fringe:
            retry_tolerance = tolerance + 15
            print(f"  Retrying background removal with tolerance {retry_tolerance}...")
            img = remove_bg(original.copy(), chroma_color, retry_tolerance)
            fringe_count, fringe_pct, has_fringe = detect_chroma_fringe(img, chroma_color, retry_tolerance)
            print(f"  Fringe re-check: {fringe_count} fringe pixels ({fringe_pct:.1f}% of edge pixels) — {'DETECTED' if has_fringe else 'CLEAN'}")
            if has_fringe:
                print("  WARNING: Chroma fringe still detected after retry with increased tolerance.")
                print("  ACTION: Still use this sprite, but add a task to the implementation plan")
                print("  for the user to manually clean up remaining background color artifacts.")

    # Step 2: Downscale
    img = downscale(img, target_width, target_height)

    # Step 3: Crop
    img = crop_sprite(img, crop_mode)

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    print(f"  Saved: {output_path} ({img.size[0]}x{img.size[1]})")


# ── hex color parsing ──────────────────────────────────────────────────────

def parse_hex_color(hex_str: str) -> tuple:
    """Parse hex color string (with or without #) to RGB tuple."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        raise ValueError(f"Invalid hex color: #{hex_str}")
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Process AI-generated sprites into game-ready assets")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # remove-bg
    p_bg = subparsers.add_parser("remove-bg", help="Remove chromakey background")
    p_bg.add_argument("--input", required=True)
    p_bg.add_argument("--output", required=True)
    p_bg.add_argument("--chroma-color", default="00FF00", help="Hex color to remove (default: 00FF00)")
    p_bg.add_argument("--tolerance", type=int, default=45, help="Color distance tolerance (default: 45)")

    # downscale
    p_ds = subparsers.add_parser("downscale", help="Nearest-neighbor downscale")
    p_ds.add_argument("--input", required=True)
    p_ds.add_argument("--output", required=True)
    p_ds.add_argument("--target-width", type=int, required=True)
    p_ds.add_argument("--target-height", type=int, required=True)

    # crop
    p_crop = subparsers.add_parser("crop", help="Crop transparent pixels")
    p_crop.add_argument("--input", required=True)
    p_crop.add_argument("--output", required=True)
    p_crop.add_argument("--crop-mode", choices=["bottom-anchor", "center", "none"], default="none")

    # pipeline
    p_pipe = subparsers.add_parser("pipeline", help="Full processing pipeline")
    p_pipe.add_argument("--input", required=True)
    p_pipe.add_argument("--output", required=True)
    p_pipe.add_argument("--target-width", type=int, required=True)
    p_pipe.add_argument("--target-height", type=int, required=True)
    p_pipe.add_argument("--crop-mode", choices=["bottom-anchor", "center", "none"], default="none")
    p_pipe.add_argument("--chroma-color", default=None, help="Hex color to remove (omit to skip bg removal)")
    p_pipe.add_argument("--tolerance", type=int, default=45, help="Color distance tolerance (default: 45)")

    args = parser.parse_args()

    if args.command == "remove-bg":
        chroma = parse_hex_color(args.chroma_color)
        img = Image.open(args.input).convert("RGBA")
        result = remove_bg(img, chroma, args.tolerance)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        result.save(args.output, "PNG")
        print(f"Background removed: {args.output}")

    elif args.command == "downscale":
        img = Image.open(args.input)
        result = downscale(img, args.target_width, args.target_height)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        result.save(args.output, "PNG")

    elif args.command == "crop":
        img = Image.open(args.input).convert("RGBA")
        result = crop_sprite(img, args.crop_mode)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        result.save(args.output, "PNG")

    elif args.command == "pipeline":
        chroma = parse_hex_color(args.chroma_color) if args.chroma_color else None
        run_pipeline(
            args.input, args.output,
            args.target_width, args.target_height,
            args.crop_mode, chroma, args.tolerance,
        )


if __name__ == "__main__":
    main()
