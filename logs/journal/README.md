# Work journal — kept outside this repository

The journal itself is **not** here. It records cold outreach to named firms and
individuals who never agreed to be published, and the paper needs excerpts from
it, not the whole of it. It lives with the manuscript, at
`paper/CS/journal/` (W01–W12.md, `outreach-log.csv`, `artifact-log.md`).

What is here is `MANIFEST.tsv`: one SHA-256 per journal file, refreshed and
committed weekly. The commit hash is anchored by `.githooks/post-commit`
(PROTOCOL.md §5), so the manifest inherits a third-party timestamp.

```bash
make journal-manifest                              # default: ../paper/CS/journal
make journal-manifest JOURNAL=/path/to/journal     # elsewhere
git commit -m "W03 journal manifest" logs/journal/MANIFEST.tsv
```

## What this proves, and what it does not

**Proves.** That a journal file's bytes on the date of the commit were the
bytes hashed. At review time the full journal can be handed to an editor in
confidence; they recompute the hashes and compare against the manifest as it
stood in that week's commit. A file edited afterwards will not match, and a
file created afterwards will not appear in the earlier manifest at all.

**Does not prove.** That an entry is truthful, or that an excerpt quoted in the
paper is representative of the file it came from. The manifest is evidence
about timing only, and the paper should say so rather than let the presence of
hashes imply more.

## Consequence for how the journal is written

Refreshing the manifest rewrites the hash of every file that changed that week,
so revising an old day's entry is visible: the hash moves in a later manifest
while the earlier one still records the original. That is the intended
behaviour — corrections are fine, silent ones are not. When an entry is
revised, say so in the entry.

Hours stay machine-readable, so that the journal could be brought in-repo later
without reformatting, if each day opens with:

    hours: 1.5 | track: learning|market|assets
