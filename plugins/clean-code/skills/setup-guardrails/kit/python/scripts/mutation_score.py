"""Fail if the mutation score (killed / tested mutants) is below the threshold.

Run after `mutmut run`. Prints surviving mutants so an agent can write the missing
assertions: `mutmut show <name>` displays the diff that the tests failed to notice.
"""

import argparse
import shutil
import subprocess
import sys
from collections import Counter

DEFAULT_MIN_SCORE = 0.85
COUNTED = {"killed", "survived", "timeout", "suspicious"}


def _results() -> list[tuple[str, str]]:
    mutmut = shutil.which("mutmut")
    if mutmut is None:
        sys.exit("mutmut is not installed")
    output = subprocess.run(
        [mutmut, "results", "--all", "true"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    rows = (line.strip().rsplit(": ", 1) for line in output.splitlines() if ": " in line)
    return [(name, status) for name, status in rows]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=float, default=DEFAULT_MIN_SCORE)
    args = parser.parse_args()

    results = _results()
    statuses = Counter(status for _, status in results)
    tested = sum(statuses[s] for s in COUNTED)
    score = statuses["killed"] / tested if tested else 0.0

    for name, status in results:
        if status == "survived":
            print(f"survived: {name}")
    print(f"mutation score: {score:.0%} ({statuses['killed']}/{tested}), minimum {args.min:.0%}")
    return 0 if score >= args.min else 1


if __name__ == "__main__":
    sys.exit(main())
