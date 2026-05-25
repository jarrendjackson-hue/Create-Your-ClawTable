"""Interactive onboarding wizard — `python clawtable.py init`.

Walks the user through:
  1. Who do you want at your table?
  2. For each: where does their material live (YouTube / book / podcast / articles)?
  3. Harvest each source.
  4. Generate build-prompts for each.
  5. Print "connect your brain" instructions.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from . import articles, books, podcasts, seat, youtube
from .util import ROOT, log, slugify


BANNER = r"""
   ____ _                _____     _     _
  / ___| | __ ___      _|_   _|_ _| |__ | | ___
 | |   | |/ _` \ \ /\ / / | |/ _` | '_ \| |/ _ \
 | |___| | (_| |\ V  V /  | | (_| | |_) | |  __/
  \____|_|\__,_| \_/\_/   |_|\__,_|_.__/|_|\___|

  Build your own AI strategy round table.
"""

SOURCE_CHOICES = {
    "1": "youtube",
    "2": "book",
    "3": "podcast",
    "4": "articles",
    "5": "skip",
}


def run() -> None:
    print(BANNER)
    print("This wizard will help you stand up your first ClawTable.\n")

    names = _ask_names()
    if not names:
        print("No names entered. Run `python clawtable.py init` again when ready.")
        return

    plan: list[tuple[str, str, str, str]] = []  # (name, slug, source_type, source_arg)
    for name in names:
        slug = slugify(name)
        source_type, source_arg = _ask_source(name)
        if source_type == "skip":
            log(f"skipping {name}")
            continue
        plan.append((name, slug, source_type, source_arg))

    if not plan:
        print("\nNothing to harvest. Exiting.")
        return

    print("\n" + "=" * 60)
    print("Plan:")
    for name, slug, source_type, source_arg in plan:
        print(f"  • {name:<30} {source_type:<10} {source_arg}")
    print("=" * 60)
    if not _yes("\nProceed? [Y/n] ", default=True):
        print("Aborted.")
        return

    print()
    harvested: list[tuple[str, str]] = []
    for name, slug, source_type, source_arg in plan:
        print(f"\n--- harvesting: {name} ({source_type}) ---")
        try:
            if source_type == "youtube":
                youtube.harvest(source_arg, slug, max_videos=10, transcribe=True)
            elif source_type == "book":
                books.harvest(source_arg, slug)
            elif source_type == "podcast":
                podcasts.harvest(source_arg, slug, max_episodes=10)
            elif source_type == "articles":
                articles.harvest(source_arg, slug)
            harvested.append((name, slug))
        except SystemExit:
            log(f"harvest failed for {name} — continuing with the rest")
        except Exception as e:
            log(f"harvest error for {name}: {e}")

    if not harvested:
        print("\nNothing was harvested successfully. Exiting.")
        return

    print(f"\n--- generating build prompts for {len(harvested)} seat(s) ---\n")
    build_prompt_paths: list[Path] = []
    for name, slug in harvested:
        try:
            path = seat.make_build_prompt(slug, name)
            build_prompt_paths.append(path)
        except SystemExit:
            log(f"prompt failed for {name}")

    _print_connect_brain(build_prompt_paths)


def _ask_names() -> list[str]:
    print("Step 1 — who do you want at your table?\n")
    print("Type one name per line. Empty line to finish.")
    print("Examples: Alex Hormozi, Charlie Munger, Paul Graham, your favorite author.\n")
    names: list[str] = []
    while True:
        try:
            line = input(f"  name #{len(names) + 1} > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            if names:
                break
            print("  (need at least one name)")
            continue
        names.append(line)
    return names


def _ask_source(name: str) -> tuple[str, str]:
    print(f"\nStep 2 — where does {name}'s material live?")
    print("  [1] YouTube channel (name, @handle, or URL)")
    print("  [2] Book (PDF / EPUB / TXT / MD on disk)")
    print("  [3] Podcast RSS feed")
    print("  [4] Article URL list (text file, one URL per line)")
    print("  [5] Skip — I'll add this seat later")

    while True:
        choice = input("  pick [1-5] > ").strip()
        if choice in SOURCE_CHOICES:
            kind = SOURCE_CHOICES[choice]
            break
        print("  please enter 1, 2, 3, 4, or 5")

    if kind == "skip":
        return "skip", ""

    prompts = {
        "youtube": "  YouTube channel name / @handle / URL > ",
        "book": "  path to book file (drop PDFs in ./books/ first) > ",
        "podcast": "  RSS feed URL > ",
        "articles": "  path to a .txt file of URLs > ",
    }
    arg = input(prompts[kind]).strip()
    if not arg:
        return "skip", ""

    # quick existence check for file-based sources
    if kind in ("book", "articles"):
        path = Path(arg).expanduser()
        if not path.exists():
            # try relative to the repo root
            alt = ROOT / arg
            if alt.exists():
                arg = str(alt)
            else:
                log(f"file not found: {arg} (will fail on harvest)")
                if not _yes("  continue anyway? [y/N] ", default=False):
                    return "skip", ""

    return kind, arg


def _yes(prompt: str, default: bool = False) -> bool:
    try:
        ans = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return default
    if not ans:
        return default
    return ans.startswith("y")


def _print_connect_brain(build_prompt_paths: list[Path]) -> None:
    print("\n" + "=" * 60)
    print(" STEP 3 — connect your brain")
    print("=" * 60)
    if not build_prompt_paths:
        print("\nNo build prompts were generated. Check the errors above.")
        return

    print(f"\nI generated {len(build_prompt_paths)} synthesis prompt(s):\n")
    for p in build_prompt_paths:
        print(f"  • {p.relative_to(ROOT)}")

    print("""
Each prompt contains the raw source material + instructions for Claude
(or any LLM) to compress it into a clean advisor seat at seats/<slug>.md.

Two ways to finish:

  A) Claude Code  (recommended — handles long inputs natively)
""")
    claude_bin = shutil.which("claude")
    if claude_bin:
        print(f"     $ claude --add-dir {ROOT}")
        print("       then say: 'read each file in build-prompts/ and follow it'")
    else:
        print("     install Claude Code:  https://claude.com/download")
        print(f"     then run:           claude --add-dir {ROOT}")
        print("     say:                'read each file in build-prompts/ and follow it'")

    print("""
  B) Any chat LLM
     Open each build-prompts/<slug>.md, paste the contents into Claude /
     ChatGPT, and ask it to write the result to seats/<slug>.md.

Once you have at least one file in seats/, run:

  $ python clawtable.py build

That bundles your seats + the orchestrator into dist/clawtable-bundle.md.
Paste that into a fresh LLM chat and tell it your idea.
""")

    # If Claude Code is installed, offer to launch it
    if claude_bin and sys.stdin.isatty():
        if _yes(f"Launch Claude Code now in {ROOT}? [y/N] ", default=False):
            try:
                subprocess.run([claude_bin, "--add-dir", str(ROOT)], check=False)
            except Exception as e:
                log(f"failed to launch claude: {e}")
