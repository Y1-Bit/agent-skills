# Python guardrails (FastAPI / aiogram / any)

Working reference: `kit/python/` (`make check`, `make demo-violations`).

1. **ruff**: `select = ["ALL"]`; ignore only `D`, `COM812`, `ISC001`, `CPY`. Thresholds: mccabe 6;
   pylint max-args 5, max-positional-args 2, max-branches 6, max-statements 20, max-returns 3,
   max-nested-blocks 3, max-public-methods 10. `PLR1702` (nesting) and `PLR0904` (public
   methods, i.e. interface width) are preview rules: enable them explicitly with
   `preview = true`, `explicit-preview-rules = true`, `extend-select = ["PLR0904", "PLR1702"]`,
   or they silently do not run. `ban-relative-imports = "all"`. banned-api:
   `datetime.datetime.now`, `datetime.datetime.utcnow` (inject a Clock), `typing.Any`.
   per-file-ignores: tests (S101, PLR2004), infrastructure (TID251); each names exact paths and a
   reason. Security (S) rules are suppressed only inline, with the invariant that makes the
   finding safe.
2. **mypy** strict + `warn_unreachable` + error codes `ignore-without-code`, `redundant-expr`,
   `truthy-bool` (or Pyright strict; keep editor and CLI on the same checked-in config).
3. **import-linter**: global layers `entrypoints → <contexts> → shared`; per-context layers
   `infrastructure → application → domain`; forbidden `fastapi/pydantic/sqlalchemy/aiogram`
   from domain and application. With two or more contexts or features add an `independence`
   contract between them and a `protected` contract so only the package's `__init__.py` is
   imported from outside.
4. **ast-grep** rules, each with valid and invalid cases in `ast-grep/tests/`:
   - `no-try-in-core` (domain/application);
   - `domain-errors-only` (no raising built-ins in the domain);
   - `thin-routes` (no try/if in route or handler functions);
   - `no-escape-hatch-comments` (noqa, type: ignore, pragma: no cover in src);
   - `no-bool-flag-pairs` (`is_*` bool pairs → enum);
   - `commit-only-in-uow` (no hand-written commit/rollback).
5. **File length** script: 250 lines max (count every line of a module).
6. **Tests**: branch coverage ≥ 95%, mutation testing (mutmut, score ≥ 85%), hypothesis for
   value objects. Coverage alone let a real off-by-one through in the kit.
7. **Reference slice**:
   - a shared `DomainError` hierarchy (InvalidValue/NotFound/Conflict/RuleViolation);
   - `BoundedText`/`PatternText` value-object bases;
   - an aggregate with invariant methods;
   - Command + Handler use cases;
   - Protocol ports owned by their use case;
   - an in-memory adapter and a composition root;
   - ONE error handler per edge mapping categories via MRO;
   - `@transactional` + `@logged` decorators over a unit of work;
   - a data-driven bot FSM (`Step` table) instead of copy-pasted step handlers.

No tool counts imports per module in Python; reviews hold modules to the same bound as
TypeScript (`references/design-rules.md`).
