"""The lossless check of docs/PORTING.md section 4, for the BPO port.

    python tools/lossless_check.py BPO_CHECKOUT [PORT_ROOT]

Every statement of BPO (bc64e91), renamed into this namespace, against every
statement of the port's modules: ground statements as triples, blank nodes as
trees (PORTING.md's `tree` and `statements`, verbatim). Prints what is missing
from the port and what the port adds, beyond the two exclusions the port
makes by design: the owl:Ontology headers (replaced, one per module) and the
statements whose subject is a CCO or OBO term (BPO's bridges; each asserted
by the pinned CCO).

Used in WP6 Phase A to show S0 adds nothing and S1 adds exactly the changes
the PO approved.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

from rdflib import BNode, Graph, URIRef
from rdflib.namespace import OWL, RDF

SOURCES = (["ontology/apqc-ext.ttl", "ontology/capabilities_roles.ttl",
            "ontology/delivery_processes.ttl"]
           + ["ontology/slices/apqc_%d_0.ttl" % n for n in range(1, 14)]
           + ["ontology/apqc-catalog.ttl", "ontology/capabilities_wiring.ttl"])
MODULES = (["ontology/bpot.ttl"]
           + ["ontology/sections/pcf_%d.ttl" % n for n in range(1, 14)]
           + ["ontology/catalog.ttl", "ontology/wiring.ttl"])
OLD = ("https://fandaws.com/ontology/bpo#",
       "https://fandaws.com/ontology/bpo/scheme#")
NEW = "https://fandaws.com/ontology/bpot#"
UPSTREAM = ("https://www.commoncoreontologies.org/",
            "http://purl.obolibrary.org/obo/")


def tree(graph, node):
    """A blank node as the sorted text of everything under it."""
    if not isinstance(node, BNode):
        return node.n3()
    rows = sorted("%s %s" % (p.n3(), tree(graph, o))
                  for p, o in graph.predicate_objects(node))
    return "[" + "; ".join(rows) + "]"


def statements(graph):
    named = {(s.n3(), p.n3(), tree(graph, o))
             for s, p, o in graph if not isinstance(s, BNode)}
    roots = {("", "", tree(graph, s)) for s in set(graph.subjects())
             if isinstance(s, BNode) and (None, None, s) not in graph}
    return named | roots


def move(term):
    if isinstance(term, URIRef):
        for old in OLD:
            if str(term).startswith(old):
                return URIRef(NEW + str(term)[len(old):])
    return term


def without_headers(graph):
    headers = set(graph.subjects(RDF.type, OWL.Ontology))
    out = Graph()
    for s, p, o in graph:
        if s in headers or str(s).startswith(UPSTREAM):
            continue
        out.add((move(s), move(p), move(o)))
    # Blank nodes reachable only from a dropped subject go with it.
    return out


def load(root: Path, files) -> Graph:
    g = Graph()
    for f in files:
        g.parse(root / f)
    return g


def main(argv) -> int:
    source = Path(argv[0])
    port = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    old = statements(without_headers(load(source, SOURCES)))
    new = statements(without_headers(load(port, MODULES)))
    missing, extra = old - new, new - old
    print("source %d, port %d, missing %d, extra %d"
          % (len(old), len(new), len(missing), len(extra)))
    for label, rows in (("missing", missing), ("extra", extra)):
        kinds = Counter(p for _, p, _ in rows)
        for p, n in sorted(kinds.items()):
            print("  %s %5d  %s" % (label, n, p))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
