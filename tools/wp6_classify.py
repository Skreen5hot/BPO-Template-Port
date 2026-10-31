"""Assign every finding of a WP6 state to exactly one finding class.

    python tools/wp6_classify.py STATE TAG

Reads research/wp6/measure/<STATE>/findings.tsv, loads TAG's ontology with
the pinned CCO and BFO (.upstream-cache/), and writes
research/wp6/measure/<STATE>/classes.tsv: each finding's identity and its
class. A finding no class claims, or two classes claim, stops the run, so
the classification covers every finding exactly once (amendment A5).

The classes, their verdicts and reasons are in research/wp6/classification.md.
Three classes are split from one shape by a mechanical test against the
pinned CCO, stated with each:

  K06/K07  "more than one named parent": K06 when every parent but one is
           already an ancestor of another asserted parent (redundant);
           K07 otherwise.
  K12/K17  "label ends in a parenthetical qualifier": K17 when the label is
           the PCF row's own name, verbatim (a P<id> class whose label equals
           PCF_<id>'s skos:prefLabel); K12 otherwise.
  K03/K04/K05  "definition does not name its parent": K03 when that parent
           is redundant in the K06 sense; K04 when the class has another
           named parent; K05 when it is the only one.
  K08/K18/K19  "two different rdfs:comment values" (amended 2026-10-31, A6,
           the BPO architect's decision): K18 when every comment variant
           of the term is in one module other than bpot.ttl (a review
           addendum, false alarm); K19 when that one module is bpot.ttl,
           where the port merged three BPO files (real, the port's); K08
           otherwise. From TAG's config/annotation-drift.tsv.
"""

from __future__ import annotations

import csv
import re
import subprocess
import sys
import tarfile
import tempfile
from io import BytesIO
from pathlib import Path

from rdflib import BNode, Graph, URIRef
from rdflib.namespace import RDFS, SKOS

ROOT = Path(__file__).resolve().parents[1]
KEYS = ("check", "where", "focus", "rule", "digest", "severity")


def content(tag: str) -> Graph:
    data = subprocess.run(["git", "archive", tag, "ontology"], cwd=ROOT,
                          capture_output=True, check=True).stdout
    g = Graph()
    with tempfile.TemporaryDirectory() as tmp:
        tarfile.open(fileobj=BytesIO(data)).extractall(tmp, filter="data")
        for f in sorted(Path(tmp).rglob("*.ttl")):
            g.parse(f)
    for upstream in ("cco.ttl", "bfo.ttl"):
        g.parse(ROOT / ".upstream-cache" / upstream)
    return g


def named_parents(g, c):
    return [p for p in g.objects(c, RDFS.subClassOf) if not isinstance(p, BNode)]


def redundant(g, c, p) -> bool:
    """p is an ancestor of another asserted named parent of c."""
    return any(p in set(g.transitive_objects(q, RDFS.subClassOf)) - {q}
               for q in named_parents(g, c) if q != p)


def label_is_pcf_name(g, c) -> bool:
    """A P<id> class whose label is its PCF row's name, verbatim."""
    ns = "https://fandaws.com/ontology/bpot#"
    m = re.fullmatch(r"P([0-9]+)", str(c)[len(ns):])
    if not m:
        return False
    row = URIRef(ns + "PCF_" + m.group(1))
    names = {str(x) for x in g.objects(row, SKOS.prefLabel)}
    return any(str(x) in names for x in g.objects(c, RDFS.label))


def comment_modules(tag: str) -> dict:
    """bpot:<local> -> the modules giving it a comment, at TAG."""
    text = subprocess.run(["git", "show", "%s:config/annotation-drift.tsv"
                           % tag], cwd=ROOT, capture_output=True, check=True,
                          ).stdout.decode("utf-8")
    out = {}
    for row in csv.DictReader(text.splitlines(), delimiter="	",
                              quoting=csv.QUOTE_NONE):
        if row["property"] == "comment":
            out.setdefault(row["term"], set()).add(row["module"])
    return out


def classify(row: dict, g: Graph, modules: dict) -> list[str]:
    rule, msg, where = row["rule"], row["message"], row["where"]
    focus = URIRef(row["focus"])
    out = []
    if "has no definition source" in msg:
        out.append("K01")
    if rule.endswith("AuthoredClassPlacementShape"):
        out.append("K02")
    if "does not name its parent" in msg:
        label = re.search(r'parent, "(.*)"\. A genus', msg).group(1)
        parents = named_parents(g, focus)
        named = [p for p in parents
                 if any(str(x) == label for x in g.objects(p, RDFS.label))]
        if named and redundant(g, focus, named[0]):
            out.append("K03")
        elif len(parents) > 1:
            out.append("K04")
        else:
            out.append("K05")
    if "more than one named parent" in msg:
        parents = named_parents(g, focus)
        rest = [p for p in parents if not redundant(g, focus, p)]
        out.append("K06" if len(rest) == 1 else "K07")
    if "two different rdfs:comment values" in msg:
        where_from = modules.get("bpot:" + str(focus).rsplit("#", 1)[1], set())
        if len(where_from) == 1:
            out.append("K19" if where_from == {"ontology/bpot.ttl"}
                       else "K18")
        else:
            out.append("K08")
    if "two different http://www.w3.org/2004/02/skos/core#definition" in msg:
        out.append("K09")
    if "two different http://www.w3.org/2000/01/rdf-schema#label" in msg:
        out.append("K10")
    if where == "naming" and rule == "scheme:capability-as-process":
        out.append("K11")
    if "ends in a parenthetical qualifier" in msg:
        out.append("K17" if label_is_pcf_name(g, focus) else "K12")
    if ("not known to fall under the property's range "
            "https://www.commoncoreontologies.org/ont00001017" in msg
            or ("whose domain https://www.commoncoreontologies.org/ont00001017"
                in msg)):
        out.append("K13")
    if msg == "Property has no skos:definition.":
        out.append("K14")
    if "Concept scheme has no top concept" in msg:
        out.append("K15")
    if row["check"] == "iri_lint" and rule == "naming_convention":
        out.append("K16")
    return out


def main(argv) -> int:
    state, tag = argv
    base = ROOT / "research" / "wp6" / "measure" / state
    with open(base / "findings.tsv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t",
                                   quoting=csv.QUOTE_NONE))
    g = content(tag)
    modules = comment_modules(tag)
    lines, counts, bad = ["\t".join(KEYS + ("class",))], {}, []
    for row in rows:
        classes = classify(row, g, modules)
        if len(classes) != 1:
            bad.append((classes, row["message"][:120]))
            continue
        counts[classes[0]] = counts.get(classes[0], 0) + 1
        lines.append("\t".join([row[k] for k in KEYS] + classes))
    if bad:
        for item in bad[:20]:
            print("  unclassified or ambiguous:", item)
        raise SystemExit("%d finding(s) not in exactly one class" % len(bad))
    (base / "classes.tsv").write_text("\n".join(lines) + "\n",
                                      encoding="utf-8", newline="\n")
    for k in sorted(counts):
        print("  %s %5d" % (k, counts[k]))
    print("  %d finding(s), every one in exactly one class" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
