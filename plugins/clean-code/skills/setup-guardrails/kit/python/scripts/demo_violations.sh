#!/usr/bin/env bash
# Runs every checker against examples/bad as if it were real src/ code,
# so you can see exactly which rule catches which agent habit.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cp -r "$ROOT/examples/bad/src" "$TMP/src"
cp -r "$ROOT/ast-grep" "$ROOT/sgconfig.yml" "$ROOT/pyproject.toml" "$TMP/"
sed -i.bak '/extend-exclude/d' "$TMP/pyproject.toml"

cd "$TMP"
echo "════════ ruff ════════"
ruff check --statistics src
echo
echo "════════ ast-grep (architecture rules) ════════"
ast-grep scan --report-style short src
echo
echo "════════ file length ════════"
python "$ROOT/scripts/check_file_length.py" src
exit 0
