# Build a ClawTable Seat — Synthesis Prompt

You are about to read raw source material (transcripts, book excerpts, articles) from a single person — call them **the subject**. Your job is to compress this material into a **ClawTable advisor seat**: a structured agent definition another AI will load to roleplay this person's strategic thinking lens.

## Inputs

- **Subject name:** `{{NAME}}`
- **Source pack directory:** `source-packs/{{SLUG}}/`
- **Source files:** see the appendix below

## Output

Write a single Markdown file to: `seats/{{SLUG}}.md`

Use the template at `prompts/seat-template.md` as the structure. Fill in every section based **only on what the source pack supports**. Do not invent positions the source pack does not back up.

## How to fill each section

### Job lens

In 2–4 short bullets, name the lenses this person reliably evaluates ideas through. Examples from established seats:

- Hormozi → offer strength, painful market, value equation, pricing, risk reversal, lead flow, gross margin, speed to cash, proof, conversion path.
- Munger → inversion, anti-stupidity, incentives, downside risk.
- YC Partner → user pull, focus, wedge selection, founder-market fit.

Extract the equivalent for the subject. Be specific to them.

### Default beliefs

3–6 operating priors that show up across the source material. Each one should be a single declarative sentence that a future AI can use as a default assumption.

Pattern: "{X is true / Y is the right move / Z doesn't work} — because {short reason from sources}."

### Reflex questions

5–8 questions this person would ask first when handed any new idea. Pull these directly from how they interrogate ideas in the source material. They should be specific, not generic.

### Disagreements

For each of these common advisor archetypes, name the position the subject would push back on — only include rows where the source pack actually supports a disagreement. Skip any you can't ground.

- Hormozi (offer-first)
- YC (user-pull-first)
- Munger (anti-stupidity)
- Brunson / Kennedy (funnel + direct response)
- Investor-exit (fundability-first)
- Saraev (AI-automation-first)

### Source list

List the files you actually used from the source pack — filenames only, one per line.

## Rules

1. **Ground everything.** If you can't point to a passage in the source pack, leave it out.
2. **No mimicry of voice.** This is a strategy lens, not a persona impression. Write in clean, declarative English.
3. **Stay legal-safe.** The seat is clearly labeled "not the real person, not endorsed." Do not write anything that pretends to speak for them.
4. **Compress hard.** A seat file should be under ~250 lines. If you have more material, pick the highest-leverage positions.
5. **Keep it operational.** Every line should help a future AI evaluate an idea, not just describe the subject.

---

## Appendix: source pack contents

{{SOURCE_APPENDIX}}
