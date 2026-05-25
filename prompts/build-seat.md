# Build a ClawTable Seat — Synthesis Prompt

You are about to read raw source material (transcripts, book excerpts, articles) from a single person — call them **the subject**. Your job is to compress this material into a **ClawTable advisor seat**: a structured agent definition another AI will load to roleplay this person's strategic thinking lens.

This seat will participate in a multi-agent strategy table designed to surface *honest, falsifiable, testable strategy*. The quality of every future debate depends on whether this seat is grounded in real source material or hallucinated.

## Inputs

- **Subject name:** `{{NAME}}`
- **Source pack directory:** `source-packs/{{SLUG}}/`
- **Source files:** see the appendix below

## Output

Write a single Markdown file to: `seats/{{SLUG}}.md`

Use the template at `prompts/seat-template.md` as the structure. Fill in every section based **only on what the source pack supports**.

## Honest synthesis rules — read before writing

1. **Ground everything.** Every default belief, reflex question, and disagreement must trace to a specific passage in the source pack. If you can't point to a passage, leave it out.
2. **Extract falsifiers, not just claims.** For every "default belief," ask: under what observable evidence would the subject reconsider? Include that falsifier. A belief without a falsifier is faith, not strategy.
3. **No mimicry of voice.** This is a strategy lens, not a persona impression. Clean, declarative English.
4. **Stay legal-safe.** The seat is clearly labeled "not the real person, not endorsed." Do not write anything that pretends to speak for them.
5. **Compress hard.** A seat file should be under ~250 lines. Pick the highest-leverage positions and drop the rest.
6. **Operational, not biographical.** Every line should help a future AI evaluate an idea, not describe the subject's career.
7. **If a section is thin, say so.** Better to write "the source pack does not strongly support a position on X" than to invent one. Future debates fail when seats fabricate positions.

## How to fill each section

### Job lens

In 2–4 short bullets, name the lenses this person reliably evaluates ideas through. Examples from established seats:

- Hormozi → offer strength, painful market, value equation, pricing, risk reversal, lead flow, gross margin, speed to cash, proof, conversion path.
- Munger → inversion, anti-stupidity, incentives, downside risk.
- YC Partner → user pull, focus, wedge selection, founder-market fit.

Extract the equivalent for the subject. Be specific to them.

### Default beliefs

3–6 operating priors that show up repeatedly across the source material. Each one must follow this pattern:

`[Declarative belief]. Source: [specific passage/talk/chapter]. Falsifier: [observable evidence that would change the subject's mind on this].`

A belief without a source citation or without a falsifier doesn't make the cut. Drop it.

### Reflex questions

5–8 questions this person would ask first when handed any new idea. Pull these directly from how they interrogate ideas in the source material. They should be specific and operational, not generic.

### Disagreements

For each of these common advisor archetypes, name the position the subject would push back on — **only include rows where the source pack actually supports a disagreement.** Skip any you can't ground.

- Hormozi (offer-first)
- YC (user-pull-first)
- Munger (anti-stupidity)
- Brunson / Kennedy (funnel + direct response)
- Investor-exit (fundability-first)
- Saraev (AI-automation-first)

For each disagreement, include: the specific position the subject would attack, and the source passage that supports the disagreement.

### Output shape

Use the standard shape from the template. Do not customize unless the source material strongly supports a different evaluation rubric for this subject (rare).

### Source list

List the files you actually used from the source pack — filenames only, one per line. **Do not list files you did not actually read.**

## What "good" looks like

A good seat:
- Cites real passages, not made-up ones.
- Has falsifiers attached to every belief.
- Names what's *outside* its lens, so it can abstain honestly later.
- Reads like an operational checklist, not a Wikipedia summary.
- Could be defended in court as a fair, source-grounded extraction from public material.

A bad seat:
- Has uncited claims that "sound like" the subject.
- Makes the subject look infallible (no falsifiers = no honest critique mechanism).
- Tries to imitate voice or speak for the real person.
- Is so generic it could be any advisor.

---

## Appendix: source pack contents

{{SOURCE_APPENDIX}}
