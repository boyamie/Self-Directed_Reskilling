#!/usr/bin/env python3
"""Audit OpenTimestamps coverage against git history. No dependencies.

    tools/ots_audit.py [--rev RANGE]        default: HEAD

Exit codes:

    0   every commit but HEAD has a proof that binds to it
    1   a commit has no proof
    2   a proof exists but does not bind to its commit

2 is worse than 1 and is kept separate. A missing proof is a visible hole. A
proof that is present but does not bind -- wrong payload, edited payload,
truncated file -- looks like coverage in any listing that only checks whether
the file exists. Silent false coverage is the failure this repository can least
afford, so it fails the audit rather than warning.

Why this reads git history and not derived/ots/UNSTAMPED.txt: the ledger is
written by .githooks/post-commit, so it can only record failures the hook was
present to witness. Commits made where the hook never ran -- the GitHub web UI,
a fresh clone before `git config core.hooksPath .githooks`, CI -- leave no
entry at all. A worklist drawn from the ledger can never reach them. Coverage
has to be derived from the set of commits that exist, which is git's to answer.

HEAD is expected to have no proof: post-commit writes the proof after the
commit it belongs to, so it is carried by the next one. That is reported and
does not fail the audit.
"""

import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OTS_DIR = os.path.join(ROOT, "derived", "ots")
LEDGER = os.path.join(OTS_DIR, "UNSTAMPED.txt")

MAGIC = b"\x00OpenTimestamps\x00\x00Proof\x00\xbf\x89\xe2\xe8\x84\xe8\x92\x94"
OP_SHA256 = 0x08
# Attestation tags, used only to report whether a proof is still a calendar
# promise or has landed in a block. Not part of the pass/fail decision.
TAG_BITCOIN = b"\x05\x88\x96\x0d\x73\xd7\x19\x01"
TAG_PENDING = b"\x83\xdf\xe3\x0d\x2e\xf9\x0c\x8e"


def git(*args):
    out = subprocess.run(["git", "-C", ROOT] + list(args),
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), out.stderr.strip()))
    return out.stdout


def read_varint(buf, i):
    shift = value = 0
    while i < len(buf):
        byte = buf[i]
        i += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, i
        shift += 7
    raise ValueError("truncated varint")


def inspect(commit):
    """Return (state, detail) for one commit. state in anchored|missing|broken."""
    payload = os.path.join(OTS_DIR, commit + ".txt")
    proof = payload + ".ots"
    if not os.path.exists(proof):
        return "missing", "no proof file"
    if not os.path.exists(payload):
        # The proof alone cannot be checked: what it commits to is the payload,
        # and without it there is nothing to show the digest belongs to this
        # commit rather than to any other file.
        return "broken", "proof present but payload %s.txt is gone" % commit[:8]

    with open(payload, "rb") as fh:
        payload_bytes = fh.read()
    if payload_bytes.decode("utf-8", "replace").strip() != commit:
        return "broken", "payload does not contain this commit hash"

    with open(proof, "rb") as fh:
        raw = fh.read()
    if not raw.startswith(MAGIC):
        return "broken", "not an OpenTimestamps proof (bad magic)"
    i = len(MAGIC)
    try:
        _version, i = read_varint(raw, i)
        if i >= len(raw) or raw[i] != OP_SHA256:
            return "broken", "unexpected digest algorithm"
        i += 1
        embedded = raw[i:i + 32]
        if len(embedded) != 32:
            return "broken", "truncated before the digest"
    except ValueError as exc:
        return "broken", str(exc)

    actual = hashlib.sha256(payload_bytes).digest()
    if embedded != actual:
        return "broken", "proof commits to a different file"

    confirmed = raw.count(TAG_BITCOIN)
    pending = raw.count(TAG_PENDING)
    if confirmed:
        return "anchored", "%d bitcoin attestation(s)" % confirmed
    return "anchored", "pending, %d calendar(s); run make ots-upgrade" % pending


def late_commits():
    """Hashes the hook recorded as unstamped, i.e. anchored after the fact."""
    if not os.path.exists(LEDGER):
        return set()
    out = set()
    with open(LEDGER, "r", encoding="utf-8") as fh:
        for line in fh:
            h = line.split("\t")[0].strip()
            if h:
                out.add(h)
    return out


def main(argv):
    rev = "HEAD"
    if argv:
        if argv[0] == "--rev" and len(argv) > 1:
            rev = argv[1]
        else:
            print(__doc__.strip())
            return 2

    commits = git("rev-list", rev).split()
    if not commits:
        print("no commits in %s" % rev, file=sys.stderr)
        return 2
    head = commits[0]
    late = late_commits()

    missing, broken, anchored = [], [], 0
    for commit in commits:
        state, detail = inspect(commit)
        subject = git("log", "-1", "--format=%s", commit).strip()[:44]
        mark = " (stamped late)" if commit in late else ""
        if state == "anchored":
            anchored += 1
            print("ok      %s  %s%s  [%s]" % (commit[:8], subject, mark, detail))
        elif state == "missing":
            if commit == head:
                print("head    %s  %s  [proof lands in the next commit]"
                      % (commit[:8], subject))
            else:
                missing.append(commit)
                print("MISSING %s  %s  %s" % (commit[:8], subject, detail))
        else:
            broken.append(commit)
            print("BROKEN  %s  %s  %s" % (commit[:8], subject, detail))

    print("\n%d commit(s): %d anchored, %d missing, %d broken"
          % (len(commits), anchored, len(missing), len(broken)))
    if late:
        print("%d of the anchored proofs were made after the fact; a late stamp\n"
              "bounds its commit from above only." % len(late & set(commits)))

    # stdout is block-buffered when not a terminal; stderr never is. Without
    # this the summary below prints above the listing it summarises.
    sys.stdout.flush()
    if broken:
        print("\nA proof that does not bind is worse than no proof: it counts as\n"
              "coverage in any check that only looks for the file. Delete the bad\n"
              "proof and re-stamp with `make ots-backfill`.", file=sys.stderr)
        return 2
    if missing:
        print("\n%d commit(s) have no proof. `make ots-backfill` stamps them, late."
              % len(missing), file=sys.stderr)
        return 1
    print("OK -- every commit before HEAD is anchored.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
