"""B13, one row per asserted parent of every multi-parent class (WP6 Phase B).

    python tools/wp6_b13.py TAG OUT_DIR

For every class in TAG's ontology with more than one named parent, writes
research/wp6/phase-b/b13-parents.tsv: each asserted parent, whether it is
redundant (already an ancestor of another asserted parent, in TAG's
ontology with the pinned CCO and BFO), the path that makes it so, the
module asserting it, and the finding class (K06 or K07) of the class.

Then writes OUT_DIR: TAG's ontology with every redundant parent axiom
removed and nothing else changed -- the candidate B13 change, which
tools/wp6_entailments.py --dir measures against TAG without committing it.
"""

from __future__ import annotations

import csv
import re
import sys
import tarfile
import tempfile
from io import BytesIO
from pathlib import Path
import subprocess

from rdflib import BNode, Graph, URIRef
from rdflib.namespace import RDFS

ROOT = Path(__file__).resolve().parents[1]
NS = "https://fandaws.com/ontology/bpot#"


def short(i) -> str:
    return (str(i).replace(NS, "bpot:")
            .replace("https://www.commoncoreontologies.org/", "cco:")
            .replace("http://purl.obolibrary.org/obo/", "obo:"))


def path_up(g, start, goal):
    """The named-superclass path from start to goal, breadth first."""
    seen, queue = {start: None}, [start]
    while queue:
        node = queue.pop(0)
        if node == goal:
            out = []
            while node is not None:
                out.append(node)
                node = seen[node]
            return list(reversed(out))
        for p in g.objects(node, RDFS.subClassOf):
            if not isinstance(p, BNode) and p not in seen:
                seen[p] = node
                queue.append(p)
    return None


def main(argv) -> int:
    tag, out_dir = argv[0], Path(argv[1])
    data = subprocess.run(["git", "archive", tag, "ontology"], cwd=ROOT,
                          capture_output=True, check=True).stdout
    classes = {}
    cls_tsv = ROOT / "research/wp6/measure/s1/classes.tsv"
    with open(cls_tsv, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["class"] in ("K06", "K07"):
                classes[r["focus"]] = r["class"]
    with tempfile.TemporaryDirectory() as tmp:
        tarfile.open(fileobj=BytesIO(data)).extractall(tmp, filter="data")
        files = sorted((Path(tmp) / "ontology").rglob("*.ttl"))
        g, by_module = Graph(), {}
        for f in files:
            m = Graph().parse(f)
            rel = f.relative_to(tmp).as_posix()
            for s, o in m.subject_objects(RDFS.subClassOf):
                if not isinstance(o, BNode):
                    by_module.setdefault((s, o), []).append(rel)
            g += m
        for u in ("bfo.ttl", "cco.ttl"):
            g.parse(ROOT / ".upstream-cache" / u)

        rows, remove = [], set()
        for c in sorted(set(g.subjects(RDFS.subClassOf))):
            if not str(c).startswith(NS):
                continue
            parents = sorted(p for p in g.objects(c, RDFS.subClassOf)
                             if not isinstance(p, BNode))
            if len(parents) < 2:
                continue
            label = next((str(x) for x in g.objects(c, RDFS.label)), "")
            for p in parents:
                via = None
                for q in parents:
                    if q != p:
                        route = path_up(g, q, p)
                        if route:
                            via = route
                            break
                if via:
                    remove.add((c, p))
                rows.append((short(c), label, short(p),
                             "redundant" if via else "needed",
                             " ⊑ ".join(short(x) for x in via) if via else "",
                             ", ".join(sorted(set(by_module[(c, p)]))),
                             classes.get(str(c), "")))
        target = ROOT / "research/wp6/phase-b/b13-parents.tsv"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "class\tlabel\tparent\tstatus\tredundant_via\tasserted_in\tfinding\n"
            + "".join("\t".join(r) + "\n" for r in rows),
            encoding="utf-8", newline="\n")

        # The candidate: the same files, the redundant axioms removed.
        out_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            m = Graph().parse(f)
            for c, p in remove:
                m.remove((c, RDFS.subClassOf, p))
            dest = out_dir / f.relative_to(Path(tmp) / "ontology")
            dest.parent.mkdir(parents=True, exist_ok=True)
            m.serialize(dest, format="turtle")
    multi = len({r[0] for r in rows})
    print("  %d multi-parent class(es), %d asserted parent(s), %d redundant "
          "(removed in %s), %d needed"
          % (multi, len(rows), len(remove), out_dir,
             sum(r[3] == "needed" for r in rows)))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
