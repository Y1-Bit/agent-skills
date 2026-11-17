---
name: "setup-guardrails"
description: "Set up deterministic guardrails so coding agents write clean, layered code: strict linters, architecture rules for agents (layer and feature-slice contracts, narrow interfaces), custom ast-grep/ESLint rules, one check command as the definition of done, a Stop-hook gate and a short AGENTS.md. Works for a new or an existing project; ships references and a working kit for Python and TypeScript/React and a method for adding other stacks. Use when asked to set up linters, clean-code rules, quality gates or agent guardrails, or when the same correction to an agent keeps coming back."
---

# Agent guardrails setup

Principle: every correction you would give an agent twice becomes a deterministic check, not
prose. A rule in AGENTS.md is a request; a lint rule is enforcement. AGENTS.md stays short and
explains the intent behind the tooling, so agents fix causes instead of fighting the checker.

## Method
1. **Collect the corrections.** List what reviews and the user keep correcting: long functions,
   try/except everywhere, layer leaks, wide "service" types, silenced checkers, untested logic.
   For an existing project, also read its review history and its AGENTS.md.
2. **Pick a check for each.** Prefer, in order: a built-in rule of the stack's linter or type
   checker; a layer or boundary contract; a small custom rule (ast-grep, ESLint
   `no-restricted-syntax`) with valid and invalid test cases. Only what no tool can check stays as
   prose in AGENTS.md (the design rules in `references/design-rules.md`).
3. **One command is the definition of done** (`make check`, `npm run check`, or one gate script
   that runs every component's check). Wire the same command into pre-commit, CI and a Claude
   Code Stop hook that runs it and exits 2 with the tail of the output on failure (skip when
   `stop_hook_active` is true). A PostToolUse hook may format and autofix on Edit/Write. Commit
   hook scripts with the executable bit.
4. **Prove each rule fires.** Keep typical agent output in `examples/bad/` and a demo-violations
   script that lints it as if it were real code. A rule that never fires on its example is not
   running (preview rules, wrong globs, overrides that replace a rule list).
5. **Existing codebase: ratchet, never big-bang.** Turn the rules on, freeze today's violations
   per rule with an owner, and shrink the frozen list as modules are touched. Never regenerate a
   suppression file to hide new violations (`references/design-rules.md`, "Ratchet").
6. **Verify before handing over**: the full check is green on the real code, and every rule
   fires on the bad examples.

Hooks from the kit are examples: install them into a project only with the user's yes, never
into the user's own settings.

## Stacks
- Python (FastAPI, aiogram, any): `${CLAUDE_SKILL_DIR}/references/python.md`
- TypeScript/React: `${CLAUDE_SKILL_DIR}/references/typescript-react.md`
- Stack-neutral design rules and review checklist: `${CLAUDE_SKILL_DIR}/references/design-rules.md`

A working reference of each ships in `${CLAUDE_SKILL_DIR}/kit/` (read `kit/README.md` first):
`kit/python/` and `kit/frontend/` each pass their own check and contain `examples/bad/` plus a
demo-violations script. For a new project, copy the matching folder and rename the example
context (a small library catalog). For an existing project, take configs and rules from it and
follow the ratchet. Keep the kit's lockfiles out of the target unless that project adopts the
kit's dependencies as they are.

**A stack with no reference yet**: apply the method with that stack's own strict linter, type
checker and boundary tool; record the result as `references/<stack>.md` in the same shape as the
existing ones (thresholds, contracts, custom rules, patterns) and propose it to this skill.

## How this skill grows
When a project shows a rule missing, wrong or too strict, propose the change to this skill: the
general lesson and the check that enforces it, never the project's code, names, domain or
internal details. Each change adds a line to `CHANGELOG.md` saying what went wrong in use.
