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

.PHONY: help check validate aggregate export week snapshot \
        ots-verify ots-upgrade ots-audit ots-backfill journal-manifest journal-verify \
        terms-extract terms-sheet terms-compare prereg-check
help:
	@echo "make check             run the tool's self-tests"
	@echo "make validate          schema + timing checks over logs/"
	@echo "make aggregate         rebuild derived/ (Principle 4 verdict, gates, hours)"
	@echo "make export            LaTeX fragments into derived/"
	@echo "make week W=3          show the path of this week's log"
	@echo "make terms-extract     Part B ratings -> derived/terms_w0.json"
	@echo "make terms-sheet       W12: blank sheet, same terms, no ratings"
	@echo "make terms-compare     W12 vs W0 (needs the W12 sheet committed)"
	@echo "make journal-manifest  re-hash the journal at JOURNAL=$(JOURNAL)"
	@echo "make journal-verify    check the journal against the committed manifest"
	@echo "make ots-verify        verify OpenTimestamps proofs in derived/ots/"
	@echo "make ots-upgrade       complete pending proofs once Bitcoin confirms"
	@echo "make ots-audit         check every commit in history has a bound proof"
	@echo "make prereg-check      registration vs protocol drift (--filing before you file)"

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

# The W0/W12 terminology pair. terms-compare is the only one that prints a W0
# rating, and it refuses until logs/terms_w12.md is committed -- so "rated
# without consulting the W0 file" is in the record rather than asserted.
terms-extract:
	@$(PY) tools/terms.py extract

terms-sheet:
	@$(PY) tools/terms.py sheet

terms-compare:
	@$(PY) tools/terms.py compare

journal-manifest:
	@test -n "$(JOURNAL)" || { echo "journal directory not found next to this clone."; \
	  echo "run: make journal-manifest JOURNAL=/path/to/journal"; exit 1; }
	@$(PY) tools/journal_manifest.py "$(JOURNAL)" --write

# Author's weekly check. NOT for a reader auditing the record: make returns 2
# for any recipe failure, so a mismatch (1) and an unreadable manifest (2)
# arrive here indistinguishable, and telling them apart is the whole point.
# The reader's procedure calls tools/journal_manifest.py directly and passes
# --manifest; see logs/journal/README.md.
journal-verify:
	@test -n "$(JOURNAL)" || { echo "journal directory not found next to this clone."; \
	  echo "run: make journal-verify JOURNAL=/path/to/journal"; exit 2; }
	@$(PY) tools/journal_manifest.py "$(JOURNAL)" --verify

ots-verify:
	@command -v ots >/dev/null 2>&1 || { echo "ots not installed (pipx install opentimestamps-client)"; exit 1; }
	@for f in derived/ots/*.ots; do echo "== $$f"; ots verify "$$f" || true; done

# A fresh stamp is a calendar promise, not yet a Bitcoin proof. Once the
# calendars land in a block -- hours to a day -- this rewrites the .ots files
# with the block attestation, which is what makes them verifiable by anyone
# without contacting the calendar servers. Run it, then commit the result.
ots-upgrade:
	@command -v ots >/dev/null 2>&1 || { echo "ots not installed (pipx install opentimestamps-client)"; exit 1; }
	@ls derived/ots/*.ots >/dev/null 2>&1 || { echo "no proofs yet"; exit 0; }
	@ots upgrade derived/ots/*.ots 2>&1 | grep -v "^Got 1 attestation" || true
	@rm -f derived/ots/*.ots.bak
	@echo "upgraded proofs still pending are left as they are; re-run tomorrow"

# Coverage is derived from git history, not from derived/ots/UNSTAMPED.txt.
# The ledger is written by the post-commit hook, so it only knows the failures
# the hook was there to see; a commit made through the GitHub web UI, or from a
# clone where core.hooksPath was never set, leaves no entry and would never
# appear in a worklist built from it. See tools/ots_audit.py.
ots-audit:
	@$(PY) tools/ots_audit.py

# Run with FILING=1 immediately before filing: it then also requires every
# [FILL] placeholder in the registration to have been resolved.
prereg-check:
	@$(PY) tools/prereg_check.py $(if $(FILING),--filing,)

# Stamps every commit that has no proof. UNSTAMPED.txt is appended to rather
# than cleared: a late stamp proves the commit existed by the time it was
# stamped, not by its commit date, and the paper should be able to say which
# proofs are late instead of presenting them all as contemporaneous.
ots-backfill:
	@command -v ots >/dev/null 2>&1 || { echo "ots not installed (pipx install opentimestamps-client)"; exit 1; }
	@mkdir -p derived/ots
	@n=0; for h in `git rev-list HEAD`; do \
	  test -f "derived/ots/$$h.txt.ots" && continue; \
	  printf '%s\n' "$$h" > "derived/ots/$$h.txt"; \
	  if ots stamp "derived/ots/$$h.txt" >/dev/null 2>&1; then \
	    echo "stamped $$h (late)"; n=`expr $$n + 1`; \
	    grep -q "^$$h	" derived/ots/UNSTAMPED.txt 2>/dev/null || \
	      printf '%s\tstamped late by ots-backfill; no proof existed at commit time\n' "$$h" >> derived/ots/UNSTAMPED.txt; \
	  else rm -f "derived/ots/$$h.txt"; echo "FAILED  $$h"; fi; \
	done; \
	test $$n -gt 0 || echo "every commit already has a proof"
	@echo "note: a late stamp bounds the commit from above only -- it proves the"
	@echo "      hash existed by the stamping time, not by the commit date."
	@echo "      commit the new proofs; that commit is stamped in turn."
