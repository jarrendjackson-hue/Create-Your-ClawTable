"""YouTube source harvester: download captions via yt-dlp, fall back to faster-whisper."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .util import log, require, source_pack_dir, write_text


def _which(tool: str) -> str | None:
    return shutil.which(tool)


def _ensure_yt_dlp() -> str:
    path = _which("yt-dlp")
    if not path:
        log("yt-dlp not found on PATH.")
        log("install with: pip install yt-dlp  (or brew install yt-dlp)")
        raise SystemExit(1)
    return path


def harvest(query: str, slug: str, max_videos: int = 10, transcribe: bool = True) -> Path:
    """
    Harvest YouTube material for an influencer.

    `query` can be:
      - a channel URL (https://www.youtube.com/@name)
      - a channel handle (@name)
      - a free-text name (will be searched)

    Captions are downloaded first; if missing, audio is transcribed with faster-whisper.
    Output: source-packs/<slug>/transcripts/*.txt
    """
    yt = _ensure_yt_dlp()
    pack = source_pack_dir(slug)
    transcripts = pack / "transcripts"
    audio = pack / "audio"
    transcripts.mkdir(exist_ok=True)
    audio.mkdir(exist_ok=True)

    target = _resolve_target(query)
    log(f"harvesting from: {target}")

    metadata_path = pack / "videos.json"
    cmd = [
        yt,
        "--flat-playlist",
        "--dump-json",
        "--playlist-end", str(max_videos),
        target,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        log(f"yt-dlp metadata failed: {proc.stderr.strip()[:400]}")
        raise SystemExit(1)

    videos = [json.loads(line) for line in proc.stdout.strip().splitlines() if line.strip()]
    metadata_path.write_text(json.dumps(videos, indent=2), encoding="utf-8")
    log(f"found {len(videos)} videos")

    for v in videos:
        vid = v.get("id")
        title = v.get("title", vid)
        if not vid:
            continue
        url = f"https://www.youtube.com/watch?v={vid}"
        transcript_file = transcripts / f"{vid}.txt"
        if transcript_file.exists():
            continue

        # 1) try captions
        caption_text = _try_captions(yt, url, pack, vid)
        if caption_text:
            write_text(transcript_file, f"# {title}\nsource: {url}\n\n{caption_text}\n")
            log(f"captions: {title[:60]}")
            continue

        if not transcribe:
            log(f"skip (no captions, transcribe=False): {title[:60]}")
            continue

        # 2) fall back to whisper
        text = _whisper_transcribe(yt, url, audio, vid)
        if text:
            write_text(transcript_file, f"# {title}\nsource: {url}\n\n{text}\n")
            log(f"whisper: {title[:60]}")
        else:
            log(f"failed: {title[:60]}")

    return pack


def _resolve_target(query: str) -> str:
    q = query.strip()
    if q.startswith("http"):
        return q
    if q.startswith("@"):
        return f"https://www.youtube.com/{q}/videos"
    # free-text search → ytsearchN: returns N results
    return f"ytsearch10:{q}"


def _try_captions(yt: str, url: str, pack: Path, vid: str) -> str | None:
    tmp = pack / "_caption_tmp"
    tmp.mkdir(exist_ok=True)
    cmd = [
        yt,
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs", "en.*",
        "--skip-download",
        "--sub-format", "vtt",
        "-o", str(tmp / "%(id)s.%(ext)s"),
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    vtts = list(tmp.glob(f"{vid}*.vtt"))
    if not vtts:
        return None
    text = _vtt_to_text(vtts[0].read_text(encoding="utf-8", errors="ignore"))
    for f in vtts:
        f.unlink(missing_ok=True)
    return text or None


def _vtt_to_text(vtt: str) -> str:
    lines = []
    for line in vtt.splitlines():
        s = line.strip()
        if not s or s.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if "-->" in s or s.isdigit():
            continue
        # strip caption tags like <c> and <00:00:00.000>
        s = _strip_tags(s)
        if s and (not lines or lines[-1] != s):
            lines.append(s)
    return "\n".join(lines)


def _strip_tags(s: str) -> str:
    import re
    return re.sub(r"<[^>]+>", "", s).strip()


def _whisper_transcribe(yt: str, url: str, audio_dir: Path, vid: str) -> str | None:
    audio_path = audio_dir / f"{vid}.m4a"
    if not audio_path.exists():
        cmd = [
            yt,
            "-f", "bestaudio[ext=m4a]/bestaudio",
            "-o", str(audio_dir / "%(id)s.%(ext)s"),
            url,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            return None
        # yt-dlp may have written a different ext
        candidates = list(audio_dir.glob(f"{vid}.*"))
        if not candidates:
            return None
        audio_path = candidates[0]

    try:
        fw = require("faster_whisper", "pip install faster-whisper")
    except SystemExit:
        return None

    model = fw.WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path), beam_size=1)
    return "\n".join(seg.text.strip() for seg in segments if seg.text.strip())
