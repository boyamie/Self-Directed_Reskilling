# Self-Directed Reskilling — contemporaneous field record

Twelve-week field record (3 Aug – 25 Oct 2026) of a solo practitioner
reskilling toward EU Cyber Resilience Act compliance work. This repository
holds the **data and the protocol**, not the manuscript.

The record is perishable: the weekly candidate-action log asks what options
were considered *at the time*, which cannot be reconstructed afterwards. That
is the reason the repository exists and the reason entries are dated and
append-only.

| | |
|---|---|
| Execution period | 2026-08-03 (W1) – 2026-10-25 (W12) |
| CRA reporting obligations | 2026-09-11 (W6) |
| Protocol | [`PROTOCOL.md`](PROTOCOL.md), frozen at tag `w0` |
| Manuscript | kept elsewhere — see *Manuscript separation* below |

## Layout

```
PROTOCOL.md                  frozen protocol; amendments append-only
docs/WEEK0_SNAPSHOT.md       the "before" measurement, due before W1
logs/candidate-actions/      W01..W12.toml — the four-field weekly form
logs/gates/                  M1..M5.toml  — second author's rulings
logs/journal/                daily entries, YYYY-MM-DD.md
tools/calog.py               validate / aggregate / export (no dependencies)
derived/                     generated; committed so the paper can cite a state
```

## Weekly routine (~5 min)

```bash
make week W=3        # create logs/candidate-actions/W03.toml from template
$EDITOR logs/candidate-actions/W03.toml
make validate        # schema + timing checks
make aggregate       # rebuild derived/ incl. the Principle 4 verdict
git commit -am "W03 candidate-action log"
```

Fill the form **before** taking the week's action. `make validate` warns when
`recorded_at` is more than two days after the week start, because a late entry
is a retrospective reconstruction and has to be reported as one.

## Setup

Python 3.11 or newer, no third-party packages.

```bash
git config core.hooksPath .githooks   # enables OpenTimestamps anchoring
make check                            # runs the tool's own tests
```

OpenTimestamps is optional; the hook is a no-op if `ots` is not installed.
Install with `pip install opentimestamps-client` — see `PROTOCOL.md` §5 for
why commit dates alone are not sufficient.

## Manuscript separation

The draft is **not** kept here. A public repository containing the manuscript
defeats double-anonymous review at any venue that uses it, and manuscript
revisions during review would interleave with the timing record. Keep the
manuscript in Overleaf or a private repository; this one holds only the record.

## Reuse

Protocol and logs: CC BY 4.0. `tools/`: MIT.
