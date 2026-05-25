"""Podcast harvester: pull episodes from an RSS feed and transcribe locally."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .util import log, require, source_pack_dir, write_text


def harvest(feed_url: str, slug: str, max_episodes: int = 10) -> Path:
    feedparser = require("feedparser", "pip install feedparser")
    requests = require("requests", "pip install requests")

    pack = source_pack_dir(slug)
    transcripts = pack / "podcasts"
    audio_dir = pack / "audio"
    transcripts.mkdir(exist_ok=True)
    audio_dir.mkdir(exist_ok=True)

    log(f"parsing feed: {feed_url}")
    feed = feedparser.parse(feed_url)
    entries = feed.entries[:max_episodes]
    log(f"found {len(entries)} episodes")

    if not entries:
        return pack

    fw = require("faster_whisper", "pip install faster-whisper")
    model = fw.WhisperModel("base", device="cpu", compute_type="int8")

    for i, entry in enumerate(entries):
        title = entry.get("title", f"episode-{i}")
        safe = _slug(title)[:80]
        transcript_file = transcripts / f"{safe}.txt"
        if transcript_file.exists():
            continue

        audio_url = _audio_url(entry)
        if not audio_url:
            log(f"no audio enclosure: {title[:60]}")
            continue

        audio_path = audio_dir / f"{safe}.mp3"
        if not audio_path.exists():
            log(f"download: {title[:60]}")
            try:
                with requests.get(audio_url, stream=True, timeout=60) as r:
                    r.raise_for_status()
                    with audio_path.open("wb") as f:
                        shutil.copyfileobj(r.raw, f)
            except Exception as e:
                log(f"  download failed: {e}")
                continue

        log(f"transcribe: {title[:60]}")
        try:
            segments, _ = model.transcribe(str(audio_path), beam_size=1)
            text = "\n".join(s.text.strip() for s in segments if s.text.strip())
        except Exception as e:
            log(f"  whisper failed: {e}")
            continue

        write_text(transcript_file, f"# {title}\nsource: {audio_url}\n\n{text}\n")

    return pack


def _audio_url(entry) -> str | None:
    for link in entry.get("links", []):
        if link.get("rel") == "enclosure" and link.get("type", "").startswith("audio"):
            return link.get("href")
    for enc in entry.get("enclosures", []):
        if enc.get("type", "").startswith("audio"):
            return enc.get("url")
    return None


def _slug(s: str) -> str:
    import re
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower())
    return s.strip("-") or "episode"
