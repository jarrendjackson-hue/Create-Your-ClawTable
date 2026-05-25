"""Seat builder + bundler.

The flow is:
  1. After harvesting source material into source-packs/<slug>/,
     call `make_build_prompt(slug, name)` to produce a paste-into-Claude
     prompt at build-prompts/<slug>.md. That prompt tells Claude to
     synthesize the raw material into a seat file at seats/<slug>.md.

  2. Once the user has at least one seat in seats/, call `bundle()` to
     stitch every seat file + the orchestrator into a single
     paste-into-LLM file at dist/clawtable-bundle.md.
"""
from __future__ import annotations

from pathlib import Path

from .util import (
    build_prompts_dir,
    dist_dir,
    log,
    prompts_dir,
    seats_dir,
    source_pack_dir,
    write_text,
)

MAX_INLINE_CHARS = 25_000


def make_build_prompt(slug: str, name: str) -> Path:
    """Render prompts/build-seat.md with this seat's source pack appended."""
    pack = source_pack_dir(slug)
    template = (prompts_dir() / "build-seat.md").read_text(encoding="utf-8")

    files = sorted([p for p in pack.rglob("*.txt") if p.is_file()])
    if not files:
        log(f"no source files found in {pack}")
        log("run a harvester first (add-youtube, add-book, add-podcast, add-articles)")
        raise SystemExit(1)

    parts = [f"### Source files ({len(files)} total)"]
    total = 0
    for f in files:
        rel = f.relative_to(pack)
        body = f.read_text(encoding="utf-8", errors="ignore")
        if total + len(body) > MAX_INLINE_CHARS:
            parts.append(
                f"\n#### `{rel}`\n\n_[file too large to inline — open it from `source-packs/{slug}/{rel}`]_\n"
            )
            continue
        total += len(body)
        parts.append(f"\n#### `{rel}`\n\n```\n{body.strip()}\n```\n")

    appendix = "\n".join(parts)
    rendered = (
        template
        .replace("{{NAME}}", name)
        .replace("{{SLUG}}", slug)
        .replace("{{SOURCE_APPENDIX}}", appendix)
    )

    out = build_prompts_dir() / f"{slug}.md"
    write_text(out, rendered)
    log(f"wrote build prompt: {out.relative_to(out.parent.parent)}")
    log("next: open that file in Claude Code (or paste into Claude) — Claude will write seats/" + slug + ".md")
    return out


def bundle(lineup: list[str] | None = None) -> Path:
    """Stitch seats + orchestrator into one paste-ready bundle."""
    seats = sorted(seats_dir().glob("*.md"))
    if lineup:
        wanted = set(lineup)
        seats = [s for s in seats if s.stem in wanted]
    if not seats:
        log("no seats found in seats/. add at least one before bundling.")
        raise SystemExit(1)

    orchestrator = (prompts_dir() / "orchestrator.md").read_text(encoding="utf-8")

    parts = [
        "# ClawTable Session Bundle",
        "",
        "Paste this entire file into Claude, ChatGPT, or any LLM with a long context window. "
        "The orchestrator prompt comes first, then each loaded seat. Tell it your idea after.",
        "",
        "---",
        "",
        orchestrator,
        "",
        "---",
        "",
        f"## Loaded seats ({len(seats)})",
        "",
    ]
    for s in seats:
        parts.append("---\n")
        parts.append(s.read_text(encoding="utf-8"))
        parts.append("")

    parts.append("\n---\n")
    parts.append("## Your turn")
    parts.append("")
    parts.append("Tell the orchestrator your idea or goal. It will run the rounds.")

    out = dist_dir() / "clawtable-bundle.md"
    write_text(out, "\n".join(parts))
    log(f"bundled {len(seats)} seats → {out}")
    return out
