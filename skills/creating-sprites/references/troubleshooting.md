# Troubleshooting

## Table of Contents

- [Background Not Transparent](#background-not-transparent)
- [Multiple Sprites in One Image](#multiple-sprites-in-one-image)
- [Wrong Proportions or Size](#wrong-proportions-or-size)
- [Style Mismatch](#style-mismatch)
- [Green Fringe After Background Removal](#green-fringe-after-background-removal)
- [Model Copies Reference Too Closely](#model-copies-reference-too-closely)
- [Model Ignores Reference Style](#model-ignores-reference-style)
- [API Errors](#api-errors)
- [Fallback: Manual Creation](#fallback-manual-creation)

## Background Not Transparent

**Note:** The generate script requests transparent backgrounds natively via the API, so this issue is rare. If it does occur:

**Symptoms:** Image has a white, grey, or checkerboard background instead of transparency.

**Diagnosis:**
1. Run `check_transparency.py` — it reports alpha channel presence and transparent pixel %
2. If `CHECKERBOARD_DETECTED: yes`, the model faked transparency with a pattern

**Fix sequence:**
1. Retry with stronger transparency prompt: "isolated sprite on transparent background, no checkerboard pattern, actual PNG transparency"
2. If still failing, switch to chromakey fallback
3. Choose a safe chromakey color (see below)
4. Regenerate with: "solid flat [COLOR] background, no gradients, no patterns, no shadows"
5. Process with: `process_sprite.py remove-bg --chroma-color HEXCODE`

**Safe chromakey color selection:**

| Subject Contains | Avoid | Use Instead |
|-----------------|-------|-------------|
| Green (plants, trees, grass) | Green | Magenta (#FF00FF) or Blue (#0000FF) |
| Blue (water, ice, sky) | Blue | Magenta (#FF00FF) or Red (#FF0000) |
| Red/orange (fire, lava) | Red | Blue (#0000FF) or Magenta (#FF00FF) |
| Purple/magenta | Magenta | Green (#00FF00) or Blue (#0000FF) |
| Mixed/uncertain | — | Magenta (#FF00FF) is safest general-purpose |

**Rule:** Pick a color that does not appear in the sprite subject.

## Multiple Sprites in One Image

**Symptoms:** The generated image contains 2+ sprites, a sprite sheet, or a grid of variations.

**Fix:**
- Strengthen prompt: "SINGLE sprite", "ONE object only", "nothing else in the frame"
- Reduce subject complexity — simpler descriptions yield single outputs
- Discard the candidate and regenerate
- If persistent, reduce reference count to 1 (multiple refs can trigger "variations" behavior)

## Wrong Proportions or Size

**Symptoms:** Sprite is too tall, too wide, or doesn't match expected dimensions.

**Fix:**
- Be more explicit about dimensions in prompt: "a 32x32 pixel art sprite" → "a square 32x32 pixel art sprite, exactly as wide as it is tall"
- For non-square sprites, state the ratio: "wider than tall, approximately 3:2 ratio"
- Use `--size 1536x1024` (landscape) or `--size 1024x1536` (portrait) to give the model more room
- Adjust `--crop-mode` if proportions are close but not exact

## Style Mismatch

**Symptoms:** Generated sprite doesn't match the project's existing art style.

**Fix:**
- Add more reference images (up to 3) showing the target style
- Be more specific about style in text: instead of "pixel art", use "16-bit SNES-style pixel art with limited palette and clean outlines"
- Add negative constraints: "no 3D rendering, no realistic shading, no gradients"
- If model still ignores style, describe style elements explicitly: "black outlines, flat colors, top-down perspective, 2-frame idle animation style"

## Green Fringe After Background Removal

**Symptoms:** After chromakey removal, sprite edges have a green/colored halo.

**Fix:**
- Increase tolerance: `--tolerance 40` or `--tolerance 50`
- The fringe-cleaning pass in `process_sprite.py` handles mild cases automatically
- Try a different chromakey color that contrasts more with the sprite
- If fringe persists, try regenerating with a higher-contrast background color

## Model Copies Reference Too Closely

**Symptoms:** Generated sprite is nearly identical to the reference image.

**Fix:**
- Add to prompt: "generate something different but in the same style"
- Use more diverse references (different subjects, same style)
- Reduce to 1 reference image if using multiple
- Describe the desired differences explicitly in the prompt

## Model Ignores Reference Style

**Symptoms:** Generated sprite has a completely different art style than the references.

**Fix:**
- Add more reference images (2-3) to strengthen the style signal
- Describe the style explicitly in text alongside the references
- Ensure references are properly upscaled (tiny 32px refs are nearly invisible to the model)
- Verify upscaled references are being passed correctly via `--reference` flags

## API Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid or expired API key | Check OPENAI_API_KEY env var |
| 429 Too Many Requests | Rate limit exceeded | Wait 30-60s between batches, reduce `--count` |
| 500 Internal Server Error | Transient server issue | Retry after 10-30s |
| No image data in response | Unexpected response format | Check OpenAI API status, verify model ID |
| Content policy violation | Prompt flagged by safety filter | Rephrase prompt, remove potentially flagged terms |

## Fallback: Manual Creation

After 3 total failed generation attempts:

1. Save the best attempt as a reference for a future manual creation pass
2. Create a task in the implementation plan: "Manually create [sprite name] sprite"
3. Include the prompt that came closest and what went wrong
4. Move on to the next sprite — don't block progress on one asset
