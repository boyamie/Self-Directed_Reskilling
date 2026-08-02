# Preregistration — AI-assisted self-directed reskilling toward EU CRA compliance consulting

Text for deposit in a public registry. It restates `PROTOCOL.md` and adds no
claim that is not already there; where the two differ, `PROTOCOL.md` governs and
`make prereg-check` reports the drift.

| | |
|---|---|
| Content fixed at | tag `w0`, `[FILL: w0 tag date]`, commit `[FILL: w0 tag commit hash]` |
| Registration filed | `[FILL: registration submitted on YYYY-MM-DD]` |
| Registry record | `[FILL: registry URL, added after submission]` |
| Repository | https://github.com/boyamie/Self-Directed_Reskilling |
| Archived release | `[FILL: Zenodo DOI for the w0 release]` |

**The two dates above are different and that is not incidental.** The content
was fixed before the execution period began; the filing is later. This study
does **not** claim to have been registered before 3 August 2026. Readers who
want evidence about when the content was fixed should use the OpenTimestamps
proofs and the archived release, not the filing date.

## 1. Study information

Analytic autoethnography of a twelve-week, self-designed reskilling program
undertaken by the first author to enter EU Cyber Resilience Act (CRA)
compliance consulting. Execution period **2026-08-03 – 2026-10-25** (W1–W12).
The CRA's reporting obligations take effect **2026-09-11**, inside W6.

One participant, who is also the first author. There is no sample, no control
condition, and no claim of generalisability. What is registered here is the
procedure and the decision rules, so that the analysis cannot be selected after
the data are in view.

## 2. Research questions

- **RQ1.** How can a solo professional structure self-directed reskilling when
  the target expertise is anchored to a fixed regulatory calendar and resources
  are severely constrained?
- **RQ2a.** What role does an external statutory deadline play in sequencing,
  pacing, and market legitimacy?
- **RQ2b.** What role do public learning artifacts play in the absence of a
  community of practice?
- **RQ2c.** Does generative AI assistance change the learner's opportunity set
  — which goals are considered worth pursuing — or only the speed at which
  goals already in that set are reached?

RQ2c is the only question with a prespecified quantitative decision rule
(§5). The others are answered interpretively from the journal and the artifact
record, and are reported as such.

## 3. Design

Analytic autoethnography. Five design principles are fixed before execution and
traced through it: backward design from regulatory dates; interleaving learning
with market contact; artifact-first learning; generative AI as a possible
change to the opportunity set; and pre-specified gates with pre-committed
failure responses.

## 4. Data collected

1. **Candidate-action log.** `logs/candidate-actions/W01–W12.toml`. Recorded at
   the start of each week, before that week's action is taken.
2. **Gate adjudications.** `logs/gates/M1–M5.toml`.
3. **Work journal.** Daily entries, kept outside the public repository because
   they name people and firms who did not consent to publication. A SHA-256
   manifest is committed weekly so that the entries can be verified against the
   record without being published.
4. **Week-0 snapshot.** `docs/WEEK0_SNAPSHOT.md`: the Korean-language CRA
   content landscape, a twenty-term self-assessment, and two competing venture
   concepts with a prior expectation, all recorded before W1.
5. **Public artifacts.** SBOMs, articles, and tools, with publication dates.

## 5. Analysis plan for RQ2c, fixed in advance

Each week the full set of candidate actions considered is enumerated, with, for
each: whether the option was generated, surfaced, or made tractable with AI
assistance (`yes` / `no` / `partly`, with one sentence of detail); and whether
the action would have been inside the opportunity set the first author would
have considered unaided (`in_set` / `outside_set` / `uncertain`). The action
selected and the rationale at the time of selection are recorded with it.

- **Support.** At least two weeks whose *selected* action is `outside_set` and
  AI-assisted (`yes` or `partly`).
- **Refutation.** Every selected action across W1–W12 is AI-assisted and
  uniformly `in_set` — AI executed faster inside an opportunity set it did not
  change.
- **Indeterminate.** Any other pattern, including one dominated by `uncertain`.
  Reported as indeterminate and not as support.

Both clauses are evaluated over *selected* actions only. Counts over the full
candidate set are reported alongside as a secondary descriptive and are not
used for the decision: evaluated that way, a single unselected `outside_set`
candidate in any week would make refutation unreachable by construction.

The rule is implemented once, in `tools/calog.py`, and the verdict is whatever
that program writes to `derived/principle4.json`.

The opportunity-set judgement is a prospective self-report and is reported as
one. It establishes that the opportunity set changed, not that AI caused the
change.

## 6. Secondary measure: terminology self-assessment

Twenty CRA terms, fixed before W1, rated 0–4 with a one-line gloss at W0 and
again at W12. The W12 rating is made from a sheet carrying the terms without
the earlier ratings, and the comparison tool refuses to display any W0 rating
until the W12 sheet is committed. Both ratings are self-reports and measure
believed change. Ratings that fall are reported with both glosses, since a fall
usually indicates the earlier rating was confident about a different concept.

## 7. Gates, fixed in advance

| Gate | Date | Week | Pass criterion | Pre-committed response if not met |
|---|---|---|---|---|
| M1 | 2026-08-16 | W2 | Track confirmed after two weeks of reading the regulation | Send ten outreach letters per candidate track; let market response decide |
| M2 | 2026-08-30 | W4 | SBOM generated and published for own product | Extend two weeks and retry; if still blocked, abandon the CRA track for the rival concept |
| M3 | 2026-09-11 | W6 | Five articles published and twenty outreach letters sent on the day the reporting obligations take effect | If a majority of prospects signal compliance is already handled, retarget to smaller firms |
| M4 | 2026-10-04 | W9 | One free pilot diagnosis delivered | If none of twenty letters converts, switch to referrals via certification bodies |
| M5 | 2026-10-25 | W12 | GO: two paid engagements closed | Redesign price and targeting once and retry; if still zero, pivot to public-sector SBOM work; content, skills and list are retained as assets |

Outcomes are reported for all five gates whether or not they pass, and the
pre-committed response is what is followed.

## 8. Adjudication and conflict of interest
<!-- inv:adjudication -->

Second author performs the adjudication: `[FILL: yes / no — if no, delete this
section and register the absence of an adjudication control as a limitation]`

The first author owns the venture whose survival M5 tests and benefits
materially if it passes. Pass or fail at each gate is therefore adjudicated by
the second author, not the first, within 48 hours of the gate date, against the
criterion as fixed above. The first author supplies the evidence; the second
author rules. Where the second author judges a criterion to have been met only
under a reading looser than the wording above, the gate is recorded as failed
and the pre-committed response is triggered. Any disagreement is reported
verbatim.

Registering an adjudication control and then not performing it would be worse
than not having one, and a registration cannot be quietly withdrawn. If the
second author does not agree to adjudicate, this section is deleted before
filing rather than after.

## 9. Timing evidence

Git commit dates are set by the committing machine and are not third-party
evidence. Each commit hash is anchored with OpenTimestamps, coverage is audited
against git history rather than against a log of failures, and the repository is
archived with a DOI at `w0` and after W12. Anchors made after the fact are
recorded as such and bound their commit from above only.

## 10. Known limitations, registered rather than discovered later

- One participant, who is also the analyst and the interested party.
- The opportunity-set field is a self-report about a counterfactual.
- The terminology pair measures believed competence at both ends.
- The registration is filed after the content was fixed and after the execution
  period begins; see the header.
- The journal is not public, so its contents are verifiable by hash but not by
  inspection.
