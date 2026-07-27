#!/usr/bin/env python3
"""Prepare a release commit: bump the version and cut the changelog.

This keeps the release pipeline read-only. Run it locally, review the diff,
then commit and tag the result (the script prints the exact commands).

What it does:
  1. Sets tapsdk/__version__.py to X.Y.Z.
  2. Renames the "## Unreleased" section in docs/release-notes.md to
     "## X.Y.Z (YYYY-MM-DD)" and inserts a fresh, empty "## Unreleased".

It refuses to run if the current Unreleased section has no bullet entries.

Usage:
  python scripts/prepare_release.py X.Y.Z [--date YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "tapsdk" / "__version__.py"
RELEASE_NOTES = ROOT / "docs" / "release-notes.md"

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
BULLET_RE = re.compile(r"^\s*[*-]\s+\S")
UNRELEASED_HEADING = "## Unreleased"

EMPTY_UNRELEASED = (
    "## Unreleased\n"
    "______________________\n"
    "### Main features\n"
    "\n"
    "### Bug fixes\n"
)


def fail(message: str) -> None:
    raise SystemExit(f"error: {message}")


def split_unreleased(text: str) -> tuple[str, list[str], str]:
    """Return (before, unreleased_block_lines, after).

    `unreleased_block_lines` covers the "## Unreleased" heading through the line
    before the next "## " heading.
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == UNRELEASED_HEADING or line.startswith(
            UNRELEASED_HEADING + " "
        ):
            start = i
            break
    if start is None:
        fail(f"no '{UNRELEASED_HEADING}' heading found in {RELEASE_NOTES}")

    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break

    return "".join(lines[:start]), lines[start:end], "".join(lines[end:])


def bump_version(version: str) -> None:
    VERSION_FILE.write_text(f'__version__ = "{version}"\n', encoding="utf-8")
    print(f"Set {VERSION_FILE.relative_to(ROOT)} to {version}")


def cut_changelog(version: str, release_date: str) -> None:
    text = RELEASE_NOTES.read_text(encoding="utf-8")

    if re.search(rf"^## {re.escape(version)}(?:\s|\(|$)", text, re.MULTILINE):
        fail(f"docs/release-notes.md already has a '## {version}' section")

    before, block, after = split_unreleased(text)

    if not any(BULLET_RE.match(line) for line in block[1:]):
        fail(
            "the '## Unreleased' section has no entries; nothing to release. "
            "Add bullets before preparing a release."
        )

    # Replace the heading line with the versioned heading; keep the entries.
    versioned = [f"## {version} ({release_date})\n"] + block[1:]
    released_block = "".join(versioned).rstrip("\n") + "\n"

    new_text = (
        before
        + EMPTY_UNRELEASED
        + "\n"
        + released_block
        + ("\n" + after.lstrip("\n") if after.strip() else "")
    )
    RELEASE_NOTES.write_text(new_text, encoding="utf-8")
    print(
        f"Renamed Unreleased -> {version} ({release_date}) in "
        f"{RELEASE_NOTES.relative_to(ROOT)} and opened a fresh Unreleased section"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Release version, e.g. 0.8.0")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Release date (YYYY-MM-DD); defaults to today",
    )
    args = parser.parse_args(argv)

    version = args.version.lstrip("v")
    if not VERSION_RE.match(version):
        fail(f"invalid version {args.version!r}; expected X.Y.Z")

    bump_version(version)
    cut_changelog(version, args.date)

    tag = f"v{version}"
    print()
    print("Review the changes, then commit and tag:")
    print("  git add tapsdk/__version__.py docs/release-notes.md")
    print(f'  git commit -m "Release {version}"')
    print(f'  git tag -a {tag} -m "Release {version}"')
    print("  git push origin HEAD")
    print(f"  git push origin {tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
