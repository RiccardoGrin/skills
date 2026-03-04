# Sprite Sizes Reference

## Common Size Examples

These are **starting points, not rigid rules**.
The agent should determine the right size based on the specific entity — a rabbit is smaller than a generic 32x32 enemy, a large bull is bigger, a slithering snake could be long and narrow.
All dimensions must be multiples of 16.

| Sprite Type | Typical Size | Gen Size | Fake Pixel Factor | Crop Mode | Anchor | Notes |
|-------------|-------------|----------|-------------------|-----------|--------|-------|
| UI icon | 16x16 | 1024x1024 |64px | none | — | Fill entire canvas |
| Item | 32x32 | 1024x1024 |32px | center | center | Centered for inventory |
| Enemy | 32x32 | 1024x1024 |32px | bottom-anchor | bottom | Hitbox alignment |
| Terrain tile | 32x32 | 1024x1024 |32px | none | — | Fill entire canvas |
| Player | 32x32 | 1024x1024 |32px | bottom-anchor | bottom | Ground alignment |
| Small animal/pet | 32x32 | 1024x1024 |32px | bottom-anchor | bottom | |
| Large animal | 48x32 | 1024x1024 |~21-32px | bottom-anchor | bottom | Wider; prompt for rect |
| Small decoration | 32x32 | 1024x1024 |32px | bottom-anchor | bottom | Crop to content |
| Large decoration | 48x64+ | 1024x1536 | varies | bottom-anchor | bottom | Trees, large props; use portrait size |
| Boss enemy | 96x64+ | 1536x1024 | ~16-21px | bottom-anchor | bottom | Use landscape size for wide bosses |
| Structure | 32x32–64x64 | 1024x1024 |varies | bottom-anchor | bottom | |

## Size Rules

- All dimensions must be multiples of 16
- Minimum size: 16x16
- Maximum practical size: 128x128 (beyond this, consider splitting into tiles)
- When in doubt, default to 32x32
- Adjust dimensions to fit the subject — wider entities get wider sprites, smaller creatures get smaller sprites

## Crop Modes

**`bottom-anchor`** — For entities (enemies, player, animals, decorations, structures).
Find the content bounding box, trim transparent pixels from all sides.
Content touches the bottom edge of the output so the sprite's feet align with the ground/hitbox.

**`center`** — For items.
No cropping. The sprite stays centered within the full target canvas.
Items need consistent bounds for inventory grid display.

**`none`** — For terrain tiles and UI icons.
No cropping. The sprite fills the entire canvas edge to edge.

## Fake Pixel Calculation

AI models can't generate at 32x32. Instead, generate at 1024x1024 and tell the model to draw pixel art that *looks* like NxN pixels.

```
fake_pixel_factor = generation_size / target_dimension
```

Examples:
- 1024 / 32 = 32 real pixels per fake pixel
- 1024 / 16 = 64 real pixels per fake pixel
- 1536 / 96 = 16 real pixels per fake pixel (landscape gen for wide boss)

Each "fake pixel" in the generated image occupies `fake_pixel_factor × fake_pixel_factor` real pixels.
Nearest-neighbor downscaling collapses these back to actual pixel-art dimensions.

## Non-Square Sprites

For non-square targets (e.g., 48x32):
- Include the aspect ratio in the prompt ("a 48x32 pixel art sprite, wider than tall")
- Use `--size 1536x1024` for landscape sprites or `--size 1024x1536` for portrait sprites to match the subject's proportions
- The fake pixel factor differs per axis — calculate each independently

## Why Entities Touch the Bottom

Entity sprites are drawn touching the bottom of the canvas so that after cropping:
- The sprite's visual feet align with its collision hitbox
- Ground contact is consistent across all entity sprites
- No floating sprites or inconsistent offsets

## Why Items Don't Crop

Items are displayed in inventory grids where every slot is the same size.
Cropping would make items different sizes, breaking grid alignment.
Instead, items are centered within their fixed canvas with transparent padding.
