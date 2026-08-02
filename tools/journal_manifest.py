#!/usr/bin/env python3
"""Hash manifest for the work journal, which is kept outside this repository.

    tools/journal_manifest.py <journal-dir> [--write]

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


def main(argv):
    if not argv:
        print(__doc__.strip())
        return 2
    journal_dir = os.path.expanduser(argv[0])
    write = "--write" in argv[1:]

    if not os.path.isdir(journal_dir):
        print("error: %s is not a directory" % journal_dir, file=sys.stderr)
        return 1

    rows = manifest(journal_dir)
    if not rows:
        print("error: no files found under %s" % journal_dir, file=sys.stderr)
        return 1

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
