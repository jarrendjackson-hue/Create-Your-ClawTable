# CLI workflow

## Contents

- Runtime and provenance
- Obtain a working copy
- Dependencies by source
- Import and build commands
- Verification and known limits

## Runtime and provenance

Upstream: https://github.com/jarrendjackson-hue/Create-Your-ClawTable

Verified revision: `742a198a9231a7388e63e9a2f43c39c19afad7c4`.

Use a terminal, a writable directory, Git, and a supported Python 3 environment; Python 3.10 or later is a conservative baseline. The packaged workflow was exercised with Python 3.12. Use the environment's actual Python command (`python3`, `python`, or Windows `py`) consistently.

The upstream CLI downloads or reads sources and writes files locally. The current LLM synthesizes the seats. No OpenAI or Anthropic API key is required by the CLI; the user's chosen LLM service may have its own cost.

## Obtain a working copy

If the user already has a checkout, inspect it and preserve all existing files and changes. Use a new directory when a clean pinned copy is needed. Run the following from a user-approved working location only if `clawtable-work` does not already exist:

```sh
git clone https://github.com/jarrendjackson-hue/Create-Your-ClawTable.git clawtable-work
cd clawtable-work
git checkout --detach 742a198a9231a7388e63e9a2f43c39c19afad7c4
python3 clawtable.py --help
```

Use this public checkout under its own MIT license. Do not recreate its modules by copying marketplace-delivered skill content to disk. If GitHub or installation is unavailable, use the chat-only path with supplied source text and be explicit about the limitation.

Run commands from the checkout root. The CLI writes its outputs relative to its own source directory, not the caller's current directory. Inputs such as book paths resolve relative to the current directory unless absolute paths are supplied.

## Dependencies by source

Install only the dependencies needed for the selected source in a virtual environment. Inspect available tools before installing. The upstream full requirements are in `requirements.txt`:

```sh
python3 -m venv .venv
```

On macOS/Linux, use `.venv/bin/python` for Python and place `.venv/bin` on the command's PATH for YouTube, because the CLI invokes `yt-dlp` by executable name. On Windows, use `.venv\Scripts\python.exe` and the corresponding Scripts directory on PATH. Activating the environment normally handles both.

| Source or operation | Required components |
| --- | --- |
| TXT/MD import, prompt generation, bundle | Python standard library |
| PDF text extraction | `pypdf`; image-only scans need a separately supplied readable transcription |
| EPUB extraction | `ebooklib`, `beautifulsoup4` |
| YouTube captions | `yt-dlp` executable on PATH |
| YouTube audio fallback | `yt-dlp`, `faster-whisper`, `ffmpeg` |
| Podcast RSS/audio | `feedparser`, `requests`, `faster-whisper`; upstream preflight also requires `ffmpeg` |
| Articles | `requests`, `trafilatura` |

For the complete upstream setup, run `python -m pip install -r requirements.txt` inside the activated virtual environment. This includes audio-transcription dependencies and may be substantially larger than a text-only setup. `ffmpeg` is a separate system dependency; use the upstream `doctor` output and the user's OS package manager rather than guessing commands.

`python clawtable.py doctor` reports capabilities. Inspect its printed report: at the verified revision, the CLI does not propagate the doctor's nonzero return status, so exit code zero does not prove all dependencies are installed. Do not install the optional Claude CLI merely to synthesize seats; the current LLM can do that step.

Whisper runs locally and downloads its model on first use. Audio harvesting consumes bandwidth, disk space, and compute time. Use captions-only mode when appropriate.

## Import and build commands

Replace all example names, paths, slugs, and URLs with the user's selected inputs. Quote shell arguments safely, especially names and paths. Do not paste source text into a shell command.

```sh
# Authorized local text/document. PDF, EPUB, TXT and MD are supported.
python clawtable.py add-book /absolute/path/to/notes.md --name "Selected Advisor" --slug selected-advisor

# Public YouTube channel or URL, initially captions only.
python clawtable.py add-youtube "https://www.youtube.com/@selected-channel" --max 3 --no-transcribe --slug selected-advisor

# User-selected podcast RSS feed. Downloads and transcribes audio locally.
python clawtable.py add-podcast "https://selected-publisher.example/feed.xml" --name "Selected Advisor" --slug selected-advisor --max 2

# Text file containing one user-selected public article URL per line.
python clawtable.py add-articles /absolute/path/to/urls.txt --name "Selected Advisor" --slug selected-advisor

# Generate the synthesis prompt using exactly the same slug.
python clawtable.py prompt --name "Selected Advisor" --slug selected-advisor
```

Inspect `source-packs/selected-advisor/` and read `build-prompts/selected-advisor.md`. Read the upstream `prompts/seat-template.md`. Use the current LLM to produce `seats/selected-advisor.md` from that evidence. Repeat for each advisor.

```sh
# Include only the requested lineup. Use actual seat filename stems.
python clawtable.py build --seats selected-advisor,second-advisor
```

The bundle is `dist/clawtable-bundle.md`. The interactive `python clawtable.py init` wizard exists for human-guided setup; prefer explicit commands for agent operation so source selection and downloads remain controlled.

## Verification and known limits

- Confirm substantial extracted text exists before generating a seat. A successful command may still have skipped all inaccessible sources.
- YouTube captions are selected with `en.*` in this revision. Do not promise arbitrary caption languages.
- A free-text YouTube search uses `ytsearch10:` internally. Use an exact channel URL when a larger or precise lineup of videos matters.
- Build prompts inline at most 25,000 characters of source text, with paths for omitted files. Read omitted files explicitly before citing them.
- `build --seats` filters existing files and can silently omit a missing requested slug. Compare requested slugs with actual files and the final bundle.
- Local books may contain copyrighted text. Keep raw material local and avoid republishing it. Use summaries and citations rather than reproducing full texts.
- The package contains no prebuilt advisor seats or third-party transcripts. Source availability and the user's LLM determine the resulting quality.
- Twitter, Substack archive harvesting, a web UI, hosted processing, and voice synthesis are not implemented in this upstream revision.
