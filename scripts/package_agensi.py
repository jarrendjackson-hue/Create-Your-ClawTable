#!/usr/bin/env python3
"""Build the text-only Agensi package without collecting user-generated data."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "marketplace" / "create-your-clawtable"
FILES = (
    "SKILL.md",
    "LICENSE",
    "agents/openai.yaml",
    "references/cli-workflow.md",
    "references/seat-synthesis.md",
    "references/roundtable.md",
)


def package(destination: Path) -> None:
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", skill_text, re.DOTALL)
    if not match or not all(
        re.search(rf"^{key}:\s*\S", match.group(1), re.MULTILINE)
        for key in ("name", "description")
    ):
        raise ValueError("SKILL.md must contain name and description frontmatter")

    contents = []
    for relative in FILES:
        source = SKILL / relative
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Missing or unsafe package file: {relative}")
        data = source.read_bytes()
        data.decode("utf-8")
        contents.append((relative, data))

    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, data in contents:
            info = zipfile.ZipInfo(relative, date_time=(2026, 11, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)

    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None or archive.namelist() != list(FILES):
            raise ValueError("Archive verification failed")
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    print(f"Created: {destination}")
    print(f"Files: {len(FILES)}; bytes: {destination.stat().st_size}")
    print(f"SHA256: {digest}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "dist" / "Create-Your-ClawTable.zip"
    )
    args = parser.parse_args()
    package(args.output)


if __name__ == "__main__":
    main()
