# macOS ships /usr/bin/python3 as 3.9, which has no tomllib, so a bare
# `python3` is not safe to assume. Pick the first interpreter that can
# actually run the tool. Override with `make PY=/path/to/python3`.
PY ?= $(shell for p in python3 python3.13 python3.12 python3.11; do \
	  command -v $$p >/dev/null 2>&1 && $$p -c 'import tomllib' >/dev/null 2>&1 \
	    && { echo $$p; break; }; done)

ifeq ($(strip $(PY)),)
$(error no python3 with tomllib found -- need 3.11 or newer. Install one, or run: make PY=/path/to/python3)
endif

# The work journal is kept outside this repository; only its hash manifest is
# committed (logs/journal/README.md). Where it sits relative to here depends on
# where this repository was cloned, so probe the sensible siblings rather than
# hard-coding one clone's layout. Override with `make journal-manifest
# JOURNAL=/path/to/journal`.
JOURNAL ?= $(firstword $(wildcard ../journal ../paper/CS/journal ../../paper/CS/journal))

.PHONY: help check validate aggregate export week snapshot ots-verify ots-backfill journal-manifest
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
	@test -n "$(JOURNAL)" || { echo "journal directory not found next to this clone."; \
	  echo "run: make journal-manifest JOURNAL=/path/to/journal"; exit 1; }
	@$(PY) tools/journal_manifest.py "$(JOURNAL)" --write

ots-verify:
	@command -v ots >/dev/null 2>&1 || { echo "ots not installed (pip install opentimestamps-client)"; exit 1; }
	@for f in derived/ots/*.ots; do echo "== $$f"; ots verify "$$f" || true; done

# Stamps commits the hook could not stamp (derived/ots/UNSTAMPED.txt).
# UNSTAMPED.txt is deliberately not cleared: a late stamp proves the commit
# existed by the time it was stamped, not by its commit date, and the paper
# should be able to say which proofs are late and by how much.
ots-backfill:
	@command -v ots >/dev/null 2>&1 || { echo "ots not installed (pip install opentimestamps-client)"; exit 1; }
	@test -s derived/ots/UNSTAMPED.txt || { echo "no unstamped commits recorded"; exit 0; }
	@cut -f1 derived/ots/UNSTAMPED.txt | sort -u | while read h; do \
	  test -f "derived/ots/$$h.ots" && continue; \
	  printf '%s\n' "$$h" > "derived/ots/$$h.txt"; \
	  if ots stamp "derived/ots/$$h.txt" >/dev/null 2>&1; then echo "stamped $$h (late)"; \
	  else rm -f "derived/ots/$$h.txt"; echo "FAILED  $$h"; fi; \
	done
	@echo "note: a late stamp bounds the commit from above only -- it proves the"
	@echo "      hash existed by the stamping time, not by the commit date."
