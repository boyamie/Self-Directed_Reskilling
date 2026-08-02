PY ?= python3

# The work journal is kept outside this repository; only its hash manifest is
# committed. See logs/journal/README.md.
JOURNAL ?= ../paper/CS/journal

.PHONY: help check validate aggregate export week snapshot ots-verify journal-manifest
help:
	@echo "make check             run the tool's self-tests"
	@echo "make validate          schema + timing checks over logs/"
	@echo "make aggregate         rebuild derived/ (Principle 4 verdict, gates, hours)"
	@echo "make export            LaTeX fragments into derived/"
	@echo "make week W=3          show the path of this week's log"
	@echo "make journal-manifest  re-hash the journal at JOURNAL=$(JOURNAL)"
	@echo "make ots-verify        verify OpenTimestamps proofs in derived/ots/"

check:
	@$(PY) tools/calog.py selftest

validate:
	@$(PY) tools/calog.py validate

aggregate: validate
	@$(PY) tools/calog.py aggregate

export: aggregate
	@$(PY) tools/calog.py export

week:
	@$(PY) tools/calog.py new-week $(W)

journal-manifest:
	@$(PY) tools/journal_manifest.py "$(JOURNAL)" --write

ots-verify:
	@command -v ots >/dev/null 2>&1 || { echo "ots not installed (pip install opentimestamps-client)"; exit 1; }
	@for f in derived/ots/*.ots; do echo "== $$f"; ots verify "$$f" || true; done
