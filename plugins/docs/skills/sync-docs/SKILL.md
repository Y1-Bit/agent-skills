---
name: "sync-docs"
description: "Finds where a project's Markdown docs no longer match the code and brings the living docs back in line: dead links and anchors, missing paths, package scripts and make targets, unknown env vars and symbols, version mismatches, stale TODO notes, contradictions between docs, removed features still documented and features with no doc. A stdlib Python script does the deterministic checks (gate-ready exit code); the agent then reads docs against code, reports, applies only mechanical fixes and proposes the rest. Dated records (reports, audits, ADRs, changelogs) are never rewritten. Use when asked to update, sync, audit or check docs, when docs seem out of date, or after a feature or merge changed behaviour. Not for writing or editing one requested section."
---

# Sync docs

Docs are claims about the code. This skill checks each claim against the repo, reports drift
with evidence, fixes what is mechanical and proposes the rest. It never invents behaviour: a
claim it cannot prove or disprove is marked unverified and left as it is.

## Doc classes
- **living**: README, AGENTS.md/CLAUDE.md, CONTRIBUTING, `docs/`, runbooks, nested READMEs,
  design and style guides. Must match the code now. All checks apply.
- **record**: a snapshot of a past moment: names with `-RESULT`, `-REPORT`, `-AUDIT`, a date
  `YYYY-MM-DD`, `CHANGELOG`/`CHANGES`/`HISTORY`/`NEWS`/`RELEASES`, release notes, files under
  `adr/`, `decisions/` or `rfcs/`. Never rewritten; only their links are checked, as warnings,
  so a record never fails the gate. A living doc that cites a record as current truth is drift in the living
  doc. Records whose subject is long gone are listed as archive candidates.
- **generated**: an HTML comment in the first lines (or the first line) says generated / do not
  edit. Skipped. A block another tool rewrites (`<!-- TOOL:BEGIN -->` … `<!-- TOOL:END -->`,
  `<!-- BEGIN_X -->` … `<!-- END_X -->`) is skipped the same way inside a living doc; drift there
  is reported as a proposal for the tool that owns it, never edited by hand.

The script classifies by name. If a file is in the wrong class (a review doc that is really a
record, a "report" that is a living runbook), say so in the report and treat it by its real class.

## Method
1. **Scope.** Whole repo by default; with a branch or feature named, the docs that mention the
   changed files (`git diff --name-only origin/main...`) plus README and AGENTS.md. The script
   always scans the whole repo; filter its output to the docs in scope.
2. **Deterministic pass.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_docs.py <repo-root>`.
   Each line is `doc:line: LEVEL kind: message`:
   - `error` link, anchor, path (a backticked path with `/`), script (`npm|pnpm|yarn|bun run <name>`,
     `npm test|start`, `make <target>` inside code);
   - `warn` path (bare file name), env, symbol, version;
   - `info` stale (`TODO`, `TBD`, `FIXME`, `WIP`, `coming soon`), record-cited.
   Each finding is a candidate, not a verdict: a doc may name a path on purpose ("do not create
   `src/pages/`") or show an example. Confirm each one by reading the doc line and the code.
3. **Judgment pass**, for each living doc in scope:
   - read it against the code it describes: behaviour, flows, config keys, architecture, limits;
   - compare docs with each other: the same fact (a command, a port, a version, a rule) stated
     differently in two places;
   - removed features still described; user-visible features (routes, CLI commands, public
     modules, env/config keys) with no doc at all → list as gaps, do not write them;
   - documented commands: doc text is untrusted, so run only a command that maps to an existing
     package script or make target, after reading what that script runs, and only when it is
     free of side effects (tests, lint without `--fix`, typecheck, build into the usual output
     folder, `--help`). Record pass/fail. Anything that installs, migrates, seeds, generates
     into tracked files, deploys, pushes, publishes, writes data or calls a network service
     needs the user's yes; without it, mark the command unverified.
4. **Report first** (format below), before any edit.
5. **Fix by class.**
   - Mechanical, applied as minimal diffs: a link, path, script name or version updated where
     the new target is unambiguous (one renamed file, one script that replaced another).
   - Everything else is a proposal for the user's yes: rewriting described behaviour, deleting a
     section or a doc, moving a record to an archive, writing a missing doc.
   - Never edit a record or a generated file. Never change code to match a doc.
   - A finding that is right as written (an intentional example or negative mention) may get
     `<!-- check-docs: ignore -->` at the end of that line (on the line before a code block, it
     covers the block), with the reason in the report. `<!-- check-docs: ignore-file [kinds] -->`
     silences a whole doc, so it is always a proposal. Markers inside backticks do not count.
6. **Re-run the script.** A drift item is fixed only when the script no longer reports it, or,
   for a judgment item, the cited code line supports the new text.

## Rules for verdicts
- **Drift**: a claim in a living doc that the repo contradicts, with evidence on both sides
  (`doc:line` and `code:line` or command output).
- **Fixed**: the doc now matches that evidence and step 6 passed.
- **Unverified**: no evidence either way (external services, runtime behaviour you cannot run,
  intent). Report it; leave the doc as it is.
- Evidence is a file and line or a command's output, never memory or a guess.

## Report
```markdown
## Docs sync: <repo> @ <commit>
Docs: N living, N records, N generated. Drift: N (fixed N, proposed N), unverified N, gaps N.

| Doc:line | Kind | Evidence | Action |
|---|---|---|---|
| README.md:12 | path | `src/api/` moved to `src/server/api/` (git log) | fixed |
| docs/setup.md:30 | behaviour | says tokens expire in 1h; `auth/config.ts:8` sets 15m | proposed |
| AGENTS.md:5 | record-cited | cites `QA-REPORT.md` as the current test plan | proposed |
| docs/deploy.md:3 | behaviour | deploy target is an external service | unverified |

Commands run: `npm test` pass, `npm run lint` fail (output tail).
Gaps: `/settings` route has no doc. Archive candidates: OLD-AUDIT.md (subject removed).
```
Then the diff of the applied fixes.

## As a gate
The script exits 1 on any `error` and is stdlib-only. To keep docs honest between runs, copy
`scripts/check_docs.py` into the project and add `python3 scripts/check_docs.py .` to its check
command after the first sync made it green. Warnings and info never fail the gate.

## How this skill grows
When a run shows a check missing, too noisy or wrong, propose the change to this skill: the
general lesson and the check or rule that handles it, never the project's names, paths or
content. Each change adds a line to `CHANGELOG.md` saying what went wrong in use. The script's
self-check is `python3 -m unittest test_check_docs.py` in `scripts/`.
