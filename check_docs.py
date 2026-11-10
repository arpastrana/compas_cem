"""
Fail when a personal name appears in project prose.

Decisions are attributed to their date, never to a person. Package
authorship metadata is a legitimate use of a name, so the pre-commit
config excludes those files.
"""

import sys
from pathlib import Path

BANNED_NAMES = ("Rafael", "Pastrana", "arpj")


def banned_name_hits(paths: list[Path]) -> list[str]:
    """
    Report every line of every path containing a banned personal name.

    This file is skipped: it has to spell the names it bans.
    """
    hits = []
    for path in paths:
        if path.resolve() == Path(__file__).resolve():
            continue
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            for name in BANNED_NAMES:
                if name in line:
                    hits.append(f"{path}:{number}: names a person ({name})")

    return hits


def main() -> int:
    """
    Run the check over the paths given on the command line.
    """
    paths = [Path(arg) for arg in sys.argv[1:] if Path(arg).exists()]
    hits = banned_name_hits(paths)
    for hit in hits:
        print(hit, file=sys.stderr)

    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
