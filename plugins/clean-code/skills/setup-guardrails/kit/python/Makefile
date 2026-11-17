.PHONY: check fix lint types arch rules test demo-violations mutate

# One command for humans, agents, pre-commit and CI. Agents: run `make check` before finishing.
check: lint types arch rules test

fix:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff format --check .
	uv run ruff check .
	uv run python scripts/check_file_length.py src --max 250

types:
	uv run mypy

arch:
	uv run lint-imports

rules:
	uv run ast-grep test --skip-snapshot-tests
	uv run ast-grep scan src

test:
	uv run pytest -q

demo-violations:
	PATH="$(CURDIR)/.venv/bin:$$PATH" ./scripts/demo_violations.sh

# Slow: run in CI on PRs touching domain/, or nightly. Not part of `check`.
mutate:
	rm -rf mutants
	uv run mutmut run
	uv run python scripts/mutation_score.py --min 0.85
