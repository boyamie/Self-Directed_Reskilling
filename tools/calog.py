#!/usr/bin/env python3
"""Candidate-action log tooling. Python 3.11+, standard library only.

Subcommands:
  validate            schema + timing checks over logs/
  aggregate           rebuild derived/ (Principle 4 verdict, gate table, hours)
  export              LaTeX fragments for the manuscript
  new-week W          create logs/candidate-actions/W<NN>.toml from template
  selftest            run the built-in tests

The Principle 4 verdict is computed by decide(), which implements PROTOCOL.md
section 2.1 literally. The verdict is whatever this function returns.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

if sys.version_info < (3, 11):
    raise SystemExit(
        "calog.py needs Python 3.11 or newer for tomllib; this is %d.%d at %s.\n"
        "macOS ships /usr/bin/python3 as 3.9. Use a newer interpreter, e.g.\n"
        "  make check PY=$(command -v python3.13)"
        % (sys.version_info[0], sys.version_info[1], sys.executable))

import tomllib  # noqa: E402  (guarded above so the failure is legible)

ROOT = pathlib.Path(__file__).resolve().parent.parent
CA_DIR = ROOT / "logs" / "candidate-actions"
GATE_DIR = ROOT / "logs" / "gates"
JOURNAL_DIR = ROOT / "logs" / "journal"
DERIVED = ROOT / "derived"

AI_VALUES = {"yes", "no", "partly"}
WITHOUT_AI_VALUES = {"in_set", "outside_set", "uncertain"}
LATE_DAYS = 2  # PROTOCOL: entry more than this many days after week start is retrospective


class Problem(str):
    pass


# --------------------------------------------------------------------- load
def load(path: pathlib.Path) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def as_date(v) -> dt.date | None:
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    return None


def final_logs(directory: pathlib.Path) -> list[tuple[pathlib.Path, dict]]:
    out = []
    for p in sorted(directory.glob("*.toml")):
        d = load(p)
        if d.get("status") == "final":
            out.append((p, d))
    return out


# ----------------------------------------------------------------- validate
def validate_week(path: pathlib.Path, d: dict) -> list[str]:
    errs: list[str] = []
    e = lambda m: errs.append(f"{path.name}: {m}")

    for key in ("week", "week_start", "week_end", "recorded_at", "selected"):
        if key not in d:
            e(f"missing required key '{key}'")
    if errs:
        return errs

    cands = d.get("candidate", [])
    if len(cands) < 2:
        e("fewer than two candidate actions — field (a) asks for the full set "
          "considered, and a set of one is not a set. If only one option was "
          "genuinely considered, say so explicitly in a second entry.")

    ids = [c.get("id") for c in cands]
    if len(ids) != len(set(ids)):
        e("duplicate candidate ids")

    for c in cands:
        cid = c.get("id", "?")
        if not (c.get("description") or "").strip():
            e(f"{cid}: empty description")
        ai = c.get("ai_assisted")
        if ai not in AI_VALUES:
            e(f"{cid}: ai_assisted={ai!r} not in {sorted(AI_VALUES)}")
        if ai in {"yes", "partly"} and not (c.get("ai_note") or "").strip():
            e(f"{cid}: ai_assisted={ai!r} requires ai_note (protocol asks for "
              "one sentence of detail)")
        wa = c.get("without_ai")
        if wa not in WITHOUT_AI_VALUES:
            e(f"{cid}: without_ai={wa!r} not in {sorted(WITHOUT_AI_VALUES)}")

    sel = d.get("selected", {})
    if sel.get("action_id") not in ids:
        e(f"selected.action_id={sel.get('action_id')!r} is not among the candidates")
    if not (sel.get("rationale_at_time") or "").strip():
        e("selected.rationale_at_time is empty — field (c) is the rationale at "
          "the time of selection and cannot be reconstructed later")

    ws, rec = as_date(d.get("week_start")), as_date(d.get("recorded_at"))
    if ws and rec:
        delta = (rec - ws).days
        if delta < 0:
            e(f"recorded_at {rec} precedes week_start {ws}")
        elif delta > LATE_DAYS:
            e(f"WARN recorded_at {rec} is {delta} days after week_start {ws}; "
              "this is a retrospective entry and must be reported as one")
    return errs


def validate_gate(path: pathlib.Path, d: dict) -> list[str]:
    errs: list[str] = []
    e = lambda m: errs.append(f"{path.name}: {m}")

    if d.get("ruling") not in {"pass", "fail"}:
        e(f"ruling={d.get('ruling')!r} must be 'pass' or 'fail'")
    if d.get("adjudicator") == "first_author":
        e("adjudicated by the first author — protocol section 3 requires the "
          "second author to rule")
    if not (d.get("evidence") or "").strip():
        e("evidence is empty")

    strict = d.get("strict_reading_met")
    if strict is None:
        e("strict_reading_met missing")
    elif strict is False and d.get("ruling") == "pass":
        e("strict_reading_met=false with ruling='pass' — protocol section 3 "
          "records a criterion met only under a looser reading as a FAIL")

    gd, ruled = as_date(d.get("gate_date")), as_date(d.get("ruled_at"))
    if gd and ruled:
        delta = (ruled - gd).days
        if delta < 0:
            e(f"ruled_at {ruled} precedes gate_date {gd}")
        elif delta > 2:
            e(f"WARN ruled_at {ruled} is {delta} days after gate_date {gd}; "
              "protocol section 3 asks for a ruling within 48 hours")
    return errs


def cmd_validate(_args) -> int:
    problems: list[str] = []
    n = 0
    for p, d in final_logs(CA_DIR):
        n += 1
        problems += validate_week(p, d)
    for p, d in final_logs(GATE_DIR):
        n += 1
        problems += validate_gate(p, d)

    warns = [x for x in problems if "WARN" in x]
    errs = [x for x in problems if "WARN" not in x]
    for x in errs:
        print("ERROR " + x)
    for x in warns:
        print(x)
    print(f"\n{n} finalised file(s); {len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0


# ----------------------------------------------------- the Principle 4 rule
def decide(weeks: list[dict]) -> dict:
    """PROTOCOL.md section 2.1, implemented literally.

    Support:    >=2 weeks whose SELECTED action is outside_set and ai in
                {yes, partly}.
    Refutation: every SELECTED action across all weeks has ai in {yes, partly}
                AND without_ai == in_set.
    Otherwise:  indeterminate.
    """
    sel_rows = []
    for d in weeks:
        by_id = {c.get("id"): c for c in d.get("candidate", [])}
        c = by_id.get(d.get("selected", {}).get("action_id"))
        if c is None:
            continue
        sel_rows.append({"week": d.get("week"), "id": c.get("id"),
                         "ai": c.get("ai_assisted"), "without_ai": c.get("without_ai")})

    support_weeks = [r["week"] for r in sel_rows
                     if r["without_ai"] == "outside_set" and r["ai"] in {"yes", "partly"}]
    n_support = len(support_weeks)

    refuted = bool(sel_rows) and all(
        r["ai"] in {"yes", "partly"} and r["without_ai"] == "in_set" for r in sel_rows)

    if n_support >= 2:
        verdict = "supported"
    elif refuted:
        verdict = "refuted"
    else:
        verdict = "indeterminate"

    # Secondary descriptive over the full candidate set — not used for the verdict.
    all_c = [c for d in weeks for c in d.get("candidate", [])]
    secondary = {
        "n_candidates": len(all_c),
        "n_outside_set": sum(1 for c in all_c if c.get("without_ai") == "outside_set"),
        "n_uncertain": sum(1 for c in all_c if c.get("without_ai") == "uncertain"),
        "n_ai_assisted": sum(1 for c in all_c if c.get("ai_assisted") in {"yes", "partly"}),
    }
    return {"verdict": verdict, "n_weeks_finalised": len(sel_rows),
            "n_support": n_support, "support_weeks": sorted(support_weeks),
            "refutation_clause_met": refuted, "selected": sel_rows,
            "secondary_over_all_candidates": secondary}


# ---------------------------------------------------------------- aggregate
def journal_hours() -> dict:
    """Total hours per track from journal front-lines: 'hours: 1.5 | track: learning'."""
    tracks: dict[str, float] = {}
    days = 0
    for p in sorted(JOURNAL_DIR.glob("*.md")):
        if p.name == "README.md":
            continue
        days += 1
        for line in p.read_text(encoding="utf-8").splitlines():
            low = line.lower().strip()
            if not low.startswith("hours:"):
                continue
            try:
                hrs = float(low.split("hours:")[1].split("|")[0].strip())
            except (ValueError, IndexError):
                continue
            track = "unspecified"
            if "track:" in low:
                track = low.split("track:")[1].strip().split()[0] if low.split("track:")[1].strip() else track
            tracks[track] = round(tracks.get(track, 0.0) + hrs, 2)
    return {"journal_days": days, "hours_by_track": tracks,
            "total_hours": round(sum(tracks.values()), 2)}


def cmd_aggregate(_args) -> int:
    weeks = [d for _, d in final_logs(CA_DIR)]
    gates = [d for _, d in final_logs(GATE_DIR)]
    DERIVED.mkdir(exist_ok=True)

    p4 = decide(weeks)
    (DERIVED / "principle4.json").write_text(json.dumps(p4, indent=2) + "\n", encoding="utf-8")

    gtab = [{"gate": g.get("gate"), "date": str(as_date(g.get("gate_date"))),
             "ruling": g.get("ruling"), "strict_reading_met": g.get("strict_reading_met"),
             "adjudicator": g.get("adjudicator"),
             "disagreement": (g.get("disagreement") or "").strip()} for g in gates]
    (DERIVED / "gates.json").write_text(json.dumps(gtab, indent=2) + "\n", encoding="utf-8")

    hrs = journal_hours()
    (DERIVED / "hours.json").write_text(json.dumps(hrs, indent=2) + "\n", encoding="utf-8")

    print(f"weeks finalised   {p4['n_weeks_finalised']}/12")
    print(f"principle 4       {p4['verdict']}  (n_support={p4['n_support']}, "
          f"weeks={p4['support_weeks']})")
    print(f"gates ruled       {len(gtab)}/5  " +
          " ".join(f"{g['gate']}={g['ruling']}" for g in gtab))
    print(f"journal           {hrs['journal_days']} days, {hrs['total_hours']} h  "
          f"{hrs['hours_by_track']}")
    return 0


# ------------------------------------------------------------------- export
def cmd_export(_args) -> int:
    DERIVED.mkdir(exist_ok=True)
    p4 = json.loads((DERIVED / "principle4.json").read_text(encoding="utf-8")) \
        if (DERIVED / "principle4.json").exists() else decide([d for _, d in final_logs(CA_DIR)])
    gates = [d for _, d in final_logs(GATE_DIR)]

    rows = "\n".join(
        f"{r['week']} & {r['id']} & {r['ai']} & {r['without_ai'].replace('_',' ')} \\\\"
        for r in p4["selected"])
    tex = ("% generated by tools/calog.py export — do not edit\n"
           "\\begin{tabular}{@{}llll@{}}\n\\toprule\n"
           "Week & Selected & AI assistance (b) & Without AI (d) \\\\\n\\midrule\n"
           f"{rows}\n\\bottomrule\n\\end{{tabular}}\n"
           f"% verdict: {p4['verdict']} (n_support={p4['n_support']})\n")
    (DERIVED / "table_candidate_actions.tex").write_text(tex, encoding="utf-8")

    grows = "\n".join(
        f"{g.get('gate')} & {as_date(g.get('gate_date'))} & {g.get('ruling')} & "
        f"{'strict' if g.get('strict_reading_met') else 'loose reading'} \\\\"
        for g in gates)
    gtex = ("% generated by tools/calog.py export — do not edit\n"
            "\\begin{tabular}{@{}llll@{}}\n\\toprule\n"
            "Gate & Date & Ruling & Reading \\\\\n\\midrule\n"
            f"{grows}\n\\bottomrule\n\\end{{tabular}}\n")
    (DERIVED / "table_gates.tex").write_text(gtex, encoding="utf-8")
    print("wrote derived/table_candidate_actions.tex, derived/table_gates.tex")
    return 0


# ----------------------------------------------------------------- new-week
def cmd_new_week(args) -> int:
    wk = int(args.week)
    if not 1 <= wk <= 12:
        print("week must be 1..12", file=sys.stderr)
        return 1
    dst = CA_DIR / f"W{wk:02d}.toml"
    print(f"{dst.relative_to(ROOT)} already exists — edit it in place" if dst.exists()
          else f"{dst.relative_to(ROOT)} missing; regenerate from the repo template")
    return 0


# ----------------------------------------------------------------- selftest
def cmd_selftest(_args) -> int:
    def mk(week, ai, wa, sel="A1", extra=None):
        cands = [{"id": "A1", "description": "x", "ai_assisted": ai,
                  "ai_note": "n", "without_ai": wa},
                 {"id": "A2", "description": "y", "ai_assisted": "no",
                  "ai_note": "", "without_ai": "in_set"}]
        if extra:
            cands.append(extra)
        return {"week": week, "candidate": cands,
                "selected": {"action_id": sel, "rationale_at_time": "r"}}

    fails = []
    def eq(got, want, label):
        if got != want:
            fails.append(f"{label}: got {got!r}, want {want!r}")

    eq(decide([mk(1, "yes", "outside_set"), mk(2, "partly", "outside_set")])["verdict"],
       "supported", "two outside_set weeks -> supported")
    eq(decide([mk(1, "yes", "outside_set")])["verdict"],
       "indeterminate", "one outside_set week is not recurrence")
    eq(decide([mk(1, "yes", "in_set"), mk(2, "partly", "in_set")])["verdict"],
       "refuted", "all selected ai-assisted and in_set -> refuted")
    eq(decide([mk(1, "no", "in_set"), mk(2, "no", "in_set")])["verdict"],
       "indeterminate", "no AI involvement -> indeterminate, not refuted")
    eq(decide([mk(1, "yes", "uncertain"), mk(2, "yes", "uncertain")])["verdict"],
       "indeterminate", "uncertain-dominated -> indeterminate")
    eq(decide([])["verdict"], "indeterminate", "empty -> indeterminate")
    # refutation must not be triggered by non-selected candidates
    eq(decide([mk(1, "yes", "in_set"), mk(2, "yes", "in_set",
        extra={"id": "A3", "description": "z", "ai_assisted": "no",
               "ai_note": "", "without_ai": "outside_set"})])["verdict"],
       "refuted", "refutation is evaluated over selected actions only")

    tmp = pathlib.Path("/tmp/_calog_probe.toml")
    tmp.write_text('week=1\nweek_start=2026-08-03\nweek_end=2026-08-09\n'
                   'recorded_at=2026-08-03T09:00:00+09:00\n'
                   '[[candidate]]\nid="A1"\ndescription="x"\nai_assisted="yes"\n'
                   'ai_note=""\nwithout_ai="in_set"\n'
                   '[selected]\naction_id="A1"\nrationale_at_time="r"\n', encoding="utf-8")
    probe = validate_week(tmp, load(tmp))
    if not any("requires ai_note" in x for x in probe):
        fails.append("validator: missing ai_note not caught")
    if not any("fewer than two candidate" in x for x in probe):
        fails.append("validator: single-candidate set not caught")

    gtmp = pathlib.Path("/tmp/_calog_gate.toml")
    gtmp.write_text('gate="M1"\ngate_date=2026-08-16\nruling="pass"\n'
                    'adjudicator="first_author"\nevidence="e"\n'
                    'strict_reading_met=false\n'
                    'ruled_at=2026-08-16T21:00:00+09:00\n', encoding="utf-8")
    gp = validate_gate(gtmp, load(gtmp))
    if not any("second author" in x for x in gp):
        fails.append("validator: first-author adjudication not caught")
    if not any("looser reading" in x for x in gp):
        fails.append("validator: loose-reading pass not caught")

    for f in fails:
        print("FAIL " + f)
    print(f"selftest: {'FAILED' if fails else 'ok'} ({len(fails)} failure(s))")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="calog", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate").set_defaults(fn=cmd_validate)
    sub.add_parser("aggregate").set_defaults(fn=cmd_aggregate)
    sub.add_parser("export").set_defaults(fn=cmd_export)
    nw = sub.add_parser("new-week"); nw.add_argument("week"); nw.set_defaults(fn=cmd_new_week)
    sub.add_parser("selftest").set_defaults(fn=cmd_selftest)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
