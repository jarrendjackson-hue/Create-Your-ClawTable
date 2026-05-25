# clawtable

**Build your own AI strategy round table.**

Type in the people you want at your table — Hormozi, Munger, Naval, your favorite YouTuber, the author of a book on your shelf. ClawTable harvests their public content, hands it to Claude (or any LLM) to compress into an "advisor seat," and bundles your roster into a single prompt you paste into a chat.

Then you ask the table questions and watch them debate, pressure-test, and vote.

> ⚠️ **Not affiliated, not endorsed.** Each seat is a strategy lens grounded in publicly available material. Seats are clearly labeled as not the real person. This is a thinking tool, not a celebrity impersonator.

---

## What you get

- **`clawtable.py`** — one CLI to harvest sources and assemble your table.
- **Four source types** — YouTube channels, books (PDF/EPUB), podcasts (RSS), and article URL lists.
- **Local-first transcription** — uses `yt-dlp` for captions and `faster-whisper` for fallback. No paid APIs.
- **LLM-agnostic output** — the final bundle is plain Markdown. Paste it into Claude, ChatGPT, Gemini, Cursor, anywhere.
- **No API keys required** — Claude does the seat-synthesis step inside your existing chat session.

---

## 60-second quickstart

```bash
git clone https://github.com/YOUR-USERNAME/clawtable.git
cd clawtable
pip install -r requirements.txt
python clawtable.py init
```

The `init` wizard asks who you want at your table, picks where each one's material lives (YouTube / book / podcast / articles), harvests it, and generates a "build this seat" prompt for Claude. Then it tells you how to connect your brain (Claude Code) to finish.

Prefer the manual flow? Run the commands below instead.

Add three people from three different source types:

```bash
# 1) Pull from a YouTube channel
python clawtable.py add-youtube "Alex Hormozi" --max 15

# 2) Upload a book (drop the PDF into ./books/ first)
python clawtable.py add-book books/poor-charlies-almanack.pdf --name "Charlie Munger"

# 3) Add a podcast feed
python clawtable.py add-podcast https://feeds.megaphone.fm/HSW3993340834 --name "MFM"
```

Now generate a "build this seat" prompt for each one:

```bash
python clawtable.py prompt --name "Alex Hormozi"
python clawtable.py prompt --name "Charlie Munger"
python clawtable.py prompt --name "MFM"
```

That writes three files to `build-prompts/`. Open each in **Claude Code** (or paste into Claude.ai). Claude reads the raw source pack inline and writes a clean seat file to `seats/`.

Finally, bundle the table:

```bash
python clawtable.py build
```

You get `dist/clawtable-bundle.md`. Paste it into any LLM and tell it your idea.

---

## How it works

```
       ┌────────────────────────────────────────────────┐
       │  YouTube  │  Books  │  Podcasts  │  Articles   │
       └─────┬─────────┬─────────┬───────────┬──────────┘
             ▼         ▼         ▼           ▼
                  source-packs/<slug>/
                  (raw transcripts + text)
                            │
                            ▼
              build-prompts/<slug>.md
       (a paste-into-Claude synthesis prompt)
                            │
                            ▼                 (Claude writes this)
                   seats/<slug>.md
                            │
                            ▼
              dist/clawtable-bundle.md
   (orchestrator + every seat, in one file)
                            │
                            ▼
              Paste into any LLM → talk
```

The CLI's job is harvesting raw material. Claude's job is synthesis. Your job is asking the right question.

---

## Commands

| Command | What it does |
|---|---|
| `init` | Interactive wizard — pick influencers, pick source for each, harvest, generate build-prompts, print Claude Code launch instructions. |
| `add-youtube "Name or URL"` | Pulls captions (or whisper-transcribes) up to N videos. |
| `add-book path/to/file.pdf --name "..."` | Extracts text from PDF / EPUB / TXT / MD. |
| `add-podcast https://feed/ --name "..."` | Downloads N episodes and transcribes locally. |
| `add-articles urls.txt --name "..."` | Scrapes a list of URLs (one per line). |
| `prompt --name "..."` | Generates the seat-build prompt for Claude. |
| `build` | Stitches every seat in `seats/` into a paste-ready bundle. |
| `build --seats hormozi,munger` | Bundles only the seats you name. |

Run any command with `--help` for full options.

---

## Why this exists

I built a private version of this for myself — a round table of advisors I could ask big questions and get pressure-tested answers, not just one model's polite consensus. The hard part wasn't the prompting, it was getting honest source-grounded lenses for each advisor.

This repo is the public, do-it-yourself version. Type in who *you* want at your table.

The private version is at [ClawTable Advisors] — this one is yours to remix.

---

## FAQ

**Do I need an OpenAI/Anthropic API key?**
No. The CLI only harvests content. The synthesis step happens inside Claude (or any LLM) when you paste the generated prompt.

**Is this legal?**
You're downloading public content for personal use and asking an LLM to summarize it into a strategy lens. The output is clearly labeled as not the real person. Don't republish transcripts. Don't claim seats are endorsed. Don't be weird.

**Will my favorite influencer work?**
Probably. The richer their public material, the better the seat. If they have a YouTube channel with 50+ hours of substantive content, or a book, you'll get a strong seat. If they only post one-liners on X, you won't.

**How do I share my table?**
By default `seats/*.md` is git-ignored. If you want to share a table, `git add -f seats/some-seat.md` and push it. Don't commit raw transcripts (`source-packs/` is ignored for good reason).

**Can I edit a seat by hand after Claude writes it?**
Yes. The seat is plain Markdown. Edit it, then re-run `build`.

---

## Roadmap

- `add-twitter` — pull a recent timeline of substantive threads.
- `add-substack` — full archive of a newsletter.
- Web UI for non-CLI users.
- Hosted version where you don't need to clone anything.

PRs welcome.

---

## License

MIT. See `LICENSE`.
