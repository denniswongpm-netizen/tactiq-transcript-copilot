# transcript-copilot

A small, working demo built after applying for Tactiq's Principal Product Manager role, to show
one concrete idea for how "meeting notes for PMs" could go one step further: turning a transcript
directly into a structured, **traceable** PRD draft — decisions, requirements, action items, and
explicitly-open questions — where every single bullet cites the exact line it came from, and a
separate check verifies that citation is real before the draft is trusted.

## Run it

No API key, no dependencies beyond the Python standard library:

```bash
python3 -m transcript_copilot.pipeline sample_transcripts/product_planning_meeting.txt
```

That prints a generated PRD draft to stdout, then reports whether every bullet in it passed the
traceability check. The sample transcript is fictional ("Loopwise" is not a real company) —
written to plausibly resemble a real Tactiq export, with a mix of decisions, feature requests,
commitments, and one deliberately *undecided* item, to show the extractor doesn't just treat
every sentence as equally settled.

Run the test suite:

```bash
python3 -m unittest discover tests -v
```

22 tests, all passing, including three specifically designed to *break* the traceability check on
purpose (a bullet citing a line that doesn't exist, a bullet whose wording was never actually said
on the line it cites, a bullet with no citation at all) — proving the check actually catches a
fabricated claim rather than rubber-stamping everything.

## Why this shape, specifically

The idea I wanted to show isn't "AI can summarize a meeting" — that's the table-stakes part of
what Tactiq already does well. It's this: **a generated artifact should never claim something the
source material didn't actually say, and that should be a mechanically checked property of the
system, not just a hope about how carefully the model was prompted.** For a product whose entire
value proposition is being a trustworthy record of what actually happened in a meeting, I think
that property is worth making structurally impossible to violate, not just something a good prompt
tries to encourage.

Concretely, that means:

- **`transcript_copilot/parser.py`** parses a transcript into addressable lines, each keeping its
  real line number from the source file — the citation key everything downstream points back to.
- **`transcript_copilot/extractor.py`** pulls out decisions, action items, feature requests, and
  *explicitly open* questions. It's rule-based on purpose for this demo (no API key needed, and
  every pattern is readable/auditable in one file) — a production version would likely swap this
  for an LLM call for better recall on phrasing this doesn't anticipate, but the contract stays
  identical either way: every extracted item must carry the real transcript line it came from.
- **`transcript_copilot/prd_builder.py`** assembles the draft. An empty section says so honestly
  ("No decisions extracted from this transcript") instead of being padded with a plausible-sounding
  guess to make the document look more complete than the meeting actually was.
- **`transcript_copilot/traceability_check.py`** is the actual gate: it re-derives each bullet's
  citation, looks that line up fresh in the real transcript, and confirms the bullet's wording is
  genuinely present on it. A citation to a line that doesn't exist, or a claim that isn't actually
  on the line it cites, is flagged — this is what `tests/test_traceability_check.py` deliberately
  exercises with three synthetic hallucinations.

This pattern — draft, then a separate mechanical check that can actually fail the draft, with the
check kept independent of the generation step so it can't be fooled by confident-sounding output —
is the same one I used building an AI-orchestrated platform end-to-end (strategy, architecture, and
execution), where every generated artifact goes through comparable code-level checks before a
human ever reviews it, backed by 2,000+ automated tests. This repo is a small, self-contained
adaptation of that same discipline to Tactiq's own domain, not a from-scratch idea.

## What I'd build next if this were real

- Swap the rule-based extractor for an LLM call, keeping the exact same "every item must cite a
  real source line" contract — the traceability check doesn't care how an item was extracted, only
  whether its citation is genuine.
- Handle multi-line context (a decision that spans several back-and-forth lines, not just one).
- Feed the "Open Questions" section into an actual follow-up mechanism (a Slack nudge, a Linear
  ticket) — the same category of workflow Tactiq's existing integrations already point at.

— Dennis Wong
[linkedin.com/in/denniswongpm](https://linkedin.com/in/denniswongpm)
