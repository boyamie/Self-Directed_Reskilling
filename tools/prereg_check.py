#!/usr/bin/env python3
"""Check docs/PREREGISTRATION.md against PROTOCOL.md. No dependencies.

    tools/prereg_check.py            report drift
    tools/prereg_check.py --filing   also require every [FILL] to be resolved

Exit 0 consistent, 1 drift or unresolved placeholders, 2 a file is missing.

The registration restates the protocol for a registry. Once filed it cannot be
quietly corrected, so the two documents drifting apart is not a formatting
problem: it means the public record of the study says something the study does
not do. This compares the things that must be identical -- dates, the decision
rule, the gate table, and whether the adjudication control exists at all --
rather than comparing prose, which is expected to differ.

The check that matters most is the last one. PROTOCOL.md 3 instructs that the
adjudication section be deleted before w0 if the second author does not agree
to perform it. If that deletion happens and the registration still carries the
section, the study has registered a control it does not operate, and a
registration can only be withdrawn, not amended away. Presence is matched on
the marker `<!-- inv:adjudication -->` in both files, not on wording, so
rewording either one cannot make the check pass by accident.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOCOL = os.path.join(ROOT, "PROTOCOL.md")
PREREG = os.path.join(ROOT, "docs", "PREREGISTRATION.md")

MARKER = "<!-- inv:adjudication -->"
FILL_RE = re.compile(r"\[FILL[^\]]*\]")

# Dates that carry meaning. Written here as well so that an edit to both
# documents at once still has to get past a third place.
EXECUTION = ["2026-08-03", "2026-10-25"]
GATES = ["2026-08-16", "2026-08-30", "2026-09-11", "2026-10-04", "2026-10-25"]
OBLIGATIONS = "2026-09-11"

# Tokens of the decision rule. Prose may differ; these may not go missing.
RULE_TOKENS = ["outside_set", "in_set", "uncertain"]


def read(path):
    if not os.path.exists(path):
        print("error: %s is missing" % os.path.relpath(path, ROOT), file=sys.stderr)
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def dates_in(text):
    return set(re.findall(r"\b20\d\d-\d\d-\d\d\b", text))


def main(argv):
    for a in argv:
        if a != "--filing":
            print(__doc__.strip())
            return 2
    filing = "--filing" in argv

    proto, prereg = read(PROTOCOL), read(PREREG)
    if proto is None or prereg is None:
        return 2

    problems = []
    p_dates, r_dates = dates_in(proto), dates_in(prereg)

    for d in EXECUTION:
        if d not in p_dates:
            problems.append("execution date %s is not in PROTOCOL.md" % d)
        if d not in r_dates:
            problems.append("execution date %s is not in the registration" % d)
    for d in GATES:
        if d not in p_dates:
            problems.append("gate date %s is not in PROTOCOL.md" % d)
        if d not in r_dates:
            problems.append("gate date %s is not in the registration" % d)
    if OBLIGATIONS not in r_dates:
        problems.append("the reporting-obligations date %s is not in the "
                        "registration" % OBLIGATIONS)

    for token in RULE_TOKENS:
        if token not in proto:
            problems.append("decision-rule term %r is not in PROTOCOL.md" % token)
        if token not in prereg:
            problems.append("decision-rule term %r is not in the registration" % token)

    # "At least two weeks" is the threshold; if one document loosens it the
    # other must too, and neither may state a different number.
    if not re.search(r"n_support >= 2|at least two weeks", proto):
        problems.append("PROTOCOL.md no longer states the support threshold")
    if not re.search(r"[Aa]t least two weeks", prereg):
        problems.append("the registration no longer states the support threshold")

    # The one that cannot be allowed to pass silently.
    in_proto = MARKER in proto
    in_prereg = MARKER in prereg
    if in_proto != in_prereg:
        if in_prereg:
            problems.append(
                "the registration carries the adjudication section but "
                "PROTOCOL.md no longer does. Registering a control that is not "
                "operated is the failure PROTOCOL.md 3 warns about, and a filed "
                "registration can only be withdrawn. Delete section 8 of the "
                "registration before filing.")
        else:
            problems.append(
                "PROTOCOL.md has the adjudication section but the registration "
                "does not. The registry record would omit the control that "
                "handles the conflict of interest.")

    fills = FILL_RE.findall(prereg)
    if filing and fills:
        problems.append("%d unresolved placeholder(s) in the registration: %s"
                        % (len(fills), "; ".join(f[:48] for f in fills[:4])))

    for p in problems:
        print("drift: %s" % p)
    sys.stdout.flush()

    if not filing and fills:
        print("\n%d placeholder(s) still to fill before filing; run with "
              "--filing to require them." % len(fills), file=sys.stderr)
    if problems:
        print("\n%d problem(s)." % len(problems), file=sys.stderr)
        return 1
    print("registration and protocol agree on dates, decision rule, gates, and "
          "the adjudication control.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
