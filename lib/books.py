"""Book harvester: extract clean text from PDF and EPUB files."""
from __future__ import annotations

from pathlib import Path

from .util import log, require, source_pack_dir, write_text


def harvest(book_path: str | Path, slug: str) -> Path:
    """Extract text from a single book file into source-packs/<slug>/books/."""
    book = Path(book_path).expanduser().resolve()
    if not book.exists():
        log(f"book not found: {book}")
        raise SystemExit(1)

    pack = source_pack_dir(slug)
    out_dir = pack / "books"
    out_dir.mkdir(exist_ok=True)

    ext = book.suffix.lower()
    if ext == ".pdf":
        text = _read_pdf(book)
    elif ext == ".epub":
        text = _read_epub(book)
    elif ext in (".txt", ".md"):
        text = book.read_text(encoding="utf-8", errors="ignore")
    else:
        log(f"unsupported book format: {ext}  (use .pdf, .epub, .txt, or .md)")
        raise SystemExit(1)

    out_file = out_dir / f"{book.stem}.txt"
    write_text(out_file, f"# {book.stem}\nsource: {book.name}\n\n{text}\n")
    log(f"book extracted: {book.name} -> {out_file.relative_to(pack.parent.parent)}")
    return pack


def _read_pdf(path: Path) -> str:
    pypdf = require("pypdf", "pip install pypdf")
    reader = pypdf.PdfReader(str(path))
    parts = []
    for i, page in enumerate(reader.pages):
        try:
            parts.append(page.extract_text() or "")
        except Exception as e:
            log(f"  page {i} extract failed: {e}")
    return "\n\n".join(p.strip() for p in parts if p.strip())


def _read_epub(path: Path) -> str:
    ebooklib = require("ebooklib", "pip install ebooklib beautifulsoup4")
    from ebooklib import epub  # noqa: F401  (validates install)
    bs4 = require("bs4", "pip install beautifulsoup4")

    book = ebooklib.epub.read_epub(str(path))
    parts = []
    ITEM_DOCUMENT = ebooklib.ITEM_DOCUMENT
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        soup = bs4.BeautifulSoup(item.get_content(), "html.parser")
        text = soup.get_text(separator="\n").strip()
        if text:
            parts.append(text)
    return "\n\n".join(parts)
