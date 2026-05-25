#!/usr/bin/env python3
"""
clawtable — build your own AI strategy round table.

First time? Run the interactive wizard:
  python clawtable.py init

Manual usage:
  python clawtable.py add-youtube  "Alex Hormozi"          [--max 20]
  python clawtable.py add-book     books/100m-offers.pdf   --name "Hormozi"
  python clawtable.py add-podcast  https://feeds.example/  --name "MFM"  [--max 10]
  python clawtable.py add-articles urls.txt                --name "Paul Graham"
  python clawtable.py prompt       --name "Alex Hormozi"
  python clawtable.py build        [--seats hormozi,saraev,...]

Workflow:
  1. add-* commands harvest raw source material into source-packs/<slug>/
  2. `prompt` generates a paste-into-Claude prompt at build-prompts/<slug>.md.
     Open it in Claude Code and Claude will write the seat file to seats/<slug>.md.
  3. `build` bundles your seats + the orchestrator into dist/clawtable-bundle.md.
     Paste that into any LLM and tell it your idea.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import articles, books, podcasts, preflight, seat, wizard, youtube  # noqa: E402
from lib.util import log, slugify  # noqa: E402


def cmd_init(args: argparse.Namespace) -> None:
    wizard.run()


def cmd_doctor(args: argparse.Namespace) -> int:
    return preflight.doctor()


def cmd_add_youtube(args: argparse.Namespace) -> None:
    name = args.name_or_query
    slug = slugify(args.slug or name)
    log(f"slug: {slug}")
    youtube.harvest(name, slug, max_videos=args.max, transcribe=not args.no_transcribe)
    log(f"done. next: python clawtable.py prompt --name \"{name}\"")


def cmd_add_book(args: argparse.Namespace) -> None:
    name = args.name
    slug = slugify(args.slug or name)
    log(f"slug: {slug}")
    books.harvest(args.path, slug)
    log(f"done. next: python clawtable.py prompt --name \"{name}\"")


def cmd_add_podcast(args: argparse.Namespace) -> None:
    name = args.name
    slug = slugify(args.slug or name)
    log(f"slug: {slug}")
    podcasts.harvest(args.feed, slug, max_episodes=args.max)
    log(f"done. next: python clawtable.py prompt --name \"{name}\"")


def cmd_add_articles(args: argparse.Namespace) -> None:
    name = args.name
    slug = slugify(args.slug or name)
    log(f"slug: {slug}")
    articles.harvest(args.urls_file, slug)
    log(f"done. next: python clawtable.py prompt --name \"{name}\"")


def cmd_prompt(args: argparse.Namespace) -> None:
    name = args.name
    slug = slugify(args.slug or name)
    seat.make_build_prompt(slug, name)


def cmd_build(args: argparse.Namespace) -> None:
    lineup = None
    if args.seats:
        lineup = [s.strip() for s in args.seats.split(",") if s.strip()]
    seat.bundle(lineup)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="clawtable", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=False)

    it = sub.add_parser("init", help="Interactive wizard — set up your first table from scratch")
    it.set_defaults(func=cmd_init)

    dr = sub.add_parser("doctor", help="Detect your OS + check what's installed; print OS-specific install commands")
    dr.set_defaults(func=cmd_doctor)

    yt = sub.add_parser("add-youtube", help="Harvest from a YouTube channel or search")
    yt.add_argument("name_or_query", help="Channel name, @handle, URL, or free-text search")
    yt.add_argument("--max", type=int, default=10, help="Max videos to pull (default 10)")
    yt.add_argument("--no-transcribe", action="store_true", help="Skip whisper fallback (captions only)")
    yt.add_argument("--slug", help="Override slug (default: slugified name)")
    yt.set_defaults(func=cmd_add_youtube)

    bk = sub.add_parser("add-book", help="Extract text from a PDF/EPUB/TXT/MD file")
    bk.add_argument("path", help="Path to the book file")
    bk.add_argument("--name", required=True, help="Subject name (e.g. \"Alex Hormozi\")")
    bk.add_argument("--slug", help="Override slug")
    bk.set_defaults(func=cmd_add_book)

    pc = sub.add_parser("add-podcast", help="Pull episodes from an RSS feed and transcribe")
    pc.add_argument("feed", help="Podcast RSS feed URL")
    pc.add_argument("--name", required=True, help="Subject name")
    pc.add_argument("--max", type=int, default=10, help="Max episodes (default 10)")
    pc.add_argument("--slug", help="Override slug")
    pc.set_defaults(func=cmd_add_podcast)

    ar = sub.add_parser("add-articles", help="Scrape a list of URLs from a text file")
    ar.add_argument("urls_file", help="Text file with one URL per line")
    ar.add_argument("--name", required=True, help="Subject name")
    ar.add_argument("--slug", help="Override slug")
    ar.set_defaults(func=cmd_add_articles)

    pr = sub.add_parser("prompt", help="Generate a build-seat prompt for Claude")
    pr.add_argument("--name", required=True, help="Subject name")
    pr.add_argument("--slug", help="Override slug")
    pr.set_defaults(func=cmd_prompt)

    bd = sub.add_parser("build", help="Bundle all seats + orchestrator into dist/clawtable-bundle.md")
    bd.add_argument("--seats", help="Comma-separated seat slugs to include (default: all)")
    bd.set_defaults(func=cmd_build)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        # No subcommand — run the wizard
        wizard.run()
        return 0
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
