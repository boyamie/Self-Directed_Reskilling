#!/usr/bin/env python3
"""The W0/W12 terminology pair. Python 3.11+, standard library only.

    tools/terms.py extract       read Part B of the snapshot -> derived/terms_w0.json
    tools/terms.py sheet         write logs/terms_w12.md, terms only, no ratings
    tools/terms.py compare       W0 vs W12, once the W12 sheet is committed

Exit codes: 0 fine, 1 the data is not ready, 2 wrong arguments or unreadable input.

Why `compare` refuses to run against an uncommitted sheet
---------------------------------------------------------
The snapshot asks for the W12 ratings to be made "without consulting this file
first". Nothing can stop someone opening docs/WEEK0_SNAPSHOT.md — it is in the
repository they are working in. What can be arranged is that the claim is
checkable rather than asserted: fill the blank sheet, commit it, and the commit
is anchored by .githooks/post-commit before any W0 value has been printed.
`compare` is the only command here that prints a W0 rating, and it will not run
until the W12 sheet is committed and unmodified. So the order of events is in
the record, not in a promise.

This does not prove the author did not peek. It proves the W12 numbers were
fixed before this tool showed them the W0 numbers, and that is the part a
reader can check.
"""

import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT = os.path.join(ROOT, "docs", "WEEK0_SNAPSHOT.md")
W0_JSON = os.path.join(ROOT, "derived", "terms_w0.json")
W12_SHEET = os.path.join(ROOT, "logs", "terms_w12.md")

N_TERMS = 20
HEADER_RE = re.compile(r"^\|\s*#\s*\|\s*Term\s*\|\s*Rating")
ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|(.*)$")


def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args),
                          capture_output=True, text=True)


def parse_table(path, require_ratings):
    """Pull the numbered term table out of a markdown file."""
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    start = next((i for i, l in enumerate(lines) if HEADER_RE.match(l)), None)
    if start is None:
        raise SystemExit("error: no term table found in %s" % path)

    rows = []
    for line in lines[start + 1:]:
        m = ROW_RE.match(line)
        if not m:
            if rows:
                break
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            raise SystemExit("error: %s: malformed row %r" % (path, line.strip()))
        num, term, rating = cells[0], cells[1], cells[2]
        gloss = cells[3] if len(cells) > 3 else ""
        entry = {"n": int(num), "term": term, "gloss": gloss}
        if rating == "":
            if require_ratings:
                entry["rating"] = None
            else:
                entry["rating"] = None
        else:
            if not re.fullmatch(r"[0-4]", rating):
                raise SystemExit("error: %s: term %s has rating %r; expected 0-4"
                                 % (path, num, rating))
            entry["rating"] = int(rating)
        rows.append(entry)

    if len(rows) != N_TERMS:
        raise SystemExit("error: %s: found %d terms, expected %d"
                         % (path, len(rows), N_TERMS))
    return rows


def unrated(rows):
    return [r["n"] for r in rows if r["rating"] is None]


def table_digest(rows):
    """Fingerprint of the Part B table as extracted: numbers, terms, ratings.

    Stored in the W0 record so that a later edit to the snapshot is detectable
    from the record itself, without depending on a freeze rule being enforced
    somewhere else.
    """
    canonical = "".join("%d\t%s\t%s\n" % (r["n"], r["term"], r["rating"])
                        for r in rows)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def cmd_extract(argv):
    # The W0 record is written once. Re-extracting after editing Part B would
    # rewrite it from the edited table, and because `compare` checks the W12
    # sheet against this file rather than against the original wording, a
    # changed term would launder itself: both sides would agree, and at W12
    # nobody remembers what term 20 used to say.
    if os.path.exists(W0_JSON):
        print("error: %s already exists and is the fixed W0 record.\n"
              "       Before w0: delete it deliberately and re-extract; the\n"
              "       change is then visible in git. After w0: do not -- record\n"
              "       the correction as a dated amendment in PROTOCOL.md 6."
              % os.path.relpath(W0_JSON, ROOT), file=sys.stderr)
        return 2

    rows = parse_table(SNAPSHOT, require_ratings=True)
    blank = unrated(rows)
    if blank:
        print("Part B is not filled in yet: %d of %d terms have no rating (%s)"
              % (len(blank), N_TERMS,
                 ", ".join(str(n) for n in blank[:8]) + ("..." if len(blank) > 8 else "")),
              file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(W0_JSON), exist_ok=True)
    with open(W0_JSON, "w", encoding="utf-8") as fh:
        json.dump({"terms": rows,
                   "total": sum(r["rating"] for r in rows),
                   "distribution": {str(k): sum(1 for r in rows if r["rating"] == k)
                                    for k in range(5)},
                   "source": os.path.relpath(SNAPSHOT, ROOT),
                   "source_table_sha256": table_digest(rows)},
                  fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("wrote %s -- %d terms, total %d/80"
          % (os.path.relpath(W0_JSON, ROOT), len(rows),
             sum(r["rating"] for r in rows)))
    return 0


def cmd_sheet(argv):
    if os.path.exists(W12_SHEET):
        print("error: %s already exists; refusing to overwrite it"
              % os.path.relpath(W12_SHEET, ROOT), file=sys.stderr)
        return 2
    rows = parse_table(SNAPSHOT, require_ratings=False)
    os.makedirs(os.path.dirname(W12_SHEET), exist_ok=True)
    body = [
        "# W12 terminology re-assessment",
        "",
        "The same twenty terms as Part B of the Week-0 snapshot, in the same",
        "order, with the ratings withheld. Rate these **without opening**",
        "`docs/WEEK0_SNAPSHOT.md`, on the identical scale:",
        "",
        "- **0** have not heard the term · **1** recognise it, could not define it",
        "- **2** could define it in a sentence · **3** could explain it to a client",
        "- **4** could produce or audit the artifact it names",
        "",
        "Then commit this file. `tools/terms.py compare` will not print a single",
        "W0 rating until it is committed, so the record shows these numbers were",
        "fixed before the earlier ones were back in view.",
        "",
        "| # | Term | Rating (0–4) | One line: what I think it means |",
        "|---|---|---|---|",
    ]
    for r in rows:
        body.append("| %d | %s | | |" % (r["n"], r["term"]))
    body += ["", "**Total / 80:** ______", ""]
    with open(W12_SHEET, "w", encoding="utf-8") as fh:
        fh.write("\n".join(body))
    print("wrote %s -- %d terms, no ratings"
          % (os.path.relpath(W12_SHEET, ROOT), len(rows)))
    return 0


def sheet_is_committed():
    rel = os.path.relpath(W12_SHEET, ROOT)
    if git("ls-files", "--error-unmatch", rel).returncode != 0:
        return False, "%s is not committed yet" % rel
    if git("diff", "--quiet", "HEAD", "--", rel).returncode != 0:
        return False, "%s has uncommitted changes" % rel
    return True, ""


def cmd_compare(argv):
    if not os.path.exists(W0_JSON):
        print("error: %s missing; run `tools/terms.py extract` first"
              % os.path.relpath(W0_JSON, ROOT), file=sys.stderr)
        return 1
    if not os.path.exists(W12_SHEET):
        print("error: %s missing; run `tools/terms.py sheet` first"
              % os.path.relpath(W12_SHEET, ROOT), file=sys.stderr)
        return 1

    w12 = parse_table(W12_SHEET, require_ratings=True)
    blank = unrated(w12)
    if blank:
        print("the W12 sheet is not finished: %d term(s) unrated (%s)"
              % (len(blank), ", ".join(str(n) for n in blank)), file=sys.stderr)
        return 1

    ok, why = sheet_is_committed()
    if not ok:
        print("refusing to print W0 ratings: %s.\n"
              "Commit the W12 sheet first -- the point of this check is that the\n"
              "W12 numbers are anchored before the W0 numbers are shown."
              % why, file=sys.stderr)
        return 1

    with open(W0_JSON, "r", encoding="utf-8") as fh:
        record = json.load(fh)
    w0 = {r["n"]: r for r in record["terms"]}

    # The snapshot must still say what it said when the W0 record was taken.
    # Checking the W12 sheet against the W0 record is not enough on its own:
    # both are generated from the snapshot, so an edit there followed by a
    # re-extract would agree with itself.
    stored = record.get("source_table_sha256")
    if stored:
        try:
            current = table_digest(parse_table(SNAPSHOT, require_ratings=True))
        except SystemExit as exc:
            print("error: cannot re-read Part B to check it is unchanged: %s"
                  % exc, file=sys.stderr)
            return 1
        if current != stored:
            print("refusing to compare: Part B of %s has changed since the W0\n"
                  "record was taken.\n"
                  "  recorded %s\n"
                  "  now      %s\n"
                  "The W0 record is the measurement; a snapshot edited after it\n"
                  "was taken means the two are no longer the same instrument.\n"
                  "Restore the snapshot from the w0 tag, or record what changed\n"
                  "as a dated amendment in PROTOCOL.md 6 and say so in the paper."
                  % (os.path.relpath(SNAPSHOT, ROOT), stored[:16], current[:16]),
                  file=sys.stderr)
            return 1

    print("%-3s %-44s %4s %4s %5s" % ("#", "term", "W0", "W12", "delta"))
    t0 = t12 = 0
    for r in w12:
        before = w0.get(r["n"])
        if before is None or before["term"] != r["term"]:
            print("error: term %d does not match the W0 list (%r vs %r)"
                  % (r["n"], before and before["term"], r["term"]), file=sys.stderr)
            return 2
        d = r["rating"] - before["rating"]
        t0 += before["rating"]
        t12 += r["rating"]
        print("%-3d %-44s %4d %4d %+5d"
              % (r["n"], r["term"][:44], before["rating"], r["rating"], d))
    print("\ntotal %d/80 -> %d/80 (%+d)" % (t0, t12, t12 - t0))
    for k in range(5):
        print("  rated %d: %2d -> %2d" % (k,
              sum(1 for r in w0.values() if r["rating"] == k),
              sum(1 for r in w12 if r["rating"] == k)))

    # A fall printed as a number alone reads as lost competence. Usually it is
    # the opposite: the W0 rating was confident about a different concept, and
    # the two glosses are the only place that shows it. They are the finding
    # for that term, so they belong in the output and not only in the JSON.
    fell = [(r, w0[r["n"]]) for r in w12 if r["rating"] < w0[r["n"]]["rating"]]
    if fell:
        print("\n%d rating(s) fell. Each is shown with both glosses, because a"
              % len(fell))
        print("negative delta cannot be read without them:\n")
        for r, before in fell:
            print("  %d. %s  %d -> %d (%+d)"
                  % (r["n"], r["term"], before["rating"], r["rating"],
                     r["rating"] - before["rating"]))
            print("     W0 : %s" % (before["gloss"] or "(none)"))
            print("     W12: %s" % (r["gloss"] or "(none)"))
        print("\nA term rated high at W0 on a mistaken reading falls once the\n"
              "author learns what it denotes. That is a result, not a loss, and\n"
              "the paper should report it as one.")
    sys.stdout.flush()
    print("\nA rating is a self-report at both ends. The pair measures what the\n"
          "author believes changed, which is not the same as what changed.",
          file=sys.stderr)
    return 0


COMMANDS = {"extract": cmd_extract, "sheet": cmd_sheet, "compare": cmd_compare}


def main(argv):
    if not argv or argv[0] not in COMMANDS:
        print(__doc__.strip())
        return 2
    return COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
