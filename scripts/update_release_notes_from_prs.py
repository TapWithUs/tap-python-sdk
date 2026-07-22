#!/usr/bin/env python3
"""Ensure docs/release-notes.md has a section for the release version.

If the section is already present, the file is left unchanged.
Otherwise a new section is inserted from PRs merged into master between the
previous v* tag and the current release commit.

Usage:
  python scripts/update_release_notes_from_prs.py [--version X.Y.Z] [--repo OWNER/REPO]

Environment:
  GITHUB_TOKEN / GH_TOKEN  — optional; raises API rate limits
  GITHUB_REPOSITORY        — default owner/repo when --repo is omitted
  GITHUB_SHA               — release commit (defaults to HEAD)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_NOTES = ROOT / "docs" / "release-notes.md"
SECTION_RE = re.compile(r"^## (\d+\.\d+\.\d+)(?:\s|\(|$)", re.MULTILINE)


def run_git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def package_version() -> str:
    about: dict[str, str] = {}
    version_file = ROOT / "tapsdk" / "__version__.py"
    exec(version_file.read_text(encoding="utf-8"), about)
    return about["__version__"]


def previous_tag(current_version: str) -> str | None:
    tags = list_version_tags()
    # Tags strictly older than current version
    older = []
    cur = tuple(int(p) for p in current_version.split("."))
    for tag in tags:
        ver = tuple(int(p) for p in tag[1:].split("."))
        if ver < cur:
            older.append(tag)
    if not older:
        return None
    return older[0]  # highest among older (list_version_tags is desc)


def list_version_tags() -> list[str]:
    raw = run_git("tag", "-l", "v*")
    tags = raw.splitlines() if raw else []
    # Prefer tags that look like vX.Y.Z
    version_tags = [t for t in tags if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
    if not version_tags:
        return []

    def key(tag: str) -> tuple[int, ...]:
        return tuple(int(p) for p in tag[1:].split("."))

    return sorted(version_tags, key=key, reverse=True)


def github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "tap-python-sdk-release-notes",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def api_get(url: str) -> object:
    req = urllib.request.Request(url, headers=github_headers())
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GitHub API error {exc.code} for {url}: {body}") from exc


def merged_prs(owner: str, repo: str, base_sha: str | None, head_sha: str) -> list[dict]:
    """Return merged PRs for commits reachable from head but not base."""
    if base_sha:
        try:
            commit_range = run_git("log", "--format=%H", f"{base_sha}..{head_sha}")
        except subprocess.CalledProcessError:
            commit_range = run_git("log", "--format=%H", head_sha)
    else:
        commit_range = run_git("log", "--format=%H", head_sha)

    shas = commit_range.splitlines() if commit_range else []
    if not shas:
        return []

    # Prefer the commits/{sha}/pulls association API (handles squash merges).
    by_number: dict[int, dict] = {}
    for sha in shas:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}/pulls"
        try:
            prs = api_get(url)
        except SystemExit:
            continue
        if not isinstance(prs, list):
            continue
        for pr in prs:
            if pr.get("merged_at") or pr.get("merged"):
                by_number[pr["number"]] = pr

    selected = list(by_number.values())
    selected.sort(key=lambda p: p.get("merged_at") or "")
    return selected


def has_section(text: str, version: str) -> bool:
    for match in SECTION_RE.finditer(text):
        if match.group(1) == version:
            return True
    return False


def format_section(version: str, prs: list[dict]) -> str:
    today = date.today().isoformat()
    lines = [
        f"## {version} ({today})",
        "______________________",
        "### Main features",
        "",
    ]
    if prs:
        for pr in prs:
            title = (pr.get("title") or "").strip().rstrip(".")
            number = pr["number"]
            lines.append(f"* {title} (#{number})")
    else:
        lines.append("* Release packaging and documentation updates.")
    lines.append("")
    return "\n".join(lines)


def insert_section(text: str, section: str) -> str:
    # Insert after the title block (first heading + optional intro paragraphs)
    lines = text.splitlines(keepends=True)
    if not lines:
        return f"# Release notes\n\n{section}"

    # Find end of preamble: after first H1 and following non-heading lines,
    # before the first ## version section.
    insert_at = 0
    seen_h1 = False
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            seen_h1 = True
            insert_at = i + 1
            continue
        if seen_h1 and line.startswith("## "):
            insert_at = i
            break
        if seen_h1:
            insert_at = i + 1

    # Ensure blank line before inserted section
    before = "".join(lines[:insert_at]).rstrip() + "\n\n"
    after = "".join(lines[insert_at:]).lstrip()
    return before + section + ("\n" if after and not section.endswith("\n") else "") + after


def parse_repo(repo: str) -> tuple[str, str]:
    owner, _, name = repo.partition("/")
    if not owner or not name:
        raise SystemExit(f"Invalid repo {repo!r}; expected OWNER/REPO")
    return owner, name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Release version (default: tapsdk.__version__)")
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", "TapWithUs/tap-python-sdk"),
        help="GitHub OWNER/REPO",
    )
    parser.add_argument(
        "--head-sha",
        default=os.environ.get("GITHUB_SHA") or None,
        help="Release commit SHA (default: GITHUB_SHA or HEAD)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the new section without writing the file",
    )
    args = parser.parse_args(argv)

    version = args.version or package_version()
    text = RELEASE_NOTES.read_text(encoding="utf-8")
    if has_section(text, version):
        print(f"Release notes already include ## {version}; leaving unchanged.")
        return 0

    head_sha = args.head_sha or run_git("rev-parse", "HEAD")
    prev = previous_tag(version)
    base_sha = None
    if prev:
        try:
            base_sha = run_git("rev-list", "-n", "1", prev)
        except subprocess.CalledProcessError:
            base_sha = None
        print(f"Collecting PRs since {prev} ({base_sha}) → {head_sha}")
    else:
        print(f"No previous v* tag found; collecting PRs reachable from {head_sha}")

    owner, repo = parse_repo(args.repo)
    prs = merged_prs(owner, repo, base_sha, head_sha)
    print(f"Found {len(prs)} merged PR(s) in range.")

    section = format_section(version, prs)
    if args.dry_run:
        print(section)
        return 0

    updated = insert_section(text, section)
    RELEASE_NOTES.write_text(updated, encoding="utf-8")
    print(f"Inserted ## {version} into {RELEASE_NOTES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
