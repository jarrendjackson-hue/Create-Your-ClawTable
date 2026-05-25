"""Shared helpers: slugging, paths, logging."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "seat"


def source_pack_dir(slug: str) -> Path:
    d = ROOT / "source-packs" / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def seats_dir() -> Path:
    d = ROOT / "seats"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_prompts_dir() -> Path:
    d = ROOT / "build-prompts"
    d.mkdir(parents=True, exist_ok=True)
    return d


def dist_dir() -> Path:
    d = ROOT / "dist"
    d.mkdir(parents=True, exist_ok=True)
    return d


def prompts_dir() -> Path:
    return ROOT / "prompts"


def log(msg: str) -> None:
    print(f"[clawtable] {msg}", file=sys.stderr)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require(modname: str, install_hint: str) -> object:
    """Lazy-import with a friendly error if the dep isn't installed."""
    try:
        return __import__(modname)
    except ImportError:
        log(f"missing dependency: {modname}")
        log(f"install with: {install_hint}")
        sys.exit(1)
