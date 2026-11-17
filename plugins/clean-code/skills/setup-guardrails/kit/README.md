# Guardrails kit

A starter kit that makes coding agents write clean, layered code. The principle comes from
Lauren Tan's talk *All Code Is Slop (Except Mine)*: whenever you correct an agent, turn the
correction into a **deterministic check**, not another line of prose. A rule in AGENTS.md is a
request. A lint rule is enforcement.

```
python/     FastAPI + aiogram + DDD/Clean Architecture reference (ruff ALL, mypy strict,
            import-linter, ast-grep rules with tests, Stop-hook gate)
frontend/   React + TS reference (typescript-eslint strict, layer boundaries,
            banned patterns, zod brands, Result, Stop-hook gate)
```

Both kits pass their own checks (`make check` / `npm run check`). Both also contain
`examples/bad/`: typical agent output plus a `demo-violations` script that shows which rule
catches which habit.

## What mutation testing found in this very kit
With 99% line+branch coverage, mutmut still had 17/56 mutants surviving. Among them was a
real off-by-one (`<=` → `<` at the max length) that no test noticed. Stryker on the frontend
started at a 41% score with all tests green. Both were raised to ≥90% by
`tests/unit/test_mutation_gaps.py` and `book.mutation-gaps.test.ts`. That is the case for
running it.

## Agent habit → what stops it

| Habit | Python | Frontend |
|---|---|---|
| Long, overloaded functions | `C901`=6, `PLR0915` 20 statements, `PLR0912/0911/1702` | `complexity` 6, `sonarjs/cognitive-complexity` 8, `max-lines-per-function` 40, `max-statements` 15 |
| Huge files | `scripts/check_file_length.py` (250) | `max-lines` 250 |
| 7-argument constructors | `PLR0913` 5, `PLR0917` 2 positional → value object | `max-params` 3 → object param |
| try/except everywhere | ast-grep `no-try-in-core`, `thin-routes` + one central handler | `no-restricted-syntax: TryStatement` outside `shared/api` + `Result` + ErrorBoundary |
| `raise ValueError(...)` in the domain | ast-grep `domain-errors-only` | — (failures are `Result` values) |
| Copy-pasted `_validate_x` methods | value-object bases `BoundedText` / `PatternText` | zod schemas with `.brand()` |
| `is_active` + `is_deleted` | ast-grep `no-bool-flag-pairs` → enum | discriminated-union state (convention + exhaustive `switch`) |
| Silencing the checker | ast-grep `no-escape-hatch-comments` (`noqa`, `type: ignore`) | `noInlineConfig`, `ban-ts-comment`, `consistent-type-assertions: never`, `no-non-null-assertion` |
| Layer leaks (domain imports FastAPI, entities import features) | import-linter contracts | `boundaries/dependencies` + index.ts-only public API |
| One wide service/store type every caller reads a slice of | `PLR0904` max 10 public methods (preview rule, enabled explicitly) | `no-restricted-syntax` width selector: max 10 operations per interface, type literal or class |
| `datetime.now()` in core / `Any` | `TID251` banned-api | `no-explicit-any`, `strict-boolean-expressions` |
| `useEffect` for everything | — | banned in product code |
| Tests that assert nothing | coverage ≥95% branch + `make mutate` (mutmut, score ≥85%) + hypothesis | `npm run mutate` (Stryker, break <80%) |
| `commit()`/`rollback()`/logging boilerplate in every handler | `@transactional` + `@logged` decorators, UoW; ast-grep `commit-only-in-uow` | — |
| Copy-pasted bot step handlers, try/except in aiogram handlers | data-driven FSM (`Step` table), `DomainErrorMiddleware`, `thin-routes` covers `handlers*.py` | — |
| "Done" while checks are red | `.claude/settings.json` Stop hook → `scripts/agent_gate.sh` | same, `scripts/agent-gate.sh` |

## New project
1. Copy `python/` or `frontend/` and rename `app` / the example context.
2. Keep `src/app/books` (or `src/features/catalog-book`) as the **reference slice**
   until you have a real one of your own. Agents copy what they see, so the best prompt is a
   good example.
3. `make check` / `npm run check` is the single definition of done for humans, agents, CI
   and pre-commit.

## Existing project (ratchet, don't big-bang)
- **ESLint:** enable the config, then freeze today's violations one rule at a time with
  `eslint . --suppress-rule <rule>` (ESLint ≥ 9.24 records them in `eslint-suppressions.json`);
  only new code has to comply. Run `--prune-suppressions` as you clean up, and never suppress
  again to hide new violations.
- **ruff:** start with the thresholds on, but put legacy paths in `per-file-ignores`, then
  shrink that list module by module. Clean a module when you touch it.
- **import-linter:** use `ignore_imports` for existing violations and delete entries as you
  fix them.
- **ast-grep:** add `ignores:` globs to a rule for legacy folders.

## The loop that keeps it working
Every time you correct an agent in review:
1. Ask: "can this be a check?" Possible forms: a lint threshold, a banned API, an ast-grep
   rule, an import contract, or a type.
2. If yes, add it with an error message that names the **fix**, not just the problem. The
   agent reads that message.
3. For ast-grep rules, add a valid and an invalid case to `ast-grep/tests/rules-test.yml`.
4. Only if it really needs judgment does it go into AGENTS.md.

Over time code review shrinks to verification artifacts, and the codebase becomes the prompt.
