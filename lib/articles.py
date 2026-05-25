"""Article harvester: pull clean text from a list of URLs."""
from __future__ import annotations

from pathlib import Path

from .util import log, require, source_pack_dir, write_text


def harvest(urls_file: str | Path, slug: str) -> Path:
    trafilatura = require("trafilatura", "pip install trafilatura")
    requests = require("requests", "pip install requests")

    urls_path = Path(urls_file).expanduser().resolve()
    if not urls_path.exists():
        log(f"urls file not found: {urls_path}")
        raise SystemExit(1)

    urls = [
        line.strip()
        for line in urls_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    log(f"loaded {len(urls)} urls")

    pack = source_pack_dir(slug)
    out = pack / "articles"
    out.mkdir(exist_ok=True)

    for i, url in enumerate(urls):
        log(f"scrape ({i + 1}/{len(urls)}): {url}")
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 clawtable"})
            r.raise_for_status()
            text = trafilatura.extract(r.text, url=url) or ""
        except Exception as e:
            log(f"  failed: {e}")
            continue
        if not text.strip():
            log("  empty extract; skipping")
            continue
        fname = f"{i:03d}-{_slug(url)[:60]}.txt"
        write_text(out / fname, f"source: {url}\n\n{text}\n")

    return pack


def _slug(url: str) -> str:
    import re
    s = re.sub(r"https?://", "", url)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower())
    return s.strip("-") or "article"
