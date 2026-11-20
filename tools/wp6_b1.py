"""B1, the origin of every drifted annotation variant (WP6 Phase B).

    python tools/wp6_b1.py BPO_CHECKOUT SOURCE_COMMIT

For each row of config/annotation-drift.tsv (a term, a property, a module,
and the value that module gives), finds the BPO source file(s) the port
took that module from, and walks BPO's history up to SOURCE_COMMIT to the
first commit at which that file gave the term that value. Terms are
matched by local name, because BPO's namespace changed in v0.4.0; the
value is matched exactly, and again with the old `ex:` prefix read as
`bpo:` (ADR-002), so a variant created only by the prefix rename is
told apart from one created by an edit.

Each distinct file version is parsed once. Writes
research/wp6/phase-b/b1-origins.tsv, one row per variant:

  term, property, module, variant      (from the drift inventory)
  registry       yes when the module is bpot.ttl, the port of BPO's
                 apqc-ext.ttl registry and capability layer
  introduced     first commit giving this value (short sha, date)
  subject        that commit's subject line
  prefix_only    yes when the value existed earlier with `ex:` for `bpo:`
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.namespace import RDFS, SKOS

ROOT = Path(__file__).resolve().parents[1]
DRIFT = ROOT / "config" / "annotation-drift.tsv"
OUT = ROOT / "research" / "wp6" / "phase-b" / "b1-origins.tsv"
PROPS = {"comment": RDFS.comment, "definition": SKOS.definition,
         "label": RDFS.label}
REGISTRY = ["ontology/apqc-ext.ttl", "ontology/capabilities_roles.ttl",
            "ontology/delivery_processes.ttl"]


def sources(module: str) -> list[str]:
    if module == "ontology/bpot.ttl":
        return REGISTRY
    if module == "ontology/catalog.ttl":
        return ["ontology/apqc-catalog.ttl"]
    if module == "ontology/wiring.ttl":
        return ["ontology/capabilities_wiring.ttl"]
    n = module.rsplit("_", 1)[1].split(".")[0]
    return ["ontology/slices/apqc_%s_0.ttl" % n]


def git(bpo: Path, *args) -> str:
    return subprocess.run(["git", *args], cwd=bpo, capture_output=True,
                          text=True, encoding="utf-8", check=True).stdout


def main(argv) -> int:
    bpo, until = Path(argv[0]), argv[1]
    with open(DRIFT, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t",
                                          quoting=csv.QUOTE_NONE)
                if r["property"] in PROPS]
    wanted = {}  # file -> {(local, prop)}
    for r in rows:
        local = r["term"].split(":", 1)[1]
        for s in sources(r["module"]):
            wanted.setdefault(s, set()).add((local, r["property"]))

    commits = git(bpo, "log", "--reverse", "--format=%h|%ad|%s",
                  "--date=short", until).splitlines()
    parsed = {}   # blob -> {(local, prop): set(values)}
    history = {}  # (file, local, prop) -> [(commit line, values)]
    for line in commits:
        sha = line.split("|", 1)[0]
        for path, keys in wanted.items():
            try:
                blob = git(bpo, "rev-parse", "%s:%s" % (sha, path)).strip()
            except subprocess.CalledProcessError:
                continue
            if blob not in parsed:
                g = Graph()
                try:
                    g.parse(data=git(bpo, "cat-file", "-p", blob),
                            format="turtle")
                except Exception:  # noqa: BLE001 -- a broken historic file
                    parsed[blob] = {}
                    continue
                found = {}
                for s, p, o in g:
                    if not isinstance(o, Literal):
                        continue
                    for name, prop in PROPS.items():
                        if p == prop:
                            local = str(s).rsplit("#", 1)[-1]
                            if (local, name) in keys:
                                found.setdefault((local, name), set()).add(
                                    str(o))
                parsed[blob] = found
            for key, values in parsed[blob].items():
                history.setdefault((path,) + key, []).append((line, values))

    out = ["term\tproperty\tmodule\tregistry\tintroduced\tsubject\t"
           "prefix_only\tvariant"]
    for r in rows:
        local = r["term"].split(":", 1)[1]
        value = r["value"]
        first, prefix_first = None, None
        for s in sources(r["module"]):
            for line, values in history.get((s, local, r["property"]), []):
                if first is None and value in values:
                    first = line
                old = {v.replace("ex:", "bpo:") for v in values}
                if prefix_first is None and value in old:
                    prefix_first = line
        if first is None:
            first = "?|?|not found in the source file's history"
        sha, date, subject = first.split("|", 2)
        prefix_only = ("yes" if prefix_first and prefix_first != first
                       else "no")
        out.append("\t".join([
            r["term"], r["property"], r["module"],
            "yes" if r["module"] == "ontology/bpot.ttl" else "no",
            "%s %s" % (sha, date), subject.replace("\t", " "), prefix_only,
            value.replace("\t", " ").replace("\n", " ")]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print("  %d variant(s), %d file version(s) parsed, over %d commit(s)"
          % (len(rows), len(parsed), len(commits)))
    print("  not found: %d" % sum("not found" in l for l in out))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
