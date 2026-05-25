"""Preflight checks + OS-aware install instructions.

Detects:
- What OS the user is on (macOS / Linux / Windows)
- Which CLI tools are on PATH (yt-dlp, ffmpeg, claude)
- Which Python deps are importable (faster-whisper, pypdf, feedparser, ...)

Prints a clean status table and exact install commands for missing pieces,
tailored to the user's OS. Can auto-run `pip install -r requirements.txt`
for them if they say yes.
"""
from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass

from .util import ROOT, log


@dataclass
class CheckResult:
    name: str
    present: bool
    why_needed: str
    install: dict[str, str]  # os_name → command


def detect_os() -> str:
    """Return one of: 'mac', 'linux', 'windows', 'unknown'."""
    sys_name = platform.system().lower()
    if sys_name == "darwin":
        return "mac"
    if sys_name == "linux":
        return "linux"
    if sys_name in ("windows", "win32"):
        return "windows"
    return "unknown"


def _has_cli(name: str) -> bool:
    return shutil.which(name) is not None


def _has_python_pkg(import_name: str) -> bool:
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def run_checks() -> list[CheckResult]:
    """Check every required + optional dep. Return ordered results."""
    return [
        CheckResult(
            name="yt-dlp (CLI)",
            present=_has_cli("yt-dlp"),
            why_needed="YouTube source — captions + audio download",
            install={
                "mac": "pip install yt-dlp   # or: brew install yt-dlp",
                "linux": "pip install yt-dlp   # or: sudo apt install yt-dlp",
                "windows": "pip install yt-dlp",
            },
        ),
        CheckResult(
            name="ffmpeg",
            present=_has_cli("ffmpeg"),
            why_needed="Whisper fallback when YouTube videos have no captions, AND podcast transcription",
            install={
                "mac": "brew install ffmpeg",
                "linux": "sudo apt install ffmpeg",
                "windows": "winget install ffmpeg   # or download from https://ffmpeg.org/download.html",
            },
        ),
        CheckResult(
            name="faster-whisper (Python)",
            present=_has_python_pkg("faster_whisper"),
            why_needed="Whisper fallback for caption-less videos and podcasts",
            install={
                "mac": "pip install faster-whisper",
                "linux": "pip install faster-whisper",
                "windows": "pip install faster-whisper",
            },
        ),
        CheckResult(
            name="pypdf (Python)",
            present=_has_python_pkg("pypdf"),
            why_needed="Book source — extract text from PDF files",
            install={k: "pip install pypdf" for k in ("mac", "linux", "windows")},
        ),
        CheckResult(
            name="ebooklib + beautifulsoup4 (Python)",
            present=_has_python_pkg("ebooklib") and _has_python_pkg("bs4"),
            why_needed="Book source — extract text from EPUB files",
            install={k: "pip install ebooklib beautifulsoup4" for k in ("mac", "linux", "windows")},
        ),
        CheckResult(
            name="feedparser (Python)",
            present=_has_python_pkg("feedparser"),
            why_needed="Podcast source — parse RSS feeds",
            install={k: "pip install feedparser" for k in ("mac", "linux", "windows")},
        ),
        CheckResult(
            name="trafilatura (Python)",
            present=_has_python_pkg("trafilatura"),
            why_needed="Articles source — extract clean text from URLs",
            install={k: "pip install trafilatura" for k in ("mac", "linux", "windows")},
        ),
        CheckResult(
            name="claude (CLI, optional)",
            present=_has_cli("claude"),
            why_needed="Optional — auto-launch Claude Code to finish seat synthesis",
            install={
                "mac": "see https://claude.com/download",
                "linux": "see https://claude.com/download",
                "windows": "see https://claude.com/download",
            },
        ),
    ]


def required_for(source_type: str, checks: list[CheckResult]) -> list[CheckResult]:
    """Filter checks to those required for a given source type."""
    mapping = {
        "youtube": ["yt-dlp (CLI)", "ffmpeg", "faster-whisper (Python)"],
        "book": ["pypdf (Python)", "ebooklib + beautifulsoup4 (Python)"],
        "podcast": ["ffmpeg", "feedparser (Python)", "faster-whisper (Python)"],
        "articles": ["trafilatura (Python)"],
    }
    names = mapping.get(source_type, [])
    return [c for c in checks if c.name in names]


def print_report(checks: list[CheckResult], os_name: str | None = None) -> tuple[int, int]:
    """Print a status table. Return (present_count, missing_count)."""
    os_name = os_name or detect_os()
    print(f"\nDetected OS: {os_name}\n")
    print("Capability                                Status")
    print("-" * 60)
    present = 0
    missing: list[CheckResult] = []
    for c in checks:
        status = "✓ installed" if c.present else "✗ missing"
        print(f"  {c.name:<40} {status}")
        if c.present:
            present += 1
        else:
            missing.append(c)

    if missing:
        print("\nMissing — here's how to install on your OS:\n")
        cmds: list[str] = []
        for c in missing:
            cmd = c.install.get(os_name, c.install.get("mac", "pip install ..."))
            print(f"  • {c.name}")
            print(f"      {c.why_needed}")
            print(f"      $ {cmd}\n")
            if cmd.startswith("pip install"):
                cmds.append(cmd)
        if cmds:
            pip_pkgs = []
            for cmd in cmds:
                pip_pkgs.extend(cmd.replace("pip install", "").split())
            print("  Or all Python packages at once:")
            print(f"      $ pip install {' '.join(sorted(set(pip_pkgs)))}\n")
            print("  Or the canonical one-liner that installs everything:")
            print(f"      $ pip install -r requirements.txt\n")

    return present, len(missing)


def offer_pip_install() -> bool:
    """Ask the user if we should run `pip install -r requirements.txt` for them."""
    try:
        ans = input("Run `pip install -r requirements.txt` now? [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    if not ans.startswith("y"):
        return False

    req = ROOT / "requirements.txt"
    if not req.exists():
        log("requirements.txt not found")
        return False

    log("installing...")
    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", str(req)]
    try:
        result = subprocess.run(pip_cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        log(f"pip install failed: {e}")
        return False


def doctor() -> int:
    """Standalone preflight check. Returns exit code (0 = all good)."""
    checks = run_checks()
    present, missing = print_report(checks)
    print(f"Summary: {present} present, {missing} missing.\n")
    if missing == 0:
        print("✓ All set. Run `python clawtable.py init` to build your first table.")
        return 0
    print("Install the missing pieces above, then re-run this check or `python clawtable.py init`.")
    return 1
