# Prompt Guide

## Table of Contents

- [Base Template](#base-template)
- [Style Keywords](#style-keywords)
- [Anchoring Instructions](#anchoring-instructions)
- [Background Instructions](#background-instructions)
- [Reference Image Usage](#reference-image-usage)
- [Per-Type Prompt Examples](#per-type-prompt-examples)
- [Refinement Tips](#refinement-tips)

## Base Template

```
A [DIMENSIONS] pixel art [SUBJECT], [STYLE KEYWORDS].
[ANCHORING INSTRUCTION].
[BACKGROUND INSTRUCTION].
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
[REFERENCE INSTRUCTION if applicable].
```

## Style Keywords

Choose keywords that match the project's art direction:

- **Era/palette**: "16-bit pixel art", "SNES-era", "GBA-style", "NES palette", "limited palette"
- **Clarity**: "clean edges", "sharp pixels", "no anti-aliasing", "crisp outlines"
- **Perspective**: "top-down view", "side view", "3/4 view", "isometric"
- **Genre**: "game sprite", "RPG sprite", "platformer sprite"
- **Inspiration**: "[game name] inspired", "in the style of [game]"

## Anchoring Instructions

- **Entities** (enemies, player, animals, decorations, structures): "touching the bottom of the image"
- **Items**: "centered in the image"
- **Terrain tiles**: "filling the entire image edge to edge"
- **UI icons**: "filling the entire image"

## Background Instructions

**Default (try first):**
```
transparent background
```

**Stronger emphasis (if transparency fails):**
```
isolated sprite on transparent background, no checkerboard pattern, actual PNG transparency
```

**Chromakey fallback (when transparency consistently fails):**
```
solid flat [COLOR] background, no gradients, no patterns, no shadows on background
```

## Reference Image Usage

- Pass 1-3 upscaled reference sprites alongside the prompt
- Add: "Match the style of the provided reference images"
- More than 3 references has diminishing returns and may confuse the model
- If no references exist (first sprite in a project), rely on style keywords alone

## Per-Type Prompt Examples

**Item (sword):**
```
A 32x32 pixel art iron sword, 16-bit RPG style, clean edges, limited palette.
Centered in the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Enemy (slime):**
```
A 32x32 pixel art green slime monster, SNES-era RPG style, cute but menacing, clean outlines.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Decoration (oak tree):**
```
A 48x64 pixel art oak tree, top-down RPG style, lush green canopy, brown trunk, limited palette.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Player character:**
```
A 32x32 pixel art adventurer character, SNES RPG style, facing south, idle pose, clean edges.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Structure (chest):**
```
A 32x32 pixel art wooden treasure chest, 16-bit style, closed lid, metal bindings, limited palette.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
```

**Boss enemy:**
```
A 96x64 pixel art dragon boss, SNES RPG style, imposing, wings spread, detailed scales, limited palette.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Animal (cow):**
```
A 48x32 pixel art cow, wider than tall, top-down farm game style, white and brown patches, simple and cute.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

## Refinement Tips

| Problem | Prompt Fix |
|---------|------------|
| Too many colors | Add "limited palette", "8-color palette", or "16-color palette" |
| Blurry/soft edges | Add "sharp edges", "no anti-aliasing", "crisp pixel boundaries" |
| Multiple sprites | Emphasize "SINGLE sprite", "ONE object only", "nothing else in frame" |
| Copies reference too closely | "Generate something different but in the same style" |
| Ignores reference style | Add more diverse reference images; describe style explicitly in text |
| Wrong perspective | Be explicit: "top-down view", "side view facing right", "3/4 angle" |
| Too detailed for pixel count | "Simple shapes", "minimal detail", match detail to target resolution |
| Wrong proportions | State dimensions more explicitly: "wider than tall", "square proportions" |
