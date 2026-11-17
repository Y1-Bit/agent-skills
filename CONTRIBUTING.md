# Improving a skill

Skills improve through use. A session that finds one of these skills wrong, incomplete, or
needing the same correction twice proposes a change; the maintainer decides.

1. Work in a separate git worktree outside the main clone (other sessions may share that clone),
   on a branch `skill/<skill>-<topic>` from `origin/main`.
2. Change `SKILL.md` (and supporting files) with the smallest edit that fixes what happened.
3. Add a line at the top of the skill's `CHANGELOG.md`: date, what changed, and what went
   wrong in use that prompted it, as a general lesson (see "Never in this repository" in the
   README).
4. Check: `claude plugin validate .` passes; for a behavior change, try it with
   `claude --plugin-dir plugins/<plugin>` on a real task; a kit change passes the kit's own check and
   demo-violations script.
5. Push the branch and open a pull request: what went wrong, the change, how it was checked.
6. The maintainer reads the diff and says yes; only then merge to `main` (squash or
   fast-forward) and delete the branch and worktree. A change after the yes needs a new yes.

Versions: `main` is the release. No tags or semver; the installed version is the commit SHA,
and each skill's `CHANGELOG.md` is its history.
