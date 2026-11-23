# Changelog: sync-docs

Newest first. Each entry: date, what changed, and what went wrong in use that prompted it.

- 2026-11-23: first version. Stdlib check script plus a judgment method. Tuned on a real repo
  and an independent review: bare file names, paths relative to a sub-package and intentional
  "do not create X" mentions flagged as missing paths (bare names are now warnings, paths match
  by suffix, `check-docs: ignore` markers exist); a tool-managed `BEGIN`/`END` block in an
  agent guide could never go green (now skipped like a generated file); a rule line saying
  "do not edit" made a whole guide count as generated (now only a header comment counts);
  records could fail the gate although they must not be edited (their findings are warnings).
