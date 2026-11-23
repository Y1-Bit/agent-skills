"""Self-check for check_docs.py: run with `python3 -m unittest test_check_docs.py` from this folder."""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import check_docs  # noqa: E402

FILES = {
    "package.json": json.dumps({"scripts": {"test": "vitest", "build": "vite build"}, "engines": {"node": ">=20"}}),
    "Makefile": "check lint: deps\n\tnpm test\ndeps:\n",
    "docs/examples.md": "<!-- check-docs: ignore-file path -->\n`src/example/only.ts` and `oldName()`\n",
    "AGENTS.md": "# Agents\n\nDo not edit `gen/` by hand.\n`src/missing/a.ts`\n",
    "docs/tricky.md": "\n".join([
        "Title",                                        # 1 setext heading
        "=====",
        "[ok](#title) and [also](tricky.md#title)",     # 3 clean
        "[^1]: a footnote, not a link",                 # 4 clean
        "Shown as text: `<!-- check-docs: ignore-file -->`",  # 5 must not silence the doc
        "````md",
        "```",
        "`src/in/fence.ts` is not path-checked",        # 8 still inside the 4-backtick fence
        "```",
        "````",
        "```sh",
        "# make sure deps are there",                   # 12 shell comment
        "make DEBUG=1 lint",                            # 13 multi-target rule
        "make -C sub deploy",                           # 14 error: deploy
        "```",
        "<!-- TOOL:BEGIN -->",
        "`src/managed/x.ts`",                           # 17 managed block, skipped
        "<!-- TOOL:END -->",
        "`src/after/y.ts`",                             # 19 error again
    ]),
    "docs/adr/0001-old.md": "# ADR\n[gone](gone.md)\n",
    "src/app.ts": "export function loadConfig() { return process.env.API_BASE_URL }\n",
    "docs/guide.md": "# Guide\n\n## Set up the app\n\nText.\n",
    "QA-REPORT.md": "# QA\n\nSee [gone](missing.md). TODO in a record is fine. `src/old.ts`\n",
    "API.md": "<!-- This file is auto-generated. Do not edit. -->\n[broken](nowhere.md)\n",
    "README.md": "\n".join([
        "# Project",
        "[ok](docs/guide.md#set-up-the-app)",          # 2 clean
        "[bad link](docs/missing.md)",                  # 3 link
        "[bad anchor](docs/guide.md#no-such)",          # 4 anchor
        "`src/app.ts` and `src/gone.ts`",               # 5 path (gone only)
        "Run `npm run build` or `npm run deploy`.",    # 6 script (deploy only)
        "Then `make check` and `make release`.",       # 7 script (release only)
        "Set `API_BASE_URL` and `SECRET_TOKEN`.",      # 8 env (SECRET_TOKEN only)
        "Call `loadConfig()` or `removedHelper()`.",   # 9 symbol (removedHelper only)
        "Needs Node 18.",                               # 10 version
        "Search is coming soon.",                       # 11 stale
        "Never create `src/pages/x.ts`. <!-- check-docs: ignore -->",  # ignored
        "See [QA](QA-REPORT.md).",                      # 13 record-cited
        "```sh",
        "npm run lint",                                 # 15 script in fence
        "cat src/not-checked-in-fence.ts",
        "```",
    ]),
}


class CheckDocsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        for rel, text in FILES.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text)
        out = io.StringIO()
        with redirect_stdout(out):
            self.code = check_docs.main(["check_docs.py", str(root)])
        self.out = out.getvalue()

    def tearDown(self):
        self.tmp.cleanup()

    def hits(self, doc, line):
        return [l for l in self.out.splitlines() if l.startswith(f"{doc}:{line}:")]

    def test_classes(self):
        self.assertIn("# record (2): QA-REPORT.md, docs/adr/0001-old.md", self.out)
        self.assertIn("# generated (1): API.md", self.out)
        self.assertEqual(self.hits("API.md", 2), [])

    def test_each_kind_fires_once_on_the_bad_case(self):
        expected = {
            3: "error link", 4: "error anchor", 5: "error path: `src/gone.ts`",
            6: "error script: package script `deploy`", 7: "error script: make target `release`",
            8: "warn env: `SECRET_TOKEN`", 9: "warn symbol: `removedHelper`",
            10: "warn version: Node 18", 11: "info stale", 13: "info record-cited",
            15: "error script: package script `lint`",
        }
        for line, text in expected.items():
            hits = self.hits("README.md", line)
            self.assertEqual(len(hits), 1, (line, hits))
            self.assertIn(text, hits[0])
        self.assertEqual(self.hits("README.md", 2), [])
        self.assertEqual(self.hits("README.md", 12), [])
        self.assertEqual(self.hits("README.md", 16), [])

    def test_ignore_file_drops_only_named_kinds(self):
        hits = self.hits("docs/examples.md", 2)
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("warn symbol", hits[0])

    def test_record_gets_link_checks_only(self):
        hits = self.hits("QA-REPORT.md", 3)
        self.assertEqual(len(hits), 1, hits)
        self.assertIn("warn link", hits[0])  # records never fail the gate
        self.assertIn("warn link", self.hits("docs/adr/0001-old.md", 2)[0])

    def test_markdown_edge_cases(self):
        lines_with_hits = {int(l.split(":")[1]) for l in self.out.splitlines() if l.startswith("docs/tricky.md:")}
        self.assertEqual(lines_with_hits, {14, 19}, self.out)
        self.assertIn("make target `deploy`", self.hits("docs/tricky.md", 14)[0])

    def test_rule_text_does_not_make_a_doc_generated(self):
        self.assertIn("error path: `src/missing/a.ts`", self.hits("AGENTS.md", 4)[0])

    def test_missing_root_is_not_a_green_gate(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(check_docs.main(["x", "/no/such/dir"]), 2)

    def test_exit_code_fails_on_errors(self):
        self.assertEqual(self.code, 1)


if __name__ == "__main__":
    unittest.main()
