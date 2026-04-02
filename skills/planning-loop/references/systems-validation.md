# Game Systems Validation

Questions and frameworks for validating that game systems work together correctly.
Used during DEEPEN, CRITIQUE, and by the Systems Integration Analyst sub-agent.

## Resource Loop Validation

For every resource in the game (food, energy, health, money, materials, ammo, etc.):

### Flow Analysis
- What are ALL sources of this resource? (spawning, crafting, rewards, regeneration, trade)
- What are ALL drains? (consumption, decay, costs, damage, theft)
- **Do the math**: At steady state, does production >= consumption? Show the numbers.
- What happens when a source is disrupted? (season change, enemy attack, player mistake)
- Is there a recovery path, or is it a death spiral once resources drop below a threshold?
- How long can an entity survive with zero income of this resource?

### Timing Analysis
- How long does it take to acquire one unit? (travel time + gathering time + return time)
- How long does one unit last?
- What is the buffer between "resource is fine" and "resource is critical"?
- Are there periods where the resource is unavailable? How long? Can entities survive that period with stockpiled resources?
- **Critical question**: Is the consumption rate faster than the replenishment rate under ANY normal gameplay condition? If yes, the system will inevitably collapse.

### Cascading Effects
- When this resource runs out, what other systems break?
- Can running out of Resource A make it impossible to acquire Resource B?
- Is there a positive feedback loop where scarcity accelerates further scarcity?

## Spatial Interaction Validation

For every entity that moves and interacts with the world:

### Movement & Access
- Can entities physically reach every location they need to reach?
- Does the movement system's step size allow entities to land on exact required positions? (e.g., center of a building, edge of a resource node)
- If positions must be exact, what is the tolerance? Is movement granularity compatible with that tolerance?
- What happens when the path to a required location is blocked?

### Collision & Crowding
- If multiple entities need the same location (e.g., entering a building), can they all get there?
- Does collision avoidance prevent entities from reaching critical destinations?
- What happens when N entities try to use a single-occupancy space? Is there a queue? Do they give up? Do they glitch?
- Can entities pass through each other when necessary (e.g., doorways) or does collision create permanent gridlock?

### Interaction Ranges
- Are interaction ranges consistent? (e.g., if "enter building" requires being at position X, can entities actually reach position X given their movement system?)
- Do interaction ranges account for entity size/hitbox, not just center point?
- What happens at the boundary of interaction range — does it feel responsive or frustrating?

## System Conflict Detection

For every pair of systems that could interact:

### Direct Conflicts
- Does System A's rules ever make System B impossible? (e.g., anti-collision prevents house entry)
- Does System A's timing ever make System B's requirements unachievable? (e.g., hunger timer faster than food regrowth)
- Do any two systems give contradictory instructions to the same entity?

### Priority Resolution
- When two systems compete for an entity's action, which wins? Is this consistent and intuitive?
- Can an entity be stuck in a loop between two competing systems? (e.g., hungry so goes to food, but scared so runs away, but hungry again...)
- Are there priority overrides for critical situations? (e.g., "fleeing from danger" should override "collision avoidance at doorway")

### Edge Cases
- What happens at system boundaries? (e.g., entity is exactly at max hunger AND exactly at a food source)
- What happens when multiple systems trigger simultaneously?
- What happens when a system's prerequisite is destroyed mid-action? (e.g., food source disappears while entity is walking toward it)

## Player Experience Validation

### Onboarding & Controls
- For every player interaction: How does the player LEARN this control exists?
- Is there persistent access to control information? (help menu, tooltips, key bindings screen)
- Are controls discoverable through standard conventions? (left-click to select, right-click for context menu, etc.)
- If controls are unconventional, is there an interactive tutorial or at minimum a reference?

### UI & Menus
- Can the player restart/reset the game?
- Can the player pause?
- Can the player save and load?
- Can the player adjust settings (volume, speed, difficulty)?
- Can UI elements be moved/resized if they might obstruct other content?
- Are all UI elements accessible regardless of game state?
- Is there a way to see game status/stats at a glance?

### Failure & Recovery
- When the player "loses," what happens? Is it clear? Is there a path forward?
- Can the player reach an unrecoverable state without realizing it?
- If the game has a fail state, can the player retry without restarting the entire application?
- Are fail states communicated clearly before they become terminal?

### Feedback & Clarity
- For every game event: Does the player know it happened? (visual, audio, notification)
- For every player action: Is there immediate feedback? (click response, animation, sound)
- For every ongoing process: Can the player see its status? (progress bars, indicators, counters)
- Are important state changes highlighted, not buried in the UI?

## End-to-End Scenario Walkthrough

Before finalizing any system design, mentally simulate these scenarios:

### The First Five Minutes
- Player launches the game. What do they see?
- What is their first action? Is it obvious?
- When do they first feel agency/success?
- When do they first feel challenged?
- If they do nothing, what happens? Is that interesting or just death?

### The Steady State Loop
- What does minute 10-30 look like? Is the core loop engaging?
- Are resources flowing sustainably, or is the player slowly losing?
- What decisions does the player make? Are they interesting or obvious?

### The Stress Test
- What happens when everything goes wrong at once? (enemies + low resources + bad weather)
- Is there a recovery path, or does the game spiral to guaranteed failure?
- Is the stress interesting (tension, drama) or frustrating (unfair, opaque)?

### The Long Game
- What happens at hour 2? Hour 10? Is there still something new?
- Does the economy inflate or collapse over time?
- Are there emergent situations, or does every playthrough feel the same?

### The Edge Cases
- What if the player does something unexpected? (ignores food, builds nothing, attacks allies)
- What if the player optimizes aggressively? Does a dominant strategy make the game boring?
- What if two players (or entities) try to do the exact same thing at the exact same time?
