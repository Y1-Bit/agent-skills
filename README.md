# agent-skills

Claude Code skills that make coding agents write clean, layered code. Instead of longer
prompts, they turn recurring review corrections into deterministic checks: strict linters,
architecture rules, a single definition of done and a Stop-hook gate, plus a behavior-preserving
refactor pass. Each skill grows with the projects it is used in: a missing or wrong rule found
in real projects comes back as a general lesson and a check.

## Plugins and skills

The repository is a Claude Code plugin marketplace, `y1-skills`. Each plugin groups the skills
of one theme; a skill shows up in a session as `<plugin>:<skill>`.

### `clean-code`

| Skill | What it does | Use it when |
|---|---|---|
| `clean-code:setup-guardrails` | Sets up deterministic checks in a project: strict linters and type checking, layer and feature-slice contracts, narrow-interface and size limits, custom ast-grep/ESLint rules, one check command, a Stop-hook gate and a short AGENTS.md. References and a working kit for Python and TypeScript/React; a method for other stacks. | Starting a project, adding agents to an existing one, or the same correction to an agent keeps coming back. |
| `clean-code:refactor-pass` | Cleans up code an agent wrote after the feature works, without changing behavior: value objects, grouped parameters, enums instead of flag pairs, errors at one edge, smaller functions. | A feature works and its branch needs a senior-level cleanup before review. |

## Install

Needs Claude Code 2.1.273+. The repository is public, so no token or login is needed.

```bash
claude plugin marketplace add Y1-Bit/agent-skills
claude plugin install clean-code@y1-skills
```

Then turn on auto-update for the marketplace: in `~/.claude/settings.json` add
`"autoUpdate": true` to the `extraKnownMarketplaces."y1-skills"` entry, or use `/plugin` →
Marketplaces → y1-skills → Enable auto-update. Claude Code then refreshes the marketplace at
session start; a new version applies in the next session or after `/reload-plugins`.

Manual update at any time:

```bash
claude plugin marketplace update y1-skills && claude plugin update clean-code@y1-skills
```

`plugin.json` has no `version`, so the installed version is the commit SHA and every commit on
`main` is an update.

Install it the same way on any machine that only uses the skills; it needs no write access.

## Layout

```
.claude-plugin/marketplace.json            marketplace "y1-skills", one entry per plugin
plugins/<plugin>/.claude-plugin/plugin.json
plugins/<plugin>/skills/<skill>/           SKILL.md, CHANGELOG.md, supporting files
```

## Add a skill or a plugin

1. In a worktree branch, create `plugins/<plugin>/skills/<skill>/SKILL.md` with frontmatter
   `name` and `description` (the description decides when the skill triggers: say what it does
   and when to use it, under ~1,500 characters) and a `CHANGELOG.md`. Name skills by the action
   (`setup-guardrails`), plugins by the theme (`clean-code`).
2. A new theme gets its own plugin: `plugins/<plugin>/.claude-plugin/plugin.json` and an entry
   in `.claude-plugin/marketplace.json`, so it can be installed on its own.
3. Put supporting files next to `SKILL.md` and reference them as `${CLAUDE_SKILL_DIR}/<path>`.
4. Test locally without publishing: `claude --plugin-dir plugins/<plugin>` (a `--plugin-dir`
   copy replaces the installed plugin for that session), then `claude plugin validate .`.
5. Add the skill to the tables above, open a pull request; merge after the maintainer's yes
   (`CONTRIBUTING.md`).

Improvements come back as a general lesson (what went wrong and which check would catch it),
written without the code, names, domain or internal details of the project where it came up.

## Update a skill

See `CONTRIBUTING.md`: branch, change, a CHANGELOG line that says what went wrong in use,
pull request, the maintainer's yes, merge to `main`. Never edit the installed copy under
`~/.claude/plugins/cache/`: it is overwritten on the next update.

## Never in this repository

Secrets, keys, tokens, wallet material, `.env` files, customer or client names, data
private to one project (addresses, hostnames, internal URLs), and code, names, domain models
or examples taken from any project the skills were used in. A skill states a general method;
project specifics stay in that project's own `AGENTS.md`.

## License

MIT, see `LICENSE`.
