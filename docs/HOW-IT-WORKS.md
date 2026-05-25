# How ClawTable Works

A longer walkthrough of what happens at each step.

## 1. Harvest

When you run `add-youtube "Alex Hormozi"`, the CLI:

1. Resolves the input — if it's a URL, uses it directly; if `@handle`, builds the channel URL; otherwise runs a YouTube search.
2. Lists the latest N videos via `yt-dlp --dump-json`.
3. For each video, tries to download auto-generated captions first (fast, no transcription cost).
4. If captions don't exist, downloads the audio and runs `faster-whisper` locally.
5. Writes each transcript to `source-packs/<slug>/transcripts/<video-id>.txt`.

Books, podcasts, and articles follow the same pattern: raw text → `source-packs/<slug>/<category>/*.txt`.

The CLI never sends data to an external LLM. Everything stays on your machine.

## 2. Synthesis prompt

`python clawtable.py prompt --name "..."` reads everything in `source-packs/<slug>/` and renders `prompts/build-seat.md` with the source pack inlined as an appendix.

The output goes to `build-prompts/<slug>.md`. That file is a self-contained prompt: it includes the seat template, the synthesis rules, and the raw source material.

If your source pack is too large to inline (> ~25k characters per file), the prompt references the file on disk and you point Claude at the path instead.

## 3. Seat creation (Claude does this)

You open `build-prompts/<slug>.md` in Claude Code (or copy-paste into Claude.ai). Claude reads the raw material, extracts the subject's distinct lens, and writes a clean seat file to `seats/<slug>.md` following the template.

Why Claude and not the CLI? Because compressing 50 hours of someone's content into a coherent strategy lens is a *judgment* task. A deterministic script would produce a worse result than letting Claude reason about it.

## 4. Bundle

`python clawtable.py build` stitches `prompts/orchestrator.md` + every file in `seats/` into one Markdown file at `dist/clawtable-bundle.md`. That's your paste-ready table.

You can also bundle a subset: `python clawtable.py build --seats hormozi,munger`.

## 5. Use the table

Open a fresh chat in your LLM of choice. Paste the whole bundle. The orchestrator prompt at the top tells the LLM how to run the meeting. Now ask your question.

The orchestrator runs these rounds:

1. Context framing
2. Independent proposals from each seat
3. Cross-examination — seats name where they disagree
4. Revision
5. Vote — `GO` / `KILL` / `REVISE`
6. Synthesis with a strict final-output contract

You get a decision, the best move, the main risk, a 7-day test, kill criteria, and one action for today.

## File layout

```
clawtable/
├── clawtable.py               # CLI entry
├── lib/                       # harvesters + bundler
│   ├── util.py
│   ├── youtube.py
│   ├── books.py
│   ├── podcasts.py
│   ├── articles.py
│   └── seat.py
├── prompts/                   # prompt contracts (shipped, edit at your own risk)
│   ├── orchestrator.md
│   ├── seat-template.md
│   └── build-seat.md
├── source-packs/              # raw harvested text — git-ignored
├── build-prompts/             # paste-into-Claude prompts — git-ignored
├── seats/                     # synthesized seats — git-ignored by default
├── books/                     # drop your PDFs/EPUBs here
└── dist/                      # final bundle — git-ignored
```

## Customizing

- **Edit the orchestrator** — `prompts/orchestrator.md`. Want different rounds, a different output contract, a different mode? Edit and re-bundle.
- **Edit the seat template** — `prompts/seat-template.md`. Want different output shapes from your seats? Edit before generating build prompts.
- **Hand-write a seat** — drop a Markdown file into `seats/`. The bundler doesn't care where it came from.
