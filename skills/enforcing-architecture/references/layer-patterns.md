# Common Layer Patterns by Stack

## Table of Contents

- [Detection Signals](#detection-signals)
- [Next.js / React](#nextjs--react)
- [Express / Fastify / Node.js API](#express--fastify--nodejs-api)
- [Django](#django)
- [Rails](#rails)
- [Go](#go)
- [General SPA](#general-spa-reactvuesvelte)
- [Monorepo / Feature-Sliced](#monorepo--feature-sliced)

## Detection Signals

Match the first pattern where 2+ signals are present.

| Signal Files/Dirs | Likely Pattern |
|-------------------|---------------|
| `app/` + `next.config.*` | Next.js |
| `src/controllers/` + `src/services/` + `src/models/` | Node.js API (classic layers) |
| `*/models.py` + `*/views.py` + `*/urls.py` | Django |
| `app/models/` + `app/controllers/` + `config/routes.rb` | Rails |
| `cmd/` + `internal/` or `pkg/` | Go |
| `src/components/` + `src/hooks/` + `src/pages/` or `src/views/` | General SPA |
| `packages/` or `apps/` + workspace config | Monorepo |
| `src/features/` with per-feature subdirs | Feature-Sliced |

## Next.js / React

```
  app/ (routes, pages, layouts)
         |
  components/
         |
  lib/ or services/
         |
  data/ or db/
         |
  [Shared: types/, utils/, config/]
```

**Non-obvious rules:**
- `components/` must not import from `data/` — only `lib/` and `app/` touch the data layer
- Server Components vs Client Components: `data/` is server-only; enforce `"use client"` boundary

## Express / Fastify / Node.js API

```
  routes/ or controllers/       (HTTP layer)
         |
  services/                     (business logic)
         |
  models/ or repositories/      (data access)
         |
  [Shared: utils/, types/, config/, middleware/]
```

**Non-obvious rules:**
- Services must not reference `req`/`res` — HTTP concerns stay in routes/controllers
- Middleware is shared (cross-cutting), not a layer in the dependency chain

## Django

```
  views.py / viewsets.py
         |
  services.py (if exists)
         |
  models.py
         |
  [Shared: utils/, templatetags/, management/]
```

**Non-obvious rules:**
- Each Django app is a boundary — cross-app imports go through public interfaces (models, services)
- Many projects skip the services layer; views call models directly — that's valid for smaller apps

## Rails

```
  controllers/
         |
  services/ (if exists)
         |
  models/
         |
  [Shared: lib/, helpers/, concerns/]
```

**Non-obvious rules:**
- Concerns are shared mixins, not a layer — they can be included anywhere
- Service objects are optional; enforce only if the project already uses them

## Go

```
  cmd/                          (entry points)
         |
  internal/
    ├── handler/ or api/
    ├── service/
    └── store/ or repo/
         |
  pkg/                          (public library)
```

**Non-obvious rules:**
- `pkg/` must not import from `internal/` or `cmd/` — it's the public API
- Go enforces `internal/` visibility natively, but cross-package direction within `internal/` needs the check script

## General SPA (React/Vue/Svelte)

```
  pages/ or views/
         |
  features/ or modules/
         |
  components/
         |
  hooks/ or composables/
         |
  services/ or api/
         |
  [Shared: utils/, types/, constants/]
```

**Non-obvious rules:**
- Features are self-contained — no cross-feature imports; communicate through shared state or events
- API layer is standalone — UI components use hooks/composables, not raw fetch

## Monorepo / Feature-Sliced

```
  packages/ or apps/
    ├── app-web/
    ├── app-api/
    ├── pkg-shared/
    └── pkg-ui/
```

**Non-obvious rules:**
- Apps can import packages but not other apps
- Packages must not import from apps
- Cross-package imports use the package's barrel export (`index.ts`), not deep paths
