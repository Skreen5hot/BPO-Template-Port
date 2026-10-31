"""Write the findings register from the approved WP6 classification.

    python tools/wp6_register.py STATE REVIEW

Amendment A5: dispositions are written and approved per class of finding,
one entry per finding. The classes and their approved reasons are the table
in research/wp6/classification.md; each finding's class is in
research/wp6/measure/<STATE>/classes.tsv (tools/wp6_classify.py).

The template's --propose takes one reason, owner and review date for all of
a check's new findings at once, so it cannot write a reason per class. This
calls the same function it does, findings.propose(), once per class, with
that class's findings, its reason and its owner, and writes the entries to
config/findings-register.yaml. REVIEW is the review date of every entry.

A class whose classification is "upstream" names the pinned upstream term
(UPSTREAM below), as the register requires of a defect not in this ontology.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import findings  # noqa: E402

TABLE = ROOT / "research" / "wp6" / "classification.md"
APPROVED = "approved by the BPO architect, %s"
#: Classes approved later than the table of 2026-10-30 (A6: dated changes).
DATES = {"K18": "2026-10-31", "K19": "2026-10-31"}
UPSTREAM = {"K13": "CCO https://www.commoncoreontologies.org/ont00001180"}


def classes() -> dict:
    """Class -> (classification, owner, reason), from the approved table."""
    out = {}
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 8 and re.fullmatch(r"K[0-9]{2}", cells[0]):
            verdict = cells[4].replace("**", "")
            out[cells[0]] = (verdict, cells[5], cells[6])
    return out


def main(argv) -> int:
    state, review = argv
    base = ROOT / "research" / "wp6" / "measure" / state
    read = lambda name: list(csv.DictReader(  # noqa: E731
        open(base / name, encoding="utf-8", newline=""), delimiter="\t",
        quoting=csv.QUOTE_NONE))
    message = {findings.identity(r): r["message"]
               for r in read("findings.tsv")}
    table = classes()
    by_class: dict = {}
    for row in read("classes.tsv"):
        record = {k: row[k] for k in findings.IDENTITY}
        record["message"] = message[findings.identity(record)]
        by_class.setdefault(row["class"], []).append(record)

    entries = []
    for name in sorted(by_class):
        verdict, owner, reason = table[name]
        text = "%s, %s (WP6 class %s, %s; research/wp6/classification.md)" % (
            verdict, reason, name, APPROVED % DATES.get(name, "2026-10-30"))
        proposed = yaml.safe_load(findings.propose(
            by_class[name], text, owner, review)) or []
        for entry in proposed:
            if name in UPSTREAM:
                entry["upstream"] = UPSTREAM[name]
        entries += proposed
        print("  %s %5d  %s" % (name, len(proposed), verdict))

    path = ROOT / findings.REGISTER
    head = path.read_text(encoding="utf-8").split("format_version:")[0]
    body = yaml.safe_dump({"format_version": 1, "entries": entries},
                          sort_keys=False, allow_unicode=True, width=100)
    path.write_text(head + body, encoding="utf-8", newline="\n")
    findings.load()  # refuses a register a check could not use
    print("  %d entr(ies) -> %s" % (len(entries), findings.REGISTER))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
