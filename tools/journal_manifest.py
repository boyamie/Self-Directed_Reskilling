#!/usr/bin/env python3
"""Hash manifest for the work journal, which is kept outside this repository.

    tools/journal_manifest.py <journal-dir>            print the manifest
    tools/journal_manifest.py <journal-dir> --write    update MANIFEST.tsv
    tools/journal_manifest.py <journal-dir> --verify   check against MANIFEST.tsv

Exit codes:

    0   verified: every recorded file still hashes to its recorded value
    1   mismatch: a recorded file changed or is gone
    2   the manifest could not be read, or the arguments are unusable

2 is kept separate from 1 deliberately. Failing to read the manifest is an
operational mistake -- wrong path, truncated file, edited by hand -- and says
nothing about the journal. An editor checking the record must not be able to
confuse "I ran this wrong" with "the journal does not match".

The journal records cold outreach to named firms and individuals who never
agreed to be published, so its text stays private. What this repository needs
from it is narrower: evidence that a given day's entry said what it says, on
the date claimed, rather than having been written afterwards.

A SHA-256 per file gives exactly that and nothing more. The manifest is
committed weekly; the commit hash is anchored by .githooks/post-commit
(PROTOCOL.md section 5). At review time the full journal can be handed to an
editor, who recomputes the hashes and checks them against the manifest as it
stood in the commit for that week. A file altered after the fact will not
match.

What this does NOT prove: that the entry is truthful, or that an excerpt
quoted in the paper is representative. It proves only that the bytes are the
bytes that existed then.
"""

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "logs", "journal", "MANIFEST.tsv")

HEADER = "file\tbytes\tsha256\n"

# Deliberately omitted: mtime. File timestamps are set by the writing machine
# and are no more third-party evidence than commit dates are (PROTOCOL.md 5).


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest(journal_dir):
    rows = []
    for dirpath, dirnames, filenames in os.walk(journal_dir):
        dirnames[:] = [d for d in sorted(dirnames) if not d.startswith(".")]
        for name in sorted(filenames):
            if name.startswith(".") or name == "MANIFEST.tsv":
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, journal_dir)
            rows.append((rel, os.path.getsize(full), digest(full)))
    return rows


class ManifestError(Exception):
    """The manifest could not be read. Distinct from a verification failure."""


def read_manifest(path):
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    if not lines or lines[0] != HEADER.rstrip("\n"):
        raise ManifestError("%s: bad header, expected %r"
                            % (path, HEADER.rstrip("\n")))
    rows = []
    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            raise ManifestError("%s:%d: expected 3 tab-separated fields, got %d"
                                % (path, lineno, len(parts)))
        name, size, sha = parts
        try:
            size = int(size)
        except ValueError:
            raise ManifestError("%s:%d: bytes field %r is not an integer"
                                % (path, lineno, size))
        rows.append((name, size, sha))
    return rows


def cmd_verify(journal_dir):
    """Recompute hashes and compare against the committed manifest.

    Scope: every file the manifest records must still hash to the recorded
    value. Files present on disk but absent from the manifest are reported and
    do not fail — during the study a manifest is always older than the journal,
    so new entries after it was written are the normal case, not tampering.
    """
    if not os.path.exists(OUT):
        print("error: no manifest at %s\n"
              "       nothing has been recorded yet; run `make journal-manifest`"
              % os.path.relpath(OUT, ROOT), file=sys.stderr)
        return 2
    try:
        recorded = read_manifest(OUT)
    except (ManifestError, OSError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    on_disk = {name: (size, sha) for name, size, sha in manifest(journal_dir)}
    changed, missing, matched = [], [], 0
    for name, size, sha in recorded:
        actual = on_disk.get(name)
        if actual is None:
            missing.append(name)
        elif actual[1] != sha:
            changed.append((name, sha, actual[1]))
        else:
            matched += 1

    extra = sorted(set(on_disk) - {r[0] for r in recorded})

    for name, want, got in changed:
        print("CHANGED %s\n  manifest %s\n  on disk  %s" % (name, want, got))
    for name in missing:
        print("MISSING %s" % name)
    for name in extra:
        print("not in manifest (ignored) %s" % name)

    print("\n%d recorded, %d matched, %d changed, %d missing"
          % (len(recorded), matched, len(changed), len(missing)))
    if changed or missing:
        # stdout is block-buffered when piped while stderr is not, so without
        # this the explanation prints above the findings it explains.
        sys.stdout.flush()
        # Say what this does and does not mean, so the reader does not take a
        # mismatch for dishonesty. Journal entries may be legitimately revised;
        # the manifest exists to make revision visible, not to forbid it.
        print("\nA mismatch shows the bytes differ from the ones recorded when\n"
              "this manifest was committed. That is what an edit after the fact\n"
              "looks like -- and also what a disclosed correction looks like.\n"
              "Compare against the manifest in the commit for the week in\n"
              "question before drawing a conclusion.", file=sys.stderr)
        return 1
    print("OK -- every recorded file still hashes to its recorded value.")
    return 0


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    journal_dir = os.path.expanduser(argv[0])
    flags = argv[1:]
    write = "--write" in flags

    if not os.path.isdir(journal_dir):
        print("error: %s is not a directory" % journal_dir, file=sys.stderr)
        return 2

    if "--verify" in flags:
        return cmd_verify(journal_dir)

    rows = manifest(journal_dir)
    if not rows:
        print("error: no files found under %s" % journal_dir, file=sys.stderr)
        return 2

    body = HEADER + "".join("%s\t%d\t%s\n" % r for r in rows)
    if write:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as fh:
            fh.write(body)
        print("wrote %s -- %d file(s)" % (os.path.relpath(OUT, ROOT), len(rows)))
    else:
        sys.stdout.write(body)
        print("\n%d file(s); re-run with --write to update the manifest"
              % len(rows), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
