# Manuscript review — `main.tex`, read 2026-08-02

Checked against the execution sheet of 2026-08-01. Counts below are from a
mechanical pass over the file; each is reproducible with a grep.

## Blocking — fix before anything goes public

**1. Placeholder in the author block.** The first author's footnote reads
`\thanks{superman.Email: ...}`. There is no affiliation, and a stray word sits
where the affiliation belongs. The second author's footnote is complete. This
is the first thing a desk editor sees.

**2. Two authors, one narrator.** The byline has two authors; the text uses
"I" and "my" (11 occurrences) and never says "first author" or "second author"
(0 occurrences). Either the second author's role is stated explicitly — and
the gate-adjudication rule makes that role substantive, not honorary — or the
byline is wrong. A reviewer of a single-actor case study will ask this on
page 1.

**3. The two instruments are absent.** The execution sheet fixes a
candidate-action log and a gate-adjudication rule as the two things that
survive the decision not to preregister. Neither appears in the manuscript:
`candidate-action` 0 occurrences, `adjudicat*` 0, `conflict of interest` 0,
`\REDACT` 0 (the sheet's item 1 refers to `\REDACT{}` fields that this version
of the file does not define). Without them, §5.4 (Principle 4) has no
instrument and §7.3 concedes the self-interest problem without a control.
Draft text for both is in `patch-fragments.tex`.

## Internal inconsistencies

**4. "four planned design principles" — there are five.** Method §4.3 codes
"descriptively against the four planned design principles" while §5 defines
Principles 1–5 and the abstract enumerates five. Principle 5 was evidently
added after the Method section was written.

**5. Principles are "planned" in one place and "emergent" in another.** The
abstract says five principles "emerged from the planning phase"; §5's opening
presents them as design reasoning fixed in advance; §4.3 codes against them as
*planned*. Pick one. For the regulatory-practice venue, "fixed in advance and
tested" is the stronger and more defensible claim — and it is what the gate
table actually documents.

**6. Table 1 overlaps on W7.** Rows read W1–2, W3–5, W6–7, W7–9, W10–12. W7
appears twice, so the twelve weeks sum to thirteen. Also W6–7 and W10–12 have
`---` in the learning column while the text says learning is compressed toward
the front; that is consistent, but state it in the caption rather than leaving
an em-dash to carry the argument.

**7. RQ2 has no sub-parts, but the design refers to one.** The execution sheet
discusses "RQ2c" — the AI-and-goal-selection claim. In the manuscript RQ2 is a
single undivided question bundling deadlines, artifacts, and AI. Splitting it
into RQ2a/b/c gives the candidate-action log a research question to answer and
makes the falsification rule reportable.

## Positioning

**8. The header targets the wrong venue.** The file header names "HRD /
workplace learning journal (Journal of Workplace Learning, HRDI, Studies in
Continuing Education)". The execution sheet ranks *International Cybersecurity
Law Review* first, on the A (regulatory/practice) branch. These want different
papers: the HRD framing leads with self-directed-learning theory and
Knowles/Garrison; the regulatory-practice framing leads with what a solo
practitioner actually did against a statutory deadline, and treats the SDL
literature as background. The current text is the HRD paper. Decide before
October, then cut accordingly — §2.1–2.3 shrink to about a third for the
regulatory venue.

**9. "ICLR" is a collision.** In your field ICLR reads as the machine-learning
conference. Write *International Cybersecurity Law Review* in full in every
internal document, or the wrong reader will draw the wrong conclusion from a
one-line note.

## Smaller items

- Abstract, "Data comprise a daily work journal…" — add the candidate-action
  log once it exists; it is the only quantified element in the study.
- §4.2 promises "\tbd{final entry count and total logged hours}". `make
  aggregate` computes both from `logs/journal/`; cite `derived/hours.json`.
- 10 `\tbd{}` markers remain, all in §6 Findings and §7.3 — expected before
  W12, but the two in §4 (entry count, artifact links/DOIs) can be closed
  early by the repository.
- §3 states the Annex III product-class finding was "reached in week~2" —
  written in the past tense in a document dated before W1. Move to the future
  or the conditional until it has happened.
- Ethics §4.4 has an IRB placeholder. Self-experimentation with no other human
  subjects is normally exempt, but the outreach contacts in W6 and W10–12 are
  third parties; say explicitly that no data about them is reported beyond
  aggregate response counts.
