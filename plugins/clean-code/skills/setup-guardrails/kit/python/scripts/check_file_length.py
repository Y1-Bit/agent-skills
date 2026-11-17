"""Fail when a source file grows past MAX_LINES. Big files = several ideas glued together.

Usage: python scripts/check_file_length.py [paths...] [--max N]
Works for any language: pass extensions via --ext (default: .py).
"""

import argparse
import sys
from pathlib import Path

DEFAULT_MAX_LINES = 250


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=["src"])
    parser.add_argument("--max", type=int, default=DEFAULT_MAX_LINES)
    parser.add_argument("--ext", nargs="*", default=[".py"])
    return parser.parse_args()


def _too_long(paths: list[str], *, extensions: list[str], limit: int) -> list[tuple[Path, int]]:
    files = (
        file
        for root in map(Path, paths)
        for file in sorted(root.rglob("*"))
        if file.suffix in extensions
    )
    counted = ((file, len(file.read_text(encoding="utf-8").splitlines())) for file in files)
    return [(file, count) for file, count in counted if count > limit]


def main() -> int:
    args = _parse_args()
    offenders = _too_long(args.paths, extensions=args.ext, limit=args.max)
    for file, count in offenders:
        print(f"{file}: {count} lines (max {args.max}) — split by responsibility")
    return 1 if offenders else 0


if __name__ == "__main__":
    sys.exit(main())
