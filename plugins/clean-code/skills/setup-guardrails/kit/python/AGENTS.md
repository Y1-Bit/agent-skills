# AGENTS.md

Short on purpose. Most rules here are **enforced by tooling** — this file explains the
intent so you fix root causes instead of fighting the checker.

## Definition of done
`make check` passes. Never finish a task with it red. Never add `# noqa`, `# type: ignore`,
or `# pragma: no cover` in `src/` (it is a lint error); fix the design instead.
If you believe a rule is wrong, say so in your summary — don't work around it.

## Before writing code
Read the reference context `src/app/books/` and copy its shape for new work.
A new bounded context = `src/app/<context>/{domain,application,infrastructure}` and a new
block in the import-linter contracts in `pyproject.toml`.

## Where things go
| Layer | Contains | May import |
|---|---|---|
| `domain/` | aggregates, value objects, domain errors. Pure Python, no I/O | `shared.domain` |
| `application/` | one use case per module: `Command` dataclass + `Handler` with one `__call__`; `ports.py` with Protocols | `domain` |
| `infrastructure/` | adapters implementing ports (DB, HTTP clients, clock, ids) | `application`, `domain` |
| `entrypoints/` | `http/` (FastAPI), `bot/` (aiogram), CLI; `container.py` composition root; ONE error mapper per edge | everything |

## Patterns to use
- **Validation lives in value objects.** A field with rules gets its own type
  (`BookTitle(BoundedText)`, `CountryCode(PatternText)`). Aggregates hold valid types, so they
  don't re-validate. Never write a chain of `_validate_<field>` methods.
- **Too many arguments → a value object.** Group cohesive fields (`BookProfile`).
- **State is an enum, not a set of booleans.** `status: BookStatus`, not `is_active` + `is_deleted`.
- **Invariants live in aggregate methods** (`book.withdraw()`), not in handlers or routes.
- **Errors:** domain/application only *raise* `DomainError` subclasses
  (`InvalidValueError`, `NotFoundError`, `ConflictError`, `RuleViolationError` or a specific
  subclass). They never catch. `entrypoints/http/error_handlers.py` maps categories to responses.
  A new error needs the right base class, not a new handler.
- **Transactions:** repositories are reached via `self.uow.<repo>`; decorate write use cases with
  `@logged` + `@transactional`. Never call `commit()`/`rollback()` yourself (lint error).
- **Logging context** (request_id / update_id) is bound by middleware. Don't pass loggers or ids
  through functions; use `structlog.get_logger()` and log events with key-values.
- **Bot flows** are data-driven: add a `Step(state, field, parser, prompt)` row instead of a new
  copy-pasted handler. Handlers in `bot/handlers.py` have no `if`/`try`; input helpers live in `forms.py`.
- **Enums from user input** go through a `parse()` classmethod that raises `InvalidValueError`
  (a bare `Enum("x")` raises `ValueError` → crash).
- **Time and ids are injected** (`Clock`, `BookIdGenerator` ports). No `datetime.now()` in core code.
- **Routes are thin:** parse → `request.to_command()` → call one handler → serialize. No `if`, no `try`.
- **Small functions.** Limits: complexity 6, 20 statements, 5 args, 3 nesting levels, 250 lines
  per file. When you hit one, extract a well-named function or a new type, don't compress code.

## Tests
- `make check` enforces ≥95% branch coverage. Coverage only proves code RAN.
- `make mutate` (CI, slow) proves tests would NOTICE breakage: mutation score ≥85% on `domain/`.
  For every survivor, `mutmut show <name>` shows the change no test caught → add the assertion.
- Value objects: add a hypothesis property test (see `test_value_objects_properties.py`).
- Bot: end-to-end through the real Dispatcher with `RecordingBot` (`tests/bot/`).
- Domain: plain unit tests, no fakes needed.
- Use cases: `InMemoryUnitOfWork` (asserts `commits`, rolls back on error) + `FixedClock` + `SequentialIds` from `tests/fakes.py`.
- Edge: one test per error category mapping (see `tests/integration/test_http.py`).
