# Protocol — frozen before the execution period

**Status.** This document is fixed before 3 August 2026 (W1) and is not edited
during the execution period (3 Aug – 25 Oct 2026). Corrections after the start
of W1 are made by appending a dated amendment to §6, never by rewriting the
text above it. The state of this file at tag `w0` is the version referred to in
the paper.

**Scope.** This is a protocol document, not a preregistration. No registry
timestamp exists; third-party timing evidence comes from the mechanism in §5.

---

## 1. Study

Analytic autoethnography of a twelve-week, self-designed reskilling program
undertaken by the first author to enter EU Cyber Resilience Act (CRA)
compliance consulting. Execution period 3 August – 25 October 2026 (W1–W12).
The CRA's reporting obligations take effect 11 September 2026, which falls in
W6.

## 2. Instrument — Candidate-action log (for Principle 4)

Recorded at the start of each week (W1–W12) and at each gate, **before the
action is taken**, in a fixed four-field form:

  (a) Candidate actions considered this week — the full set, enumerated.
  (b) For each: was the option generated, surfaced, or made tractable with
      AI assistance? [yes / no / partly — with one sentence of detail]
  (c) Action selected, and the rationale at the time of selection.
  (d) Feasibility judgement without AI assistance: would this action have been
      inside the opportunity set the author would have considered on his own?
      [in set / outside set / uncertain]

Principle 4 is supported only if selected actions recur that are recorded (d)
"outside set" with (b) yes/partly. It is treated as refuted if AI assistance
appears throughout field (b) while field (d) is uniformly "in set" — i.e. AI
executed faster within an opportunity set it did not change. Field (d) is a
prospective self-report and is reported as such; it establishes that the
opportunity set changed, not that AI caused the change.

### 2.1 Decision rule, stated operationally

Fixed here so that the rule cannot be chosen after seeing the data.

- **Support.** `n_support` = number of weeks whose *selected* action has
  (d) = `outside_set` and (b) ∈ {`yes`, `partly`}. "Recur" is read as
  `n_support >= 2`.
- **Refutation.** Every *selected* action across W1–W12 has (b) ∈ {`yes`,
  `partly`} **and** (d) = `in_set` for all of them.
- **Indeterminate.** Any other pattern, including one dominated by
  `uncertain`. Reported as indeterminate; not reported as support.

The refutation clause is evaluated over *selected* actions only, matching the
support clause. The same counts over the full candidate set are reported
alongside as a secondary descriptive, and are not used for the decision.

`tools/calog.py aggregate` computes all three and writes the verdict to
`derived/principle4.json`. The verdict is whatever the tool computes.

## 3. Instrument — Gate adjudication

Pass or fail at each gate is adjudicated by the second author, not the first,
and is recorded within 48 hours of the gate date on the criterion as fixed in
this protocol before the execution period began. The first author supplies the
evidence; the second author rules. Where the second author judges a criterion
to have been met only under a reading looser than the protocol wording, the
gate is recorded as failed and the pre-committed failure response is triggered.
Any disagreement is reported verbatim in the paper.

### 3.1 Gates as fixed

| Gate | Date | Week | Pass criterion | Pre-committed response if not met |
|---|---|---|---|---|
| M1 | 2026-08-16 | W2 | Track confirmed after two weeks of reading the regulation | Send ten outreach letters per candidate track; let market response decide |
| M2 | 2026-08-30 | W4 | SBOM generated and published for own product | Extend two weeks and retry; if still blocked, abandon the CRA track for the rival concept |
| M3 | 2026-09-11 | W6 | Five articles published and twenty outreach letters sent on the day the reporting obligations take effect | If a majority of prospects signal compliance is already handled, retarget to smaller firms |
| M4 | 2026-10-04 | W9 | One free pilot diagnosis delivered | If none of twenty letters converts, switch to referrals via certification bodies |
| M5 | 2026-10-25 | W12 | GO: two paid engagements closed | Redesign price and targeting once and retry; if still zero, pivot to public-sector SBOM work; content, skills and list are retained as assets |

**Condition of inclusion.** §3 applies only if the second author has agreed to
perform the adjudication. Writing it and not performing it is worse than not
writing it. If the second author declines, delete §3 at `w0` and record the
absence of an adjudication control as a limitation.

## 4. Conflict of interest

The first author owns the venture whose survival M5 tests and benefits
materially from its success. The adjudication rule in §3 exists to control
this. The repository is held by the second author, so the timing record in §5
is not under the sole control of the interested party.

## 5. Timing evidence

Git author and committer dates are set by the committing machine and can be
set to any value; they are not third-party evidence of when a commit was made.
Two mechanisms are used instead:

1. **OpenTimestamps.** `.githooks/post-commit` anchors each commit hash. The
   `.ots` proofs are committed under `derived/ots/`. Free, permanent,
   independently verifiable.
2. **Zenodo.** A release is cut at `w0` and after W12; the deposit date is
   recorded by a third party and a DOI is issued.

GitHub's public push-event feed is not relied on: it is retained for
approximately 90 days and W1 events will be gone before peer review.

### 5.1 Coverage is audited, not assumed

The hook in mechanism 1 runs only where it is installed. `core.hooksPath` is
local configuration and is not carried by a clone, so a commit made through the
GitHub web interface, from a fresh clone, or by CI is not anchored and leaves
no record of not having been. A ledger written by the hook cannot report gaps
the hook was absent for.

Coverage is therefore derived from `git rev-list`, by `tools/ots_audit.py`, and
every commit is required to have a proof that binds to it: the payload contains
that commit's hash and the proof commits to that payload. A proof that is
present but does not bind fails the audit rather than warning, because in any
check that only looks for the file it counts as coverage while providing none.

`make ots-audit` must exit 0 before the `w0` tag is cut and before the release
after W12. That is the operational definition of "the record up to this point
is anchored".

Anchors made after the fact are recorded as such in `derived/ots/UNSTAMPED.txt`
and reported by the audit. A late anchor bounds its commit from above only: it
shows the hash existed by the time it was stamped, not that it existed at the
commit date. The paper reports the audit as it stands, including which proofs
are late and which commits were anchored only in retrospect.

## 6. Amendments

Append-only. Each entry: date, section touched, what changed, why.

_(none yet)_
