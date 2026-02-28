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

Study the project's existing sprites before choosing style keywords. Look at outlines, shading depth, perspective, and proportions — then pick keywords that match.

**Common keyword categories:**

- **Era/genre**: "indie RPG style", "16-bit style", "retro", "modern pixel art"
- **Outlines**: "bold dark outlines", "thin outlines", "no outlines", "crisp outlines"
- **Shading**: "rich shading", "detailed color gradients", "flat shading", "cel-shaded", "limited palette"
- **Perspective**: "3/4 top-down view", "side view", "top-down view", "isometric"
- **Shape**: "slightly chunky proportions", "rounded forms", "angular", "slim"
- **Clarity**: "clean edges", "sharp pixels", "no anti-aliasing"

**Important:** Always derive style keywords from the existing sprites in the project. Don't default to generic terms like "16-bit RPG" or "limited palette" — many indie games use rich multi-tone shading that those keywords would suppress.

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

These are examples — adapt the style keywords to match the project's existing art. The structure (dimensions, anchoring, background, constraints, reference line) stays the same; swap in whatever style fits.

**Item (sword):**
```
A 32x32 pixel art iron sword, [STYLE KEYWORDS].
Centered in the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Enemy:**
```
A 32x32 pixel art fiery crawler monster, [STYLE KEYWORDS], menacing.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Decoration (tree):**
```
A 48x64 pixel art tree, [STYLE KEYWORDS], lush green canopy with detailed shading, brown trunk with highlights.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Player character:**
```
A 32x32 pixel art adventurer character, [STYLE KEYWORDS], facing south, idle pose.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Structure (workbench):**
```
A 32x32 pixel art wooden workbench, [STYLE KEYWORDS], detailed wood grain shading, tools on surface.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Boss enemy:**
```
A 96x64 pixel art dragon boss, [STYLE KEYWORDS], imposing, wings spread, detailed scales.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Animal (cow):**
```
A 48x32 pixel art cow, [STYLE KEYWORDS], white and brown patches with detailed shading.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Fish (trout):**
```
A 32x32 pixel art trout, [STYLE KEYWORDS], side view, rich color gradients along body, detailed fins.
Centered in the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

**Pet (flame fox):**
```
A 32x32 pixel art flame fox companion, [STYLE KEYWORDS], warm orange and yellow tones with fiery highlights, cute proportions.
Touching the bottom of the image.
Transparent background.
Single sprite only, centered in frame, no border, no shadow, no text, no grid.
Match the style of the provided reference images.
```

## Refinement Tips

| Problem | Prompt Fix |
|---------|------------|
| Too many colors / noisy | Add "cohesive color palette", "controlled shading", or "limited palette" — but check existing sprites first, many projects use rich multi-tone shading |
| Blurry/soft edges | Add "sharp edges", "no anti-aliasing", "crisp pixel boundaries" |
| Multiple sprites | Emphasize "SINGLE sprite", "ONE object only", "nothing else in frame" |
| Copies reference too closely | "Generate something different but in the same style" |
| Ignores reference style | Add more diverse reference images; describe style explicitly in text |
| Wrong perspective | Be explicit: "top-down view", "side view facing right", "3/4 angle" |
| Too detailed for pixel count | "Simple shapes", "minimal detail", match detail to target resolution |
| Wrong proportions | State dimensions more explicitly: "wider than tall", "square proportions" |
