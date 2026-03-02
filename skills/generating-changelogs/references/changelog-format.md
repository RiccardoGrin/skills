# Changelog Format Specification

Full format template, emoji mapping, tone rules, and approved sample for player-facing changelogs.

## Table of Contents

- [Format Template](#format-template)
- [Emoji Mapping](#emoji-mapping)
- [Tone Rules](#tone-rules)
- [Approved Sample](#approved-sample)
- [Non-Game Adaptation](#non-game-adaptation)

## Format Template

```markdown
**{ProjectName} — v{Version} "{Subtitle}"**

_{Thematic summary — 1-2 sentences, present tense, player-facing. Captures the feel of the update.}_

### {Emoji} {Section Title}
{Optional spotlight intro — one flavorful sentence for major sections.}

- **{Feature Name}** — {Concise, player-facing description}
  - *{Sub-item name}* — {Brief description}
  - *{Sub-item name}* — {Brief description}
- **{Feature Name}** — {Description}

### {Emoji} {Section Title}

- **{Feature Name}** — {Description}

### 🔧 Fixes & Improvements
- {Fix or improvement description — no bold name needed for simple fixes}
- {Another fix}
```

**Structural rules:**

- Title line uses bold (`**`), includes project name, version, and subtitle in quotes
- Thematic summary is italicized (`_..._`), immediately below the title
- Section headers use `###` with one emoji before the title
- Feature names within sections are bold, followed by an em dash (`—`), then description
- Sub-items are indented, use italic names, followed by an em dash, then description
- Fixes section uses simple bullets without bold names (unless the fix is significant)
- One blank line between sections
- No trailing punctuation on bullet items unless they're full sentences

## Emoji Mapping

One emoji per section header. Never use emoji on individual bullet items.

| Section Type | Emoji | Example Header |
|-------------|-------|----------------|
| World, Biomes, Environment | 🌍 | `### 🌍 World & Biomes` |
| Combat, Enemies, Bosses | ⚔️ | `### ⚔️ Combat & Enemies` |
| Tools, Crafting, Items | 🛠️ | `### 🛠️ Tools & Crafting` |
| Farming, Gathering, Crops | 🌾 | `### 🌾 Farming` |
| Creatures, NPCs, Wildlife | 🐾 | `### 🐾 Wildlife & Breeding` |
| Abilities, Skills, Progression | ✨ | `### ✨ Abilities & Progression` |
| UI, HUD, Menus | 🖥️ | `### 🖥️ Interface` |
| Audio, Music, Sound | 🔊 | `### 🔊 Audio` |
| Performance, Optimization | ⚡ | `### ⚡ Performance` |
| Fixes, Improvements, Polish | 🔧 | `### 🔧 Fixes & Improvements` |
| New Features (general) | ✨ | `### ✨ New Features` |
| Configuration, Settings | ⚙️ | `### ⚙️ Configuration` |
| API, Integration | 🔌 | `### 🔌 API Changes` |
| Security | 🔒 | `### 🔒 Security` |
| Documentation | 📝 | `### 📝 Documentation` |

For custom sections not listed above, choose the closest thematic emoji. Don't reuse an emoji that's already assigned to another section in the same changelog.

## Tone Rules

The changelog is for players and users, not developers.

**Voice:** Third-person, present tense, direct.
Describe what exists in the update, not what was done to create it.

**Good examples:**

- "Four distinct regions beyond the void ring, each with unique wildlife and resources"
- "A multi-phase boss lurking in the dark forest"
- "Craft a hoe, till the ground, plant seeds — soil near water stays moist for faster growth"
- "Blinks away after being hit, forcing you to chase it down"

**Bad examples:**

- "We added four new biomes to the Tier 2 area" ← dev diary voice
- "Shadow King has 500 HP, deals 25 damage per bolt, and spawns 3 minions" ← stats dump
- "Implemented BiomeManager with config-driven tile spawning" ← implementation detail
- "Fixed bug in CropSystem.js where growth timer wasn't resetting" ← code reference

**Rules of thumb:**

1. If it mentions a file name, class name, or function — rewrite it
2. If it includes numbers only a developer would care about — remove them
3. If it says "we" or "I" — rewrite in present tense ("New boss guards the dark forest")
4. If it says "implemented", "added", "created" — rewrite to describe the result, not the action
5. If it describes how something was built — describe what it does instead
6. Brief is better — one punchy sentence beats two wordy ones

## Approved Sample

This is the reference implementation. New changelogs should match this structure, tone, and level of detail.

```markdown
**Dissolution — v0.2.0 "Dissolution Expands"**

_The world beyond the void ring awakens. Four new biomes, two boss encounters, a full farming system, and powerful new abilities await those brave enough to push past the barrier._

### 🌍 World & Biomes
The void ring is no longer the edge of the world — it's the gateway.

- **Tier 2 Biomes** — Four distinct regions beyond the first void ring:
  - *Jungle* — Dense, humid canopy with exotic wildlife and fruit-bearing plants
  - *Dark Forest* — Shadowy woodland prowled by wolves and something far worse
  - *Flower Field* — Vibrant meadow home to deer and restorative flowers
  - *Mushroom Grove* — Fungal landscape dotted with glowcaps and giant mushrooms
- **Tier 3 Zones (Preview)** — Two end-game regions beyond the second barrier: Ashen Waste and Crystal Hollow
- **Barrier System** — Three layered barriers gate progression, each more dangerous than the last
- **New Structures** — Hunter's Blind, Abandoned Mine, Mushroom Ring, Overgrown Shrine, and Watchtower Ruins scattered across the world
- **Rock Variations** — Biome-specific formations: mossy, sandstone, icy, fungal, void-veined, and more
- **Ground Cover** — Tall grass, pebbles, sticks, and small mushrooms add life to the landscape

### ⚔️ Combat & Enemies
New threats await in Tier 2 — and two bosses guard the path forward.

- **Teleporter** — Blinks away after being hit, forcing you to chase it down
- **Splitter** — Fragments into smaller copies on death across three size stages
- **Mobile Shooter** — Maintains distance while firing slow projectiles
- **Shadow King** — Multi-phase boss lurking in the dark forest. Shadow bolts, dissolution zones, and minion summons. Drops the Shadow Crown.
- **Void Heart** — The final boss. Void tendrils, corruption waves, and a three-phase fight deep in Tier 3. Defeating it ends the game.
- **Boss Compass** — Craftable compass pointing toward the nearest undefeated boss. Activate Boss Shrines to reveal spawn locations on the minimap.

### 🛠️ Tools & Crafting
- **Copper Ore & Copper Tools** — New mid-tier gear crafted from deposits found in Tier 2
- **Gold Ore & Gold Tools** — Higher-tier tools from gold deposits with improved stats
- **Void Weapons** — End-game gear crafted from void crystals, dark aura, and gems. The void sword steals life on hit.

### 🌾 Farming
A full crop system brings a new dimension to survival.

- **Tilling & Planting** — Craft a hoe, till the ground, plant seeds. Soil near water stays moist for faster growth.
- **Crop Growth** — Three stages over multiple days. Harvest when mature.
- **Tier 2 Crops** — Jungle Fruit, Glowcap, and Sunpetal — each with unique effects
- **5 Unique Flowers** — Whitepetal heals, Frostbloom generates aura, Bogshade grants poison immunity, Sunblaze boosts speed, Meadowbell restores hunger. Each grows in specific biomes and can be planted.

### 🐾 Wildlife & Breeding
- **6 Tier 2 Animals** — Pig, Crow, Bee, Gecko, Wolf, Deer — each with distinct behavior. Wolves hunt at night. Crows flee at double speed. Bees retaliate when provoked.
- **Animal Breeding** — Feed an animal its preferred food to trigger love mode. Nearby pairs produce babies that grow to adults over time.

### ✨ Abilities & Progression
- **Altar Evolution** — Max out your Tier 1 altar, then evolve it to unlock Tier 2 upgrades and abilities
- **Aura Burst** — Knockback and damage in a wide radius
- **Shadow Step** — Short-range teleport through obstacles
- **Observer Pulse** — Destroys incoming projectiles around you
- **Environmental Hazards** — Swamp poison and tundra cold drain health. Stay near torches or campfires for protection.

### 🔧 Fixes & Improvements
- Void ring is now guaranteed to be at least 26 tiles thick
- Ghost spawns on the nearest safe tile when dying in the void
- Ghost is now visible on the minimap
- Dark aura drops rebalanced across void enemies
- Food items now show health and hunger restore values in tooltips
- Resource-specific hit effects — leaves scatter from trees, chunks fly from rocks, shards burst from crystals
```

## Non-Game Adaptation

The format works for any project type. The structure stays the same — only the section names and emoji change to match the domain.

**What stays identical:**

- Bold title with version and subtitle
- Italic thematic summary
- `###` section headers with one emoji each
- Bold feature names with em dash descriptions
- Spotlight intros for major sections
- Fixes & Improvements always last

**Section naming by project type:**

| Game Project | App / Library | SaaS / Web App |
|-------------|---------------|----------------|
| 🌍 World & Biomes | ✨ New Features | ✨ New Features |
| ⚔️ Combat & Enemies | 🔄 Changes | 🔄 Changes |
| 🛠️ Tools & Crafting | ⚙️ Configuration | ⚙️ Settings & Admin |
| 🌾 Farming | 📦 Data & Storage | 📦 Data Pipeline |
| ✨ Abilities & Progression | 🖥️ User Experience | 🖥️ User Experience |
| 🔧 Fixes & Improvements | 🔧 Fixes & Improvements | 🔧 Fixes & Improvements |
| — | ⚡ Performance | ⚡ Performance |
| — | 🔌 API Changes | 🔌 API Changes |
| — | 🔒 Security | 🔒 Security |

**The principle:** Group by what the user interacts with, not by how the code is organized.
For a CLI tool, that might be "New Commands", "Output Formatting", "Configuration".
For a design system, that might be "New Components", "Token Changes", "Accessibility".
Create whatever sections make sense — use the emoji mapping table above for standard ones, pick a thematic emoji for custom ones.

**Tone adaptation:**

- Game changelogs lean flavorful and evocative ("A multi-phase boss lurking in the dark forest")
- App/library changelogs lean clear and practical ("Dashboard widgets can now be resized and reordered")
- Both avoid implementation details — describe the result, not the code
