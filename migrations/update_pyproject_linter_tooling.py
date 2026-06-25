#!/usr/bin/env python3
"""Update dependency-groups.dev linter/tooling dependencies in pyproject.toml."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # ty: ignore[unresolved-import]


REQUIRED_DEV_DEPENDENCIES = [
    "pre-commit>=4.3.0",
    "pytest>=8.4.1",
    "pytest-cov>=6.2.1",
    "ruff>=0.12.10",
    "ty>=0.0.23",
]


def _dependency_name(requirement: str) -> str:
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
    if not match:
        return requirement.strip().lower()
    return match.group(1).lower().replace("_", "-")


def _merge_dependencies(existing: list[str]) -> list[str]:
    required_names = {_dependency_name(dep) for dep in REQUIRED_DEV_DEPENDENCIES}
    merged = list(REQUIRED_DEV_DEPENDENCIES)
    for dep in existing:
        if _dependency_name(dep) not in required_names:
            merged.append(dep)
    return merged


def _render_dev_block(dependencies: list[str]) -> list[str]:
    block = ["dev = [\n"]
    block.extend([f'    "{dependency}",\n' for dependency in dependencies])
    block.append("]\n")
    return block


def _find_section_bounds(lines: list[str], section: str) -> tuple[int, int] | None:
    section_header = f"[{section}]"
    for index, line in enumerate(lines):
        if line.strip() == section_header:
            end_index = len(lines)
            for next_index in range(index + 1, len(lines)):
                if lines[next_index].lstrip().startswith("["):
                    end_index = next_index
                    break
            return index, end_index
    return None


def _find_dev_block(lines: list[str], start: int, end: int) -> tuple[int, int] | None:
    for index in range(start + 1, end):
        stripped = lines[index].strip()
        if stripped.startswith("dev") and "[" in stripped:
            depth = lines[index][lines[index].index("[") :].count("[") - lines[index][lines[index].index("[") :].count(
                "]"
            )
            block_end = index
            while depth > 0 and block_end + 1 < end:
                block_end += 1
                depth += lines[block_end].count("[") - lines[block_end].count("]")
            return index, block_end
    return None


def update_pyproject(path: Path) -> bool:
    original_text = path.read_text()
    parsed = tomllib.loads(original_text)
    dependency_groups = parsed.get("dependency-groups", {})
    existing_dev = dependency_groups.get("dev", [])
    if not isinstance(existing_dev, list):
        raise ValueError("[dependency-groups].dev must be a list")

    merged_dev = _merge_dependencies([str(item) for item in existing_dev])

    lines = path.read_text().splitlines(keepends=True)
    section_bounds = _find_section_bounds(lines, "dependency-groups")
    replacement = _render_dev_block(merged_dev)

    if section_bounds is None:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] = lines[-1] + "\n"
        if lines and lines[-1].strip():
            lines.append("\n")
        lines.extend(["[dependency-groups]\n", *replacement])
    else:
        section_start, section_end = section_bounds
        dev_bounds = _find_dev_block(lines, section_start, section_end)
        if dev_bounds is None:
            insertion_index = section_end
            if insertion_index > section_start + 1 and lines[insertion_index - 1].strip():
                replacement = ["\n", *replacement]
            lines[insertion_index:insertion_index] = replacement
        else:
            dev_start, dev_end = dev_bounds
            lines[dev_start : dev_end + 1] = replacement

    updated_text = "".join(lines)
    if updated_text == original_text:
        return False
    path.write_text(updated_text)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pyproject-file", default="pyproject.toml", help="Path to pyproject.toml")
    parser.add_argument("--check", action="store_true", help="Exit with code 1 if an update is needed")
    args = parser.parse_args()

    pyproject_file = Path(args.pyproject_file)
    if not pyproject_file.exists():
        print(f"Error: file does not exist: {pyproject_file}", file=sys.stderr)
        return 2

    original_text = pyproject_file.read_text()
    changed = update_pyproject(pyproject_file)

    if args.check:
        if changed:
            pyproject_file.write_text(original_text)
            print("pyproject.toml needs linter/tooling dependency migration")
            return 1
        print("pyproject.toml linter/tooling dependencies are up to date")
        return 0

    if changed:
        print(f"Updated {pyproject_file}")
    else:
        print(f"No changes needed for {pyproject_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
