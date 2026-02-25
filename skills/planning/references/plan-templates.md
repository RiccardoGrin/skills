# Plan Templates — Worked Examples

## Table of Contents

- [Flat List Example](#flat-list-example)
- [Phased Plan Example](#phased-plan-example)
- [What Makes These Work](#what-makes-these-work)

## Flat List Example

A small feature: adding keyboard shortcuts to a task list app.

```
## Goal

Add keyboard shortcuts for common task actions (complete, delete, move up/down) so power users can manage tasks without touching the mouse.

## Research Insights

**UX Pattern**: Notion, Linear, and Todoist all use single-key shortcuts when no text input is focused, with a `?` shortcut to show available keys. Linear's approach of contextual shortcuts (different keys depending on what's selected) is the closest match to our task list.

**Accessibility**: WCAG 2.1 SC 2.1.4 requires that single-key shortcuts can be remapped or disabled. We'll add a toggle in settings.

## Changes

### 1. Add keyboard event listener to task list
- **File**: `src/components/TaskList.tsx`
- **Target**: `TaskList` component
- **Action**: Add a `useEffect` hook that registers a `keydown` listener on the task list container. Only active when no text input is focused (check `document.activeElement`). Keys: `d` = complete, `Backspace` = delete, `j`/`k` = move selection down/up.
- **Reasoning**: Centralizing the listener on the container (not individual items) avoids N listeners and simplifies cleanup.
- **Depends on**: Nothing

### 2. Add visual selection state to task items
- **File**: `src/components/TaskItem.tsx`
- **Target**: `TaskItem` component
- **Action**: Accept a `selected` prop. When true, apply `ring-2 ring-blue-500` outline and set `aria-selected="true"`. Ensure the selected item scrolls into view using `scrollIntoView({ block: 'nearest' })`.
- **Reasoning**: Keyboard navigation requires visible focus indication — the existing hover state is not sufficient.
- **Depends on**: Nothing

### 3. Add keyboard shortcut toggle to settings
- **File**: `src/components/Settings.tsx`
- **Target**: `KeyboardSection` (new section in existing settings panel)
- **Action**: Add a toggle switch for "Enable keyboard shortcuts" (default: on). Store preference in `localStorage` key `prefs.keyboardShortcuts`. The `TaskList` listener checks this before handling keys.
- **Reasoning**: WCAG 2.1 SC 2.1.4 requires single-key shortcuts to be disablable.
- **Depends on**: Nothing

### 4. Add shortcut help overlay
- **File**: `src/components/ShortcutHelp.tsx` (new file)
- **Target**: New `ShortcutHelp` modal component
- **Action**: Create a modal triggered by `?` key that displays a two-column table of shortcut keys and their actions. Dismiss with `Escape` or clicking outside. Use the existing `Modal` component from `src/components/ui/Modal.tsx`.
- **Reasoning**: Discoverability — users need to learn what shortcuts exist. The `?` convention is standard (GitHub, Gmail, Linear all use it).
- **Depends on**: Change 1 (the `?` key is handled by the same listener)

## Edge Cases & Risks
- User is typing in the task title edit field — shortcuts must not fire. Mitigated by checking `activeElement` tag name.
- Task list is empty — `j`/`k` navigation should no-op gracefully, not throw.
- Screen reader users — `aria-selected` and shortcut toggle ensure keyboard shortcuts don't interfere with assistive technology.

## Validation
- [ ] Pressing `d` on a selected task marks it complete
- [ ] Pressing `Backspace` on a selected task deletes it (with confirmation)
- [ ] `j`/`k` moves selection down/up, wrapping at list boundaries
- [ ] `?` opens the shortcut help overlay
- [ ] Shortcuts do not fire when a text input is focused
- [ ] Disabling shortcuts in settings prevents all shortcut actions
- [ ] Selected task has visible focus ring and `aria-selected="true"`
```

**Why this works**: Each change names a specific file, component, and action. Dependencies are explicit. The research insight directly influenced the design (single-key shortcuts, `?` help). Edge cases are specific scenarios with mitigations, not generic "handle errors."

## Phased Plan Example

A medium feature: adding comment threads to a document editor.

```
## Goal

Add threaded comments to documents so collaborators can discuss specific text selections inline, similar to Google Docs.

## Research Insights

**UX Pattern**: Google Docs, Notion, and Figma all anchor comments to content selections. Google Docs uses a sidebar; Notion uses inline popovers. Given our document layout has no sidebar, inline popovers (Notion-style) fit better.

**Technical Approach**: Store comment anchors as document decorations (ProseMirror plugin), not inline marks. Decorations survive content edits around them; inline marks break when adjacent text is modified.

## Phase 1: Data Model & API

### 1. Add comments table to database
- **File**: `prisma/schema.prisma`
- **Target**: New `Comment` model
- **Action**: Add `Comment` model with fields: `id`, `documentId` (relation to `Document`), `authorId` (relation to `User`), `body` (text), `anchorStart` (int), `anchorEnd` (int), `parentId` (nullable self-relation for threads), `resolved` (boolean, default false), `createdAt`, `updatedAt`.
- **Reasoning**: Anchor positions stored as character offsets, transformed on each document edit. `parentId` enables threading without a separate model.
- **Depends on**: Nothing

### 2. Add comment API endpoints
- **File**: `src/api/comments.ts`
- **Target**: New router
- **Action**: Add CRUD endpoints: `POST /documents/:id/comments` (create), `GET /documents/:id/comments` (list with thread nesting), `PATCH /comments/:id` (edit body, resolve), `DELETE /comments/:id` (soft delete). All endpoints require document read permission. Edit/delete restricted to comment author.
- **Reasoning**: REST endpoints match existing API patterns in `src/api/`. Thread nesting handled in the GET query (group by `parentId`) rather than separate endpoints.
- **Depends on**: Change 1 (needs the Comment model)

**Checkpoint**: Run `prisma migrate dev`, hit endpoints with curl/Postman. Verify CRUD works, thread nesting returns correctly, permissions enforce.

## Phase 2: Editor Integration

### 3. Add comment decoration plugin
- **File**: `src/editor/plugins/comments.ts` (new file)
- **Target**: New ProseMirror plugin
- **Action**: Create a plugin that renders highlight decorations at comment anchor positions. Decorations are yellow background for unresolved, grey for resolved. Clicking a decoration emits a `comment-select` event with the comment ID. Anchor positions update on document transactions using ProseMirror's `Mapping` API.
- **Reasoning**: Decorations (not marks) are the correct ProseMirror pattern — they don't modify the document schema and survive edits to surrounding content.
- **Depends on**: Change 2 (loads comments from API)

### 4. Add text selection comment trigger
- **File**: `src/editor/components/SelectionToolbar.tsx`
- **Target**: `SelectionToolbar` component
- **Action**: Add a "Comment" button to the existing floating toolbar that appears on text selection. On click, capture the selection range and open the comment composer (Change 5).
- **Reasoning**: Follows the existing selection toolbar pattern (already has Bold, Italic, Link buttons). Users expect comment creation from text selection.
- **Depends on**: Change 3 (needs decoration plugin registered)

**Checkpoint**: Select text, click Comment button, verify highlight decoration appears at the correct position. Edit text before and after the highlight — verify anchor positions stay correct.

## Phase 3: Comment UI

### 5. Add comment composer and thread view
- **File**: `src/editor/components/CommentThread.tsx` (new file)
- **Target**: New `CommentThread` component
- **Action**: Inline popover anchored to the decoration. Shows: existing thread (if any), reply textarea, resolve button (for thread author and document owner). Uses the existing `Popover` component from `src/components/ui/Popover.tsx`. Submits via the API from Change 2.
- **Reasoning**: Inline popover (not sidebar) chosen based on research — matches our layout and the Notion pattern.
- **Depends on**: Changes 2, 3, 4

### 6. Add comment indicators in document gutter
- **File**: `src/editor/components/Gutter.tsx`
- **Target**: `Gutter` component (existing)
- **Action**: Add small comment count badges next to lines that have associated comments. Clicking a badge scrolls to and opens the corresponding comment thread.
- **Reasoning**: When documents have many comments, users need to scan for discussion without reading the full document. Gutter indicators are the standard pattern (VS Code, Google Docs).
- **Depends on**: Change 3 (reads decoration positions)

**Checkpoint**: Full flow — select text, create comment, reply in thread, resolve. Verify gutter indicators appear and clicking them opens the thread. Test with 10+ comments on a document.

## Edge Cases & Risks
- User deletes the text a comment is anchored to — decoration plugin should detect zero-width anchors and mark comments as "orphaned" with a visual indicator.
- Two users comment on overlapping selections — decorations can overlap; clicking in the overlap zone should show both threads in the popover.
- Very long threads — popover should scroll internally with a max height, not overflow the viewport.
- Concurrent edits to the same region — anchor position mapping handles this, but test with rapid sequential edits to verify.

## Validation
- [ ] User can select text and create a comment
- [ ] Comment appears as a highlight in the document
- [ ] Clicking the highlight opens the thread
- [ ] Users can reply to create a thread
- [ ] Thread author or document owner can resolve a comment
- [ ] Resolved comments show as grey highlights
- [ ] Editing text around a comment preserves the anchor position
- [ ] Deleting commented text shows an "orphaned" state
- [ ] Gutter badges show comment count per line
- [ ] All interactions are keyboard-accessible
```

**Why this works**: Phases group by system layer (data, editor, UI) with clear checkpoints. Each phase builds on the previous one. The dependency chain is explicit — you can't build the popover UI before the API and decoration plugin exist. Research directly influenced two decisions (inline popover over sidebar, decorations over marks).

## Loop-Compatible Output Example

When a plan is destined for autonomous loop execution, Phase 4b produces a flat `IMPLEMENTATION_PLAN.md` alongside the rich plan.
Given the phased plan above (comment threads), the loop-ready output would be:

```
# Implementation Plan

## Goal
Add threaded comments to documents so collaborators can discuss specific text selections inline.

See `docs/plans/comment-threads.md` for full context.

## Tasks
- [ ] Add Comment model to database — `prisma/schema.prisma` — new model with anchor positions, threading via parentId
- [ ] Add comment CRUD API endpoints — `src/api/comments.ts` — REST endpoints matching existing API patterns
- [ ] Add comment decoration plugin — `src/editor/plugins/comments.ts` — ProseMirror decorations for highlight + anchor mapping
- [ ] Add comment trigger to selection toolbar — `src/editor/components/SelectionToolbar.tsx` — "Comment" button on text selection
- [ ] Add comment composer and thread view — `src/editor/components/CommentThread.tsx` — inline popover with reply + resolve
- [ ] Add comment indicators in gutter — `src/editor/components/Gutter.tsx` — count badges linking to threads

## Decision Log
<!-- Populated by Claude during implementation -->

## Issues Found
<!-- Populated by Claude during implementation -->
```

**Key properties**: Each task is one line, starts with `- [ ]`, includes the file path, and is completable in a single loop iteration.
The loop reads `[ ]` markers to find the next task and marks them `[x]` on completion.

## What Makes These Work

Both examples follow the same principles:

1. **Specific actions, not vague directives** — "Add a `useEffect` hook that registers a `keydown` listener" vs "add keyboard support"
2. **Real file paths** — every change names the exact file and target within it
3. **Reasoning for every decision** — not just what, but why this approach over alternatives
4. **Dependency chains** — implementers know what order to work in
5. **Research-informed design** — external patterns cited where they influenced the plan
6. **Testable validation** — each criterion can be verified with a specific action and expected result
7. **Concrete edge cases** — specific scenarios with specific mitigations, not "handle errors gracefully"
