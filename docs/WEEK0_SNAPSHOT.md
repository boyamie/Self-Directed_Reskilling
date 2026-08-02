# Week-0 snapshot — the "before" measurement

**Who fills this in: the first author, and nobody else.** The first author is
the participant — the person who owns the venture M5 tests and who carries out
the twelve weeks (PROTOCOL.md §1, §4). Every measurement below is a measurement
of that person. The second author holds the repository and adjudicates the
gates; their own knowledge of the CRA is not what this study measures, and a
snapshot filled in by them measures the wrong person.

This was not stated in the first version of this file, and Part B was filled in
once by the second author in good faith before the omission was noticed. See
the note above the Part B table.

**Complete before 2026-08-03 (W1).** Tag the repository `w0` when done. After
W1 begins this file is frozen; nothing below can be honestly re-measured once
twelve weeks of learning have happened.

Budget: about two hours. Three parts.

## Fill them in this order: B, then C, then A

The parts are lettered by topic but they are not independent, and the order
below is the one that keeps them measurable.

**B first, before anything else.** It asks what twenty terms mean to you with
no lookups. Part A is a search through Korean CRA material — doing it first
puts SBOM, VEX and Annex III in front of you, and the ratings afterwards are no
longer a "before" measurement. The W0/W12 pair is the only quantitative measure
in the study; if B is contaminated, half of it is gone and nothing later can
recover it.

**C second.** Its prior expectation — which track you expect M1 to pick, with a
confidence figure — is the quantity M1 tests. Part A is evidence bearing on
exactly that, so recording the expectation after the search measures the search
instead of the prior.

**A last.** Nothing in A is harmed by having done B and C.

While B is unfinished, do not look terms up, and do not ask an AI assistant
about the CRA. It is the most convenient lookup device within reach and the
easiest way to lose the baseline without noticing.

---

## Part B — Terminology self-assessment (~40 min) · do this first

Twenty terms, rated **before** any study. Scale:

- **0** — have not heard the term
- **1** — recognise it, could not define it
- **2** — could define it in a sentence
- **3** — could explain it to a client and answer follow-up questions
- **4** — could produce or audit the artifact it names

Rate honestly and quickly; a considered rating is already contaminated by
looking things up. Repeat the identical list at W12 without consulting this
file first.

The "what I think it means" column matters as much as the number. A wrong
one-line gloss recorded now is evidence; the same term rated 3 at W12 with a
correct gloss is the finding. Write the gloss even where the rating is 0 — "no
idea, sounds like it is about X" is usable data.

### Two rating rules, fixed at W0 and applied identically at W12

Both came up while the W0 ratings were being made. They are written down here
because a scale applied one way at W0 and another way at W12 measures the
change in the scale.

**1. Rate the concept, not the English label.** The list is in English and the
rater is not. If a label leaves you blank, that is a 0 — but if seeing it makes
a Korean name surface unprompted, rate the concept and put that Korean name in
the gloss. The test is whether it surfaces on its own; looking it up or
translating it is a lookup and ends the measurement.

**2. A gloss read off the English words is a 1, not a 3.** Several of these
terms are transparent compounds — *actively exploited vulnerability*,
*coordinated vulnerability disclosure policy*, *product with digital elements*,
*technical documentation* — and a plausible sentence can be assembled from the
words alone. That is not the same as knowing what the term denotes in this
regulation, and 3 on this scale claims you could field a client's follow-up
questions. If the answer came from reading the words, the rating is 1.

This rule matters in a specific direction: an inflated W0 shrinks the measured
gain at W12 and under-reports what was actually learned.

> **Superseded once.** This table was first filled in by the second author, on
> 2026-08-02, before it said whose ratings it wanted. Those ratings and the
> record extracted from them are in this repository's history at `e8af4b0` and
> are timestamped; they are not deleted, because a repository whose whole
> purpose is an unedited record should not quietly drop the part that went
> wrong. They are kept as the *second author's* baseline — useful in its own
> right, since it says how much of this field the adjudicator knew — and are
> not the study's measurement. The table below is the first author's.

| # | Term | Rating (0–4) | One line: what I think it means |
|---|---|---|---|
| 1 | Cyber Resilience Act, Annex I |  |  |
| 2 | Annex III important products, class I / II |  |  |
| 3 | Default class / manufacturer self-assessment |  |  |
| 4 | Conformity assessment module (A / B+C / H) |  |  |
| 5 | CE marking, declaration of conformity |  |  |
| 6 | Product with digital elements (PDE) |  |  |
| 7 | SBOM |  |  |
| 8 | SPDX |  |  |
| 9 | CycloneDX |  |  |
| 10 | Syft |  |  |
| 11 | Grype |  |  |
| 12 | CVE |  |  |
| 13 | CVSS |  |  |
| 14 | VEX |  |  |
| 15 | Actively exploited vulnerability |  |  |
| 16 | Coordinated vulnerability disclosure policy |  |  |
| 17 | Support period / security update obligation |  |  |
| 18 | Technical documentation (Annex VII) |  |  |
| 19 | Market surveillance authority |  |  |
| 20 | ENISA single reporting platform |  |  |

Record the total and the distribution, not just the total.

**Total / 80:** ______ **Distribution** (count at each of 0,1,2,3,4): ______

When this table is filled, run `make terms-extract`. At W12 the procedure is
`make terms-sheet` — which writes the same twenty terms with the ratings
withheld — then fill it, **commit it**, then `make terms-compare`. Compare is
the only command that prints a W0 rating and it refuses to run until the W12
sheet is committed, so the claim that the second rating was made without
consulting the first is a matter of record rather than of memory.

## Part C — Competing-concept prose, fixed (~40 min) · second

M1 (W2) decides between the CRA track and a rival venture concept. Write both
concepts down **now**, before two weeks of reading the regulation makes one of
them feel obviously correct. Roughly 300 words each, in the present tense, and
do not edit after W1 begins.

For each concept: what the service is, who pays for it, why now, what I would
have to learn, what would make me abandon it.

### Concept 1 — CRA compliance consulting

_(write here)_

### Concept 2 — rival concept

_(write here)_

### Prior expectation, recorded before M1

Which do I expect to choose, and with what confidence (0–100%)? One sentence
on why. This is the quantity M1 is a test of.

_(write here)_

## Part A — Korean-language CRA content landscape (~40 min) · last

What exists in Korean, right now, before any of my own articles are published.
This is the baseline the article series is measured against.

For each search, record the query, the date, and what came back. Keep raw
counts even where they are noisy — the point is comparability with the same
searches repeated at W12, not precision.

Record the engine and any filters exactly as used. At W12 the same queries are
run again, and a comparison is only meaningful if the method was written down
rather than remembered.

| Query (Korean) | Engine | Date | Results, first 2 pages | Notes on quality |
|---|---|---|---|---|
| 사이버복원력법 | | | | |
| CRA 사이버보안 규정 | | | | |
| SBOM 작성 | | | | |
| 취약점 신고 의무 EU | | | | |
| CRA 자체평가 | | | | |

Also record: how many Korean-language practitioner articles (not news
reprints) exist on the CRA; which certification bodies have published Korean
CRA guidance; whether any Korean-language SBOM tutorial exists.

**The gap, in one sentence** — what a Korean-reading compliance officer cannot
currently get:

>

---

## Also fix before W1 — the `\REDACT{}` fields

The manuscript's conflict-of-interest disclosure needs three facts settled now,
because after twelve weeks "what I could do at the time" is already
contaminated:

1. **Employment and ownership.** Who employs whom; who owns what share of the
   venture; who benefits if M5 passes.
2. **Prior technical scope.** What the first author could already do on
   2026-08-02, stated concretely enough to be falsifiable (languages, tools,
   whether he had ever produced an SBOM, whether he had read the CRA).
3. **Who produced the planning documents.** The roadmap, the gate table, and
   this protocol — authored by whom, with what AI assistance.

## Before cutting the `w0` tag

- [ ] Parts B, C, A written, in that order
- [ ] The three `\REDACT{}` facts settled
- [ ] §3 decided: does the second author perform the gate adjudication? If not,
      delete §3 now — PROTOCOL.md §3 says so itself, so deleting it before W1
      is following the protocol, not changing your mind
- [ ] `make check` and `make validate` pass
- [ ] `make ots-audit` exits 0 — PROTOCOL.md §5.1 requires this before the tag
- [ ] commit, then `git tag w0`, then one more commit to carry that commit's
      OpenTimestamps proof
