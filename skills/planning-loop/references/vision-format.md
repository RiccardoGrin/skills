# VISION.md Format

VISION.md is a **hub/index** for the game design — it should stay under ~500 lines.
Detailed content goes in separate files in a `vision/` directory, linked from VISION.md.

## Template

```markdown
<!-- When planning is complete, the loop agent adds PLANNING_COMPLETE above this line -->
# Vision: {Game Name}

## Seed

{Original game idea from the user, preserved verbatim. Never modify this section.}

## Status

- **Phase**: Expansion
- **Iterations completed**: 0
- **Confidence**: Starting
- **Last focus**: None

### Dimensions Explored

(None yet)

### Dimensions Pending

(To be discovered during expansion)

## Concept

{Evolves from seed. The core fantasy — what is this game and why would someone play it? Rewritten as understanding deepens. Keep to 1-2 paragraphs here.}

## Feature Map

{Summary-level list organized by game system. Each feature shows status: [proposed] / [explored] / [confirmed] / [cut]. Keep summary-level here — detailed mechanics go in vision/ files.}

## Detail Files

{Links to detailed vision documents as they are created. Examples:}

- [Core Mechanics](vision/core-mechanics.md)
- [Progression & Economy](vision/progression.md)
- [Competitor Research](vision/competitor-research.md)
- [Narrative & World](vision/narrative.md)
- [Architecture & Testability](vision/architecture.md)

{The agent creates whatever files make sense for the game — there is no fixed list.}

## Uniqueness

{What makes this game genuinely different — the hook in 1-2 sentences. Detailed analysis in vision/ files.}

## Inspirations & Competitors

{Brief summary — detailed research goes in vision/competitor-research.md or similar.}

## Scope & Milestones

{Playable vertical slices, ordered by fastest path to playable. Added during Refine phase.}

- **Milestone 1**: Minimal game loop — [core action] + [visible result]
- **Milestone 2**: Core mechanic end-to-end — [the central fantasy is playable]
- **Milestone 3+**: Additional systems layered on one at a time
- **MVP**: The first milestone where a player would choose to keep playing

## Systems Interactions

{How game systems connect and affect each other. Added during Deepen phase, validated during Critique. This section prevents systems from being designed in isolation.}

### Resource Flows
{For each resource: sources, drains, steady-state math, disruption survival. Show the numbers.}

### Spatial Rules
{Movement granularity, collision rules, interaction ranges, priority when systems conflict.}

### Known Conflicts & Resolutions
| Conflict | Systems Involved | Resolution | Iteration |
|----------|-----------------|------------|-----------|

## Player Experience

{How the player interacts with and understands the game. Added during Critique phase.}

### First 5 Minutes
{Step-by-step walkthrough of a new player's first experience.}

### Controls Reference
{Every player interaction and how the player learns it exists.}

### UI Requirements
{Menus, HUD, repositioning, accessibility. Checklist of required elements.}

## Open Questions

- What is the core game loop — the 30-second action the player repeats?
- What makes each play session feel different?
- How far can the core mechanic be pushed?

## Decision Log

| Decision | Reasoning | Iteration |
|----------|-----------|-----------|

## Cutting Room Floor

{Game mechanics explored and intentionally cut, with reasons. Prevents re-exploring dead ends.}
```

## File Splitting Guidelines

- VISION.md should never exceed ~500 lines. If it's growing past that, content needs to move to detail files.
- When a section has more than ~50-100 lines of detailed content, extract it to `vision/<topic>.md` and replace with a brief summary + link.
- Common detail files for games (create as needed, not required):
  - `vision/core-mechanics.md` — detailed breakdown of the core game loop and primary mechanics
  - `vision/progression.md` — progression systems, economy, balance curves, unlocks
  - `vision/combat-system.md` (or whatever the primary system is) — deep dive into the main gameplay system
  - `vision/competitor-research.md` — detailed competitor analysis and genre research
  - `vision/narrative.md` — story, world-building, lore, environmental storytelling
  - `vision/architecture.md` — technical architecture, engine choice, testability approach
  - `vision/game-feel.md` — juice, feedback, screen shake, sound design, player satisfaction
- The agent should create whatever files make sense for the game. These are suggestions, not rules.
- Every detail file must be linked from VISION.md's Detail Files section so the next iteration can find it.

## Evolution Rules

- **Seed**: Never modify. The original game idea preserved for reference.
- **Status**: Update every iteration — phase, iteration count, last focus, confidence level.
- **Concept**: Rewrite as understanding deepens. Keep brief in VISION.md — this is the elevator pitch.
- **Feature Map**: Grows during Expansion. Status changes during Critique and Refinement. Keep summary-level in VISION.md.
- **Detail Files**: When deep-diving a game system or doing research, write to the appropriate vision/ file, not directly into VISION.md.
- **Scope & Milestones**: Added during Refine. Playable vertical slices ordered fastest-to-playable.
- **Systems Interactions**: Added during Deepen. Every time a system is deepened, its connections to other systems must be documented here with concrete numbers and timing. Updated whenever the Systems Integration Analyst finds conflicts.
- **Player Experience**: Added during Critique. Every Critique iteration must validate the first-5-minutes walkthrough and controls reference. Updated whenever the Player Experience Designer finds gaps.
- **Open Questions**: Add liberally. Resolve by moving answers to appropriate sections or detail files.
- **Decision Log**: Record every significant design decision with reasoning and iteration number.
- **Cutting Room Floor**: Always explain why a mechanic was cut. Never silently remove features.

## Phase Assessment Signals

| Signal | Likely Phase |
|--------|-------------|
| Few mechanics, obvious game ideas only, thin sections | Expand |
| Mechanics listed but bullet-point level, no system details | Deepen |
| Deep mechanics but no competitor/genre analysis | Research |
| Rich vision but unchallenged — is it actually fun? | Critique |
| Battle-tested, comprehensive, high confidence | Refine |
| Refined with clear playable milestones | Plan |

The agent should not rigidly follow this order.
Use judgment — expansion may reveal a need for immediate research, critique may expose gaps needing more expansion.

## Implementation Plan Structure

When the PLAN phase creates the implementation plan, it splits across files:

- `IMPLEMENTATION_PLAN.md` — hub with Goal, milestone list (status + links), Decision Log, Issues Found, and usage instructions for the dev loop
- `plans/milestone-N-name.md` — one file per milestone, each with flat `- [ ]` checkbox tasks

Milestone ordering follows **fastest path to playable**:
1. Milestone 1 = minimal testable game loop (player acts, something happens)
2. Each subsequent milestone adds one major system + its tests
3. No "infrastructure-only" milestones — setup is done incrementally within the milestone that needs it
4. Test tasks are part of every milestone, not deferred

This keeps each file manageable and ensures the dev loop builds toward something playable at every step.
