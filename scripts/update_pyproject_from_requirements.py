#!/usr/bin/env python3
"""Sync `requirements.txt` into `pyproject.toml` [project].dependencies.

Usage:
  python scripts/update_pyproject_from_requirements.py --dry-run
  python scripts/update_pyproject_from_requirements.py --apply

The script:
- Reads `requirements.txt` and parses simple requirement lines (ignores comments and blank lines).
- Merges these requirements into the `dependencies` array under the `[project]` section of `pyproject.toml`.
- Writes a backup to `pyproject.toml.bak` before applying changes.

Note: This is intentionally conservative - it preserves other fields and formatting where possible using toml library.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
import sys

import tomli
import tomli_w


ROOT = Path(__file__).resolve().parents[1]
REQ_FILE = ROOT / "requirements.txt"
PYPROJECT = ROOT / "pyproject.toml"
BACKUP = ROOT / "pyproject.toml.bak"


def parse_requirements(req_path: Path) -> list[str]:
    reqs: list[str] = []
    if not req_path.exists():
        return reqs

    for raw in req_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        # Keep simple requirement specifiers (package, package>=1.2)
        # Ignore VCS/URL lines for now
        if line.startswith("-e ") or line.startswith("git+") or "@" in line:
            print(f"Skipping non-pip-file requirement: {line}")
            continue

        reqs.append(line)

    return reqs


def load_pyproject(path: Path) -> dict:
    return tomli.loads(path.read_text())


def write_pyproject(path: Path, data: dict):
    path.write_text(tomli_w.dumps(data))


def merge_dependencies(existing: list | None, new_reqs: list[str]) -> list[str]:
    existing = existing or []
    # Keep existing normalized strings and merge any new ones if missing.
    merged = list(existing)

    def normalize(s: str) -> str:
        return s.strip()

    normalized_set = {normalize(s) for s in merged}

    for r in new_reqs:
        nr = normalize(r)
        if nr not in normalized_set:
            merged.append(nr)
            normalized_set.add(nr)

    return merged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    parser.add_argument("--apply", action="store_true", help="Apply changes to pyproject.toml")

    args = parser.parse_args(argv)

    reqs = parse_requirements(REQ_FILE)
    if not reqs:
        print("No requirements found in requirements.txt")
        return 0

    if not PYPROJECT.exists():
        print(f"pyproject.toml not found at {PYPROJECT}")
        return 2

    py = load_pyproject(PYPROJECT)

    project = py.get("project") or {}
    existing_deps = project.get("dependencies")

    merged = merge_dependencies(existing_deps, reqs)

    if existing_deps == merged:
        print("No dependency changes required.")
        return 0

    print("Dependencies will be updated to:")
    for d in merged:
        print(f"  {d}")

    if args.dry_run:
        print("Dry-run complete. No changes written.")
        return 0

    if not args.apply:
        print("No --apply flag supplied. Use --apply to write changes, or --dry-run to preview.")
        return 1

    # Backup
    shutil.copy2(PYPROJECT, BACKUP)
    print(f"Backed up {PYPROJECT} to {BACKUP}")

    # Update structure and write
    py.setdefault("project", {})["dependencies"] = merged
    write_pyproject(PYPROJECT, py)

    print(f"pyproject.toml updated with {len(merged)} dependencies.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
