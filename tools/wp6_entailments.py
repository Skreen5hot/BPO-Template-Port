"""The class hierarchy a WP6 state entails, and what differs between states.

    python tools/wp6_entailments.py STATE TAG          # a tagged state
    python tools/wp6_entailments.py STATE --dir DIR    # modules in DIR
    python tools/wp6_entailments.py --diff STATE_A STATE_B

The memo of 2026-10-31 asks that a change to asserted axioms be told apart
from a change to what the ontology entails. For one state this merges its
modules (TAG's ontology/, or every .ttl under DIR, for a candidate change
not committed anywhere) with the pinned BFO and CCO (.upstream-cache/),
runs the pinned ROBOT with ELK, and writes every entailed superclass of
every class in the project's namespace, direct and indirect, with whether
it is also asserted:

  research/wp6/measure/<STATE>/entailments.tsv   class, superclass, asserted

--diff compares two such files: superclasses entailed in one state and not
the other, per class, and the asserted-only differences (an asserted axiom
added or removed with the entailment unchanged).
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import tarfile
import tempfile
from io import BytesIO
from pathlib import Path

from rdflib import BNode, Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "ontology"))

NS = "https://fandaws.com/ontology/bpot#"
THING = str(OWL.Thing)


def modules_of(tag: str, tmp: Path) -> list[Path]:
    data = subprocess.run(["git", "archive", tag, "ontology"], cwd=ROOT,
                          capture_output=True, check=True).stdout
    tarfile.open(fileobj=BytesIO(data)).extractall(tmp, filter="data")
    return sorted((tmp / "ontology").rglob("*.ttl"))


def asserted(paths: list[Path]) -> set:
    g = Graph()
    for p in paths:
        g.parse(p)
    return {(str(s), str(o)) for s, o in g.subject_objects(RDFS.subClassOf)
            if str(s).startswith(NS) and not isinstance(o, BNode)}


def entailed(paths: list[Path], tmp: Path) -> set:
    import reason

    jar = reason.fetch_jar(reason.config(ROOT)["robot"],
                           ROOT / reason.TOOL_CACHE)
    upstream = [ROOT / ".upstream-cache" / n for n in ("bfo.ttl", "cco.ttl")]
    out = tmp / "inferred.ttl"
    command = [reason.java(), "-jar", str(jar), "merge"]
    for p in upstream + paths:
        command += ["--input", str(p)]
    command += ["reason", "--reasoner", "ELK", "--axiom-generators",
                "SubClass EquivalentClass", "--include-indirect", "true",
                "--exclude-tautologies", "structural",
                # Kept: B13's redundant parents are what is being measured.
                "--remove-redundant-subclass-axioms", "false",
                "--output", str(out)]
    done = subprocess.run(command, capture_output=True, text=True,
                          errors="replace")
    if done.returncode != 0:
        raise SystemExit("ROBOT failed:\n" + done.stdout[-1500:]
                         + done.stderr[-1500:])
    g = Graph()
    g.parse(out)
    pairs = set()
    for s, o in g.subject_objects(RDFS.subClassOf):
        if isinstance(s, URIRef) and isinstance(o, URIRef) \
                and str(s).startswith(NS) and str(o) != THING and s != o:
            pairs.add((str(s), str(o)))
    for s, o in g.subject_objects(OWL.equivalentClass):
        if isinstance(s, URIRef) and isinstance(o, URIRef) and s != o:
            for a, b in ((s, o), (o, s)):
                if str(a).startswith(NS):
                    pairs.add((str(a), str(b)))
    named = {str(c) for c in g.subjects(RDF.type, OWL.Class)
             if isinstance(c, URIRef) and str(c).startswith(NS)}
    return pairs, named


def write(state: str, paths: list[Path], tmp: Path) -> Path:
    told = asserted(paths)
    pairs, named = entailed(paths, tmp)
    missing = told - pairs
    if missing:
        # An asserted named superclass not entailed would be a reasoner fault.
        raise SystemExit("asserted but not entailed: %s" % sorted(missing)[:5])
    base = ROOT / "research" / "wp6" / "measure" / state
    base.mkdir(parents=True, exist_ok=True)
    path = base / "entailments.tsv"
    rows = sorted(pairs)
    path.write_text("class\tsuperclass\tasserted\n" + "".join(
        "%s\t%s\t%s\n" % (s, o, "yes" if (s, o) in told else "no")
        for s, o in rows), encoding="utf-8", newline="\n")
    print("  %s: %d class(es), %d entailed superclass pair(s), %d asserted"
          % (state, len(named), len(rows), len(told)))
    return path


def load(state: str) -> dict:
    path = ROOT / "research" / "wp6" / "measure" / state / "entailments.tsv"
    with open(path, encoding="utf-8", newline="") as f:
        return {(r["class"], r["superclass"]): r["asserted"] == "yes"
                for r in csv.DictReader(f, delimiter="\t")}


def diff(a: str, b: str) -> int:
    x, y = load(a), load(b)
    only_a = sorted(set(x) - set(y))
    only_b = sorted(set(y) - set(x))
    told = sorted(k for k in set(x) & set(y) if x[k] != y[k])
    short = lambda i: i.replace(NS, "bpot:").replace(  # noqa: E731
        "https://www.commoncoreontologies.org/", "cco:").replace(
        "http://purl.obolibrary.org/obo/", "obo:")
    print("  entailed in %s only: %d" % (a, len(only_a)))
    for s, o in only_a:
        print("    %s  ⊑  %s" % (short(s), short(o)))
    print("  entailed in %s only: %d" % (b, len(only_b)))
    for s, o in only_b:
        print("    %s  ⊑  %s" % (short(s), short(o)))
    print("  entailed in both, asserted in one only: %d" % len(told))
    for s, o in told:
        print("    %s  ⊑  %s  (asserted in %s)"
              % (short(s), short(o), a if x[(s, o)] else b))
    return 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("state", nargs="?")
    ap.add_argument("tag", nargs="?")
    ap.add_argument("--dir")
    ap.add_argument("--diff", nargs=2, metavar=("STATE_A", "STATE_B"))
    args = ap.parse_args(argv)
    if args.diff:
        return diff(*args.diff)
    with tempfile.TemporaryDirectory() as tmp:
        if args.dir:
            paths = sorted(Path(args.dir).rglob("*.ttl"))
        else:
            paths = modules_of(args.tag, Path(tmp))
        write(args.state, paths, Path(tmp))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
