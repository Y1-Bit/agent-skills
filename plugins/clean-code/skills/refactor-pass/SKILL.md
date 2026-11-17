---
name: "refactor-pass"
description: "Behavior-preserving cleanup pass after an agent wrote a feature: extract long functions, centralize error handling, introduce value objects. Use when asked to refactor or clean up recent code."
---

# Refactor pass

A separate pass, run AFTER a feature works. The writing agent optimizes for "it works". This pass optimizes for "a senior engineer would write it this way". Behavior must not change.

## Rules
1. Scope: only files changed in the current branch (`git diff --name-only origin/main...`) unless told otherwise.
2. Tests must be green before you start and after every step. If there are no tests for the code you touch, write characterization tests first.
3. Never change public behavior, API shapes, or error codes. Never add `noqa`, `type: ignore`, `eslint-disable`, `as` casts or `!`.
4. Run the project's check command (`make check` / `npm run check`) at the end. It must pass.

## Checklist (apply in this order)
1. **Validation scattered in methods** → value objects / zod brands. Each concept validates itself once at construction.
2. **Long parameter lists (>4)** → group cohesive params into a value object or command dataclass.
3. **Boolean state flags (`is_active` + `is_deleted`, `isLoading` + `isError`)** → enum / discriminated union.
4. **try/except or try/catch in domain, use cases, routes or components** → raise a domain error (or return `Result`) and let the single edge handler / ErrorBoundary deal with it.
5. **Business conditions in routes/handlers/components** → move into aggregate methods or use cases.
6. **Functions over ~20 statements or with nesting > 2** → extract well-named functions. Prefer guard clauses over nested ifs.
7. **Duplicated logic in 3+ places** → one function or decorator. Two places is not yet duplication.
8. **Cross-cutting concerns repeated per function (logging, retries, transactions, timing)** → decorator, middleware or context manager.
9. **Global time/randomness/IO in core code** → inject via a port (Clock, IdGenerator).
10. **Comments that explain WHAT** → delete them and rename instead. Keep only comments that explain WHY.

## Output
Small commits, one checklist item each. Finish with a short list: what changed, which items were skipped and why. List any correction that came up twice: it is a candidate for a new lint rule (propose the rule).