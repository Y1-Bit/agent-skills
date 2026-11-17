# Changelog: setup-guardrails

Newest first. Each entry: date, what changed, and what went wrong in use that prompted it.

- 2026-11-17: first public version. SKILL.md is the stack-neutral method; stack details moved to
  `references/python.md` and `references/typescript-react.md`; new `references/design-rules.md`
  (feature slices, narrow interfaces, coupling, smells, review checklist, per-rule ratchet) from
  a larger codebase where green linters still let god hooks and wide interfaces through. Kit:
  the example context is a neutral library catalog; interface width enforced (ESLint selector,
  ruff `PLR0904`); `PLR1702` and `PLR0904` enabled explicitly because preview rules did not run
  and the kit's own script broke the nesting limit unnoticed; hook and demo scripts committed
  executable because the Stop hook failed with "Permission denied" in a copied project.
