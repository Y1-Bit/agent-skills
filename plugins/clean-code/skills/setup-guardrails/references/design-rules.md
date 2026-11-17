# Design rules (any stack)

Linters keep functions small; these rules keep the structure right. Enforce what a tool can
check; reviews apply the rest even where every linter passes.

## Feature slices
- Organise code by use case, not by technical kind. One user-facing capability lives in one
  folder: in TypeScript `features/<feature>/` with `model/` (its port, its narrow hook, its view
  mapping), `ui/` (its screens) and `adapters/` (one implementation of the port per external
  system); in Python a feature is a subpackage with its own layer folders.
- A feature's public entry is `features/<feature>/index.ts` (Python: the subpackage
  `__init__.py`); everything else in it is private. Other code imports it only through that
  entry. Enforce it: `eslint-plugin-boundaries` (`fileInternalPath: index.ts`); import-linter
  `protected` for a feature's internals and `independence` between sibling features.
- Pages and the composition root compose features and hold no use-case logic.
- Domain and shared runtime modules never import a feature.

## Narrow interfaces
- An interface belongs to its consumer and stays narrow: at most 10 operations (methods or
  function-typed members; data fields do not count) on one interface, type, class or Protocol.
  Enforced by the ESLint width selector and ruff `PLR0904`.
- A screen or use case that needs more uses two narrow ports or hooks, not a wider one.

## Coupling and size
- A module imports at most 12 other modules, 20 in tests and fixtures
  (`import-x/max-dependencies`; reviews hold languages without such a tool to the same bound).
- Size limits (complexity, nesting, parameters, function and file length) signal a missing
  abstraction: split by responsibility, never by line count.
- Pick strict limits for a new project (the kit's). In a large existing codebase, start from
  limits it can reach (for example complexity 12, 80 lines per function, 400 per file) and lower
  them as the ratchet shrinks.

## One reason to change
- Each module, hook, class and function serves one use case. Extend by adding a module, not by
  adding a flag or a field to a shared one.
- Inject collaborators (clients, clocks, storage) instead of constructing them in business logic,
  so every unit is testable without a network.
- Add a port or adapter only where a real external boundary or a second implementation exists.

## Names, types, errors
- Names state the domain: no abbreviations beyond common ones (`id`, `url`); no
  `data`/`info`/`manager`/`helper`/`util` without a domain noun; booleans read as predicates
  (`isReady`, `has_access`); a value with a unit carries it in its name (`timeoutMs`,
  `priceCents`).
- Types are always known: no `any`, unchecked casts or non-null assertions in production code;
  parse external input into typed domain values at the boundary; exhaustive `switch`/`match`
  over unions and enums.
- Raise typed domain errors with actionable messages; never swallow an exception or log and
  continue on an unexpected state.
- No import cycles, dead code, commented-out code, or printing outside CLI entry points.

## Smells to reject, whatever the linters say
- **God hook or façade**: one controller, context, store or service that bundles unrelated use
  cases and hands everything to every consumer.
- **Wide interface**: a type of which most consumers read a small slice.
- **Split by line count**: code moved into `part`/`helpers`/`shared` files, or into hooks that
  are reassembled into one aggregate, only to pass a size limit.
- **Flat layer folder** mixing features: `components/`, `hooks/`, `services/` holding unrelated
  features, or an integration folder holding one adapter per feature.
- **Pass-through mapping**: a view or adapter that only renames fields to feed an aggregate.
- **Reaching into internals** of another feature, or a domain module importing a feature.

## Review checklist (every change, before the gates)
- Name each changed module's one consumer and one reason to change.
- List the operations each new or widened interface offers and which consumers use which.
- Check that every cross-feature import goes through the feature's entry.
- Reject any smell above.

## Ratchet (existing codebase)
- No rule is weakened, no limit raised and no suppression added to land a change.
- Violations that exist when a rule is introduced may be frozen for that rule only (ESLint
  `--suppress-rule <rule>`, ruff per-file-ignores naming exact files with a reason,
  import-linter `ignore_imports`, ast-grep `ignores`), each with a named owner. Fixing a file
  removes its entries; never regenerate a suppression file to hide new violations.
- Security findings are suppressed only inline, with the invariant that makes them safe.

## One gate for many components
In a repository with several components, one script runs every component's native check, with
each gate set to `enforce` or `report` in a checked-in file (move a gate from report to enforce
once it is clean). Pre-commit runs it on staged files, CI runs the same script, and the Stop hook
runs the fast subset.
