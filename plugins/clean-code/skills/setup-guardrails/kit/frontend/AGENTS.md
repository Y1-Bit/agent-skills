# AGENTS.md

Most rules below are **enforced by ESLint/tsc**. This file explains the intent so you fix the
root cause instead of fighting the checker.

## Definition of done
`npm run check` passes (tsc, eslint with `--max-warnings 0`, vitest). Inline
`eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `as` casts and `!` are all errors. If a rule
seems wrong, say so in your summary — don't work around it.

## Layers (imports only flow to the right)
`app → features → entities → shared`

| Layer | Contains |
|---|---|
| `src/app` | providers, routing, the single `ErrorBoundary` |
| `src/features/<slice>` | user actions: `model/` (hooks, state), `ui/` (components). Public API: `index.ts` |
| `src/entities/<slice>` | domain types as zod schemas, API calls for that entity. Public API: `index.ts` |
| `src/shared` | `api/http.ts` (the only `try/catch`), `lib/` (Result, generic hooks), ui kit |

Import other slices **only through `index.ts`**, using the `@/` alias.

## Patterns to use
- **Parse, don't cast.** Data from the network or a form goes through a zod schema. Branded
  types (`BookId`, `CountryCode`) come from parsing, never from `as`.
- **Expected failures are values:** API calls return `Result<T, AppError>`. Check `result.ok`.
  No try/catch outside `shared/api`. Bugs go to the `ErrorBoundary`.
- **UI state is a discriminated union** (`idle | invalid | submitting | failed | done`), never
  a bag of `isLoading`/`isError`/`data` booleans. `switch` on it — exhaustiveness is checked.
- **No `useEffect` in product code.** Derive values during render; do work in event handlers;
  for data fetching use the project's data hook (or add one to `shared/lib` once, well-tested).
- **Small units.** Limits: complexity 6, cognitive complexity 8, 40 lines per function,
  15 statements, 3 params, 250 lines per file. When you hit one, extract a component, hook or
  pure function — don't compress code.
- **Tests must kill mutants.** `npm run mutate` (Stryker) breaks the build below 80% on
  `entities/*/model` and `shared/lib`. Assert exact messages, boundaries and enum values.
- Reference implementation to copy: `src/features/catalog-book` + `src/entities/book`.
