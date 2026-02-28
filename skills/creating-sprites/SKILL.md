---
name: creating-sprites
description: Guides pixel-art sprite creation via Gemini image generation with automated processing. Covers sizing, prompting, transparency verification, downscaling, and cropping. Use when creating game sprites or pixel art assets
---

# Creating Sprites

Generate pixel-art game sprites via Gemini's native image generation API, then process them into game-ready assets with transparency, correct dimensions, and proper anchoring.

## Reference Files

| File | Read When |
|------|-----------|
| `references/sprite-sizes.md` | Choosing target size, generation size, crop mode, or fake pixel math for a sprite type |
| `references/prompt-guide.md` | Constructing or refining a generation prompt, choosing style keywords, or writing per-type prompts |
| `references/troubleshooting.md` | A generation fails, transparency check fails, style doesn't match, or API returns errors |

## Prerequisites

- **`GEMINI_API_KEY`** — a Google AI Studio API key (free at https://aistudio.google.com/apikey)
  - The generate script auto-loads from: `--api-key` flag → `GEMINI_API_KEY` env var → `.env` file in current directory
- **Python dependencies**: `google-genai` and `Pillow` (installed via `requirements.txt` in the skill's `scripts/` directory)

## Script Paths

All `scripts/` paths in this skill are **relative to the skill directory**, not the project directory. Resolve them to absolute paths before running. For example, if the skill is installed at `~/.claude/skills/creating-sprites/`, then `scripts/generate_sprite.py` means `~/.claude/skills/creating-sprites/scripts/generate_sprite.py`.

## Workflow Checklist

```
- [ ] Phase 0: Verify prerequisites
- [ ] Phase 1: Determine sprite requirements
- [ ] Phase 2: Prepare reference images
- [ ] Phase 3: Construct prompt
- [ ] Phase 4: Generate candidates
- [ ] Phase 5: Validate candidates
- [ ] Phase 6: Process chosen sprite
- [ ] Phase 7: Save and update plan
```

## Phase 0: Verify Prerequisites

Before doing any work, verify the environment is ready. Handle what you can; only ask the user for things you can't resolve yourself.

1. **Check API key** — check all three sources:
   ```bash
   python -c "
   import os
   from pathlib import Path
   key = os.environ.get('GEMINI_API_KEY', '')
   if not key:
       env = Path('.env')
       if env.exists():
           for line in env.read_text().splitlines():
               if line.strip().startswith('GEMINI_API_KEY'):
                   key = line.partition('=')[2].strip().strip('\"').strip(\"'\")
   print('OK' if key else 'MISSING')
   "
   ```
   - If `MISSING`: ask the user to get a key from https://aistudio.google.com/apikey and either add `GEMINI_API_KEY=their-key` to a `.env` file in the project root, or export it as an environment variable
   - Do NOT proceed past this phase without a valid key

2. **Install Python dependencies** (do this yourself, don't ask the user):
   ```bash
   pip install -r <skill-dir>/scripts/requirements.txt
   ```
   Then verify:
   ```bash
   python -c "from google import genai; from PIL import Image; print('OK')"
   ```
   - If install fails due to permissions, try `pip install --user -r ...`

Only the API key requires user action. Everything else you should handle yourself.

## Phase 1: Determine Sprite Requirements

Identify what to create and look up its parameters.

1. Determine the entity type: item, enemy, decoration, structure, UI icon, player, pet, animal, boss, terrain tile
2. Read `references/sprite-sizes.md` for common size examples, generation size, and crop mode — use these as a starting point and adjust based on the specific entity
3. Record these values:
   - `target_width` and `target_height` (e.g., 32x32)
   - `generation_size` (1024 or 2048)
   - `crop_mode` (bottom-anchor, center, or none)
4. Identify the destination path in the project for the final sprite
5. Identify 1-3 existing sprites that could serve as style references

## Phase 2: Prepare Reference Images

Existing sprites are tiny and must be upscaled for the AI model to interpret them.

For each reference sprite, run:
```bash
python scripts/upscale_reference.py --input path/to/sprite.png --output temp/sprite_upscaled.png
```

The script auto-calculates the best integer multiplier to reach 500-1024px using nearest-neighbor interpolation (preserves pixel crispness).

If no reference sprites exist (first sprite in the project), skip this phase.
The prompt alone will define the style.

## Phase 3: Construct Prompt

Read `references/prompt-guide.md` for the base template, style keywords, and per-type examples.

Every prompt must specify:
- Pixel-art style with era/palette keywords
- Target fake-pixel dimensions ("a 32x32 pixel art sprite")
- **Transparent background** (always request this first)
- ONE sprite only, centered in frame
- No border, no shadow, no text, no grid
- Subject description
- Anchoring: "touching the bottom of the image" for entities, "centered" for items
- "Match the style of the provided reference images" when references are included

## Phase 4: Generate Candidates

Run the generation script to produce 4 candidates (each is a separate API call — one sprite per image):

```bash
python scripts/generate_sprite.py \
  --prompt "A 32x32 pixel art ..." \
  --output-dir ./sprites-wip \
  --reference temp/ref1_upscaled.png \
  --reference temp/ref2_upscaled.png \
  --count 4
```

Outputs: `candidate_001.png` through `candidate_004.png` in the output directory.

## Phase 5: Validate Candidates

Two-step validation: programmatic then visual.

### Step A — Programmatic Transparency Check

Run on each candidate:
```bash
python scripts/check_transparency.py --input ./sprites-wip/candidate_001.png
```

Output format:
```
FILE: candidate_001.png
FORMAT: PNG
ALPHA_CHANNEL: yes
TRANSPARENT_PIXELS: 45.2%
CHECKERBOARD_DETECTED: no
RESULT: PASS
```

- **PASS**: At least 10% transparent pixels, no checkerboard pattern
- **FAIL**: No alpha channel, 0% transparency, checkerboard detected, or not PNG
- Discard any candidate that fails

### Step B — Visual Inspection

Use the Read tool to view each passing candidate.
Check: single sprite? Correct orientation? Right proportions? Matches game style?
Pick the best candidate.

### If All Candidates Fail Transparency

1. Retry once with stronger prompt: "isolated sprite on transparent background, no checkerboard pattern, actual PNG transparency"
2. If still failing, switch to chromakey fallback:
   - Analyze the sprite subject to pick a safe background color
   - **Green (#00FF00)**: safe for non-plant sprites
   - **Magenta (#FF00FF)**: safe for plant/nature sprites, general-purpose fallback
   - **Blue (#0000FF)**: safe for purple/magenta subjects
   - Add to prompt: "solid flat [COLOR] background, no gradients, no patterns, no shadows"
   - After generation, process with: `process_sprite.py remove-bg --chroma-color HEXCODE`

### If Candidates Fail Visual Check

- Adjust the prompt (see `references/troubleshooting.md`)
- Add, remove, or change reference images
- After 3 total failed attempts, create a manual creation task and move on

## Phase 6: Process Chosen Sprite

Run the full pipeline on the selected candidate:

```bash
python scripts/process_sprite.py pipeline \
  --input ./sprites-wip/candidate_002.png \
  --output ./sprites/my_sprite.png \
  --target-width 32 --target-height 32 \
  --crop-mode bottom-anchor
```

If chromakey was used, add `--chroma-color HEXCODE --tolerance 30`.

Pipeline steps (can also run individually):
1. **Remove background** (if chromakey): `remove-bg --chroma-color HEXCODE`
2. **Downscale**: nearest-neighbor from generation size to target dimensions
3. **Crop** per crop mode: bottom-anchor trims sides/top; center and none leave canvas as-is

**Post-chromakey re-check**: If chromakey was used, run `check_transparency.py` on the output.
If it fails or the visual check shows artifacts, create a manual task in the implementation plan and skip this sprite.

Read the final sprite to verify: correct dimensions, clean transparency, pixel-art preserved, appropriate crop.

## Phase 7: Save and Update Plan

1. Move the final sprite to the correct project folder
2. Clean up temporary files (sprites-wip/, temp upscaled references)
3. Update the implementation plan with integration tasks (add to asset registry, create entity config, etc.)

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| Generating without reference images | Always use 1-3 style references when available |
| Passing tiny 32px sprites as references | Upscale references to 500-1024px with nearest neighbor first |
| Bilinear/bicubic downscaling | Always nearest-neighbor to preserve pixel crispness |
| Multiple sprites in one image | ONE sprite per image, 4 separate API calls |
| Only visual transparency check | Always run check_transparency.py script first |
| Green chromakey for plant sprites | Pick a chromakey color not present in the subject |
| Skipping visual validation | Always Read the image to inspect after programmatic checks |
| Cropping items | Items stay centered in canvas; only crop entities |
| Giving up after 1 failed generation | Adjust prompt/refs and retry; give up after 3 total attempts |

## Dependency Note

This skill requires `google-genai` and `Pillow`. Phase 0 handles installation automatically.
This is an approved exception to the standard-library-only rule for scripts.
