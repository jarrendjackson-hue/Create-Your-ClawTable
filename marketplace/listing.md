# Create-Your-ClawTable — AI Strategy Roundtable

**Submission status:** Prepared; not submitted to Agensi. Google sign-in is required to continue.

**Draft price:** Free

**Categories:** Agents & Orchestration · Research & Analysis · Business & Operations

**Tags:** strategy, advisors, research, decision-making, open-source, clawtable

**Documentation:** https://github.com/jarrendjackson-hue/Create-Your-ClawTable

## Marketplace summary

Build a custom AI advisor roundtable from your chosen YouTube channels, books, podcasts, and articles. Turn source material into cited strategy lenses, pressure-test ideas, and export a reusable Markdown prompt.

## Marketplace description

## Build your own AI strategy roundtable

Choose the thinkers, creators, books, or other sources you want at your table. Create-Your-ClawTable helps your agent turn that material into source-grounded advisor seats and assemble them into a reusable Markdown prompt.

Use the table to develop a plan or pressure-test a specific idea through proposals, a Devil’s Advocate, cross-examination, revisions, votes, and a conditional red-team round. Finish with a decision, the main risk, falsifiers, practical tests, and a concrete next action.

## What the skill helps you do

- Collect material with the open-source Python CLI from public YouTube channels, podcast RSS feeds, article URL lists, and authorized local PDF, EPUB, TXT, or Markdown files.
- Synthesize concise advisor seats with source anchors, operating beliefs, reflex questions, and explicit limits.
- Build a table from your selected seats and export the orchestrator plus lineup as one Markdown bundle.
- Run Strategy Mode for a goal or Judge Mode for a proposal, with room for disagreement and abstention.

## What is included

An agent workflow, verified CLI instructions, seat-synthesis guidance, a roundtable protocol, and the MIT license. The skill uses Jarren Jackson’s public Create-Your-ClawTable project, with a documented source revision. It contains no prebuilt celebrity seats or third-party transcripts.

## Requirements

For source harvesting, your agent needs terminal access, Python, and the upstream open-source CLI. Dependencies vary by source; audio transcription uses local Whisper and requires additional setup. The CLI does not require an OpenAI or Anthropic API key. Seat synthesis runs in your existing LLM session, whose normal service costs may apply.

In a chat-only environment, the skill can work from source text you supply and help create seats and run the discussion. It cannot execute the CLI or fetch inaccessible files there.

## Honest, source-grounded perspectives

Advisor seats are AI-generated strategic lenses, not the actual people, endorsements, or independent AI models. Unsupported claims are flagged, citations come from material actually read, and the skill can abstain when the evidence is insufficient. Use only sources you are authorized to access and keep raw books, transcripts, and private documents out of public listings.

Free and open source under the MIT license.

---

## Package validation

Validated a local Markdown source import, generated a synthesis prompt, created a source-grounded advisor seat, and built a bundle containing exactly that seat plus the orchestrator. Online harvesting and Agensi’s upload checks have not been exercised in this validation. The ZIP contains SKILL.md at the root, the MIT license, agent metadata, and three workflow references.

## Build the upload package

From the project root, run `python3 scripts/package_agensi.py`. The output is `dist/Create-Your-ClawTable.zip`.
