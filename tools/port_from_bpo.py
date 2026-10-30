"""Port the Business Process Ontology (BPO) into this repository.

One-shot, deterministic: reads a checkout of Skreen5hot/BusinessProcessOntology
and writes the modules and the SSSOM mapping set from it. Re-running it on the
same source commit gives the same bytes.

    python tools/port_from_bpo.py ../BusinessProcessOntology
    python tools/port_from_bpo.py ../BusinessProcessOntology --unchanged

--unchanged writes S0 for the template evaluation (WP6, amendment A2): BPO
ported with only the port's own mechanics (namespace, headers, duplicates,
bridges, and the header's cited sources), without the four changes the PO
approved on 2026-10-26 (top concepts, retyped properties, property
definitions, the release on every module).

What it does to the source, and nothing else:

  namespace   https://fandaws.com/ontology/bpo#         -> <namespace>
              https://fandaws.com/ontology/bpo/scheme#  -> <namespace>
              Local names are kept, so bpo:P10002 is bpot:P10002.
  headers     BPO's 18 owl:Ontology headers are replaced by one per module
              here; each records the BPO header it came from in
              dcterms:source.
  duplicates  BPO's slices each inline the act genera of apqc-ext.ttl (its
              D9 registry) so that a slice validates standalone. Here every
              module is read together, so a statement already written by an
              earlier module is written once. A statement is compared with
              its blank-node restrictions expanded, so an inlined copy of a
              restriction is a duplicate and a changed one is not.
  bridges     BPO's "1b. CCO SUPERCLASS BRIDGES" re-state CCO's own
              subClassOf axioms so that a slice validates without CCO.
              Statements about a CCO term are upstream's to make: dropped,
              and listed, so each can be checked against the pinned CCO.
  top concepts  BPO's PCF scheme names no top concept (shapes/skos_shapes.ttl
              requires one). Each concept of the scheme with no
              skos:broader -- the 13 PCF categories -- is made a top concept,
              both directions. Added on the PO's decision; nothing else in
              the catalog changes.
  properties  The ten BPO properties get the skos:definition the PO
              approved (DEFINITIONS); their comments are kept. The three
              requires* properties, asserted only between classes, become
              annotation properties (RETYPED).
  provenance  Each BPO header's dcterms:source literal is carried to the
              new module's header, and every module holding APQC text also
              cites the release it came from (PCF_RELEASE): BPO named it
              only on the catalog, and on no slice.
  drift       Every label, definition or comment that reads differently in
              different places is listed, variant by variant, in
              config/annotation-drift.tsv. Nothing is chosen between them.

Not ported: ontology/reference/ (frozen, superseded in BPO itself),
ontology/reports/ (generated), the APQC source spreadsheet, BPO's SHACL
shapes (a shape set of its own, ported separately), and the Python pipeline.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import rdflib
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import project  # noqa: E402

OLD = "https://fandaws.com/ontology/bpo#"
OLD_SCHEME = "https://fandaws.com/ontology/bpo/scheme#"
CCO = "https://www.commoncoreontologies.org/"
OBO = "http://purl.obolibrary.org/obo/"

#: (module path, title, comment, BPO source files) in precedence order:
#: a statement is written by the first module whose sources make it.
SECTIONS = {
    1: "Develop Vision and Strategy",
    2: "Develop and Manage Products and Services",
    3: "Market and Sell Products and Services",
    4: "Manage Supply Chain for Physical Products",
    5: "Deliver Services",
    6: "Manage Customer Service",
    7: "Develop and Manage Human Capital",
    8: "Manage Information Technology (IT)",
    9: "Manage Financial Resources",
    10: "Acquire, Construct, and Manage Assets",
    11: "Manage Enterprise Risk, Compliance, Remediation, and Resiliency",
    12: "Manage External Relationships",
    13: "Develop and Manage Business Capabilities",
}


def modules() -> list[tuple[str, str, str, list[str]]]:
    out = [("ontology/bpot.ttl", None, None,
            ["ontology/apqc-ext.ttl", "ontology/capabilities_roles.ttl",
             "ontology/delivery_processes.ttl"])]
    for n, title in SECTIONS.items():
        out.append((
            "ontology/sections/pcf_%d.ttl" % n,
            "Business Process Ontology -- PCF %d.0 %s" % (n, title),
            "Reality layer for APQC PCF category %d.0: the process universals "
            "that pass the bounded-occurrent test, the organization "
            "capabilities, roles and information content entities they use."
            % n,
            ["ontology/slices/apqc_%d_0.ttl" % n]))
    out.append((
        "ontology/catalog.ttl",
        "Business Process Ontology -- APQC PCF catalog",
        "Every row of the APQC Process Classification Framework "
        "(Cross-Industry, v7.4) as a SKOS concept; the dotted hierarchy as "
        "skos:broader. A lossless index of the framework, not a claim about "
        "what exists; process classes point at their row with "
        "designatesProcessType.",
        ["ontology/apqc-catalog.ttl"]))
    out.append((
        "ontology/wiring.ttl",
        "Business Process Ontology -- capability and role wiring",
        "Which capabilities and roles each process requires, and which "
        "processes each capability enables. Generated in BPO from its "
        "judgment tables; an overlay on the section modules.",
        ["ontology/capabilities_wiring.ttl"]))
    return out


def rename(term, namespace: str):
    if isinstance(term, URIRef):
        text = str(term)
        for old in (OLD, OLD_SCHEME):
            if text.startswith(old):
                return URIRef(namespace + text[len(old):])
    return term


def canon(graph: rdflib.Graph, node):
    """A blank node as the frozen set of what it says, recursively."""
    if not isinstance(node, BNode):
        return node
    return frozenset((p, canon(graph, o)) for p, o in graph.predicate_objects(node))


def closure(graph: rdflib.Graph, node, out: list):
    for p, o in graph.predicate_objects(node):
        out.append((node, p, o))
        if isinstance(o, BNode):
            closure(graph, o, out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("source", type=Path, help="a BusinessProcessOntology checkout")
    parser.add_argument("--unchanged", action="store_true",
                        help="S0: none of the PO-approved changes")
    args = parser.parse_args(argv)
    config = project.load()
    namespace, iri_base = config["namespace"], config["iri_base"]

    seen: set = set()
    origin: dict = {}          # new IRI -> first module that wrote about it
    dropped_bridges, dropped_headers, duplicates = [], [], 0
    renamed: dict = {}         # new IRI -> old IRI, every term ported
    kinds: dict = {}           # new IRI -> SSSOM entity type
    labels: dict = {}          # new IRI -> label
    written, graphs = [], []

    for path, title, comment, sources in modules():
        out = rdflib.Graph()
        for prefix, ns in (("bpot", namespace), ("cco", CCO), ("obo", OBO),
                           ("owl", str(OWL)), ("rdfs", str(RDFS)),
                           ("skos", str(SKOS)), ("dcterms", str(DCTERMS)),
                           ("xsd", str(XSD))):
            out.bind(prefix, ns, replace=True)
        target = ROOT / path
        header = URIRef(iri_base if path == "ontology/bpot.ttl"
                        else iri_base + "/" + path[len("ontology/"):-len(".ttl")])
        if path == "ontology/bpot.ttl":
            existing = rdflib.Graph().parse(target)
            for t in existing.triples((header, None, None)):
                out.add(t)
        else:
            out.add((header, RDF.type, OWL.Ontology))
            out.add((header, DCTERMS.title, Literal(title)))
            out.add((header, DCTERMS.license, URIRef("https://opensource.org/licenses/MIT")))
            out.add((header, DCTERMS.creator, Literal(config["licence_holder"])))
            out.add((header, OWL.versionIRI, URIRef(iri_base + "/0.0.0/" + path[len("ontology/"):])))
            out.add((header, OWL.versionInfo, Literal("0.0.0")))
            out.add((header, RDFS.comment, Literal(comment)))

        for source in sources:
            graph = rdflib.Graph().parse(args.source / source)
            for old_header in graph.subjects(RDF.type, OWL.Ontology):
                dropped_headers.append((source, str(old_header)))
                out.add((header, DCTERMS.source, old_header))
                # The release of the framework a module was built from.
                for cited in graph.objects(old_header, DCTERMS.source):
                    if isinstance(cited, Literal):
                        out.add((header, DCTERMS.source, cited))
            headers = set(graph.subjects(RDF.type, OWL.Ontology))
            for s, p, o in sorted(graph, key=lambda t: (str(t[0]), str(t[1]), str(t[2]))):
                if isinstance(s, BNode) or s in headers:
                    continue
                if str(s).startswith(CCO) or str(s).startswith(OBO):
                    dropped_bridges.append((source, s, p, o))
                    continue
                key = (rename(s, namespace), p, canon(graph, o))
                if key in seen:
                    duplicates += 1
                    continue
                seen.add(key)
                triples = [(s, p, o)]
                if isinstance(o, BNode):
                    closure(graph, o, triples)
                for a, b, c in triples:
                    out.add((rename(a, namespace), rename(b, namespace),
                             rename(c, namespace)))
                for term in (s, p, o):
                    new = rename(term, namespace)
                    if new is not term and isinstance(term, URIRef):
                        if renamed.setdefault(str(new), str(term)) != str(term):
                            raise SystemExit("two BPO IRIs map to %s" % new)
                origin.setdefault(str(rename(s, namespace)), path)

        tops = 0
        for scheme in ([] if args.unchanged else
                       list(out.subjects(RDF.type, SKOS.ConceptScheme))):
            for concept in sorted(out.subjects(SKOS.inScheme, scheme)):
                if (concept, SKOS.broader, None) not in out:
                    out.add((scheme, SKOS.hasTopConcept, concept))
                    out.add((concept, SKOS.topConceptOf, scheme))
                    tops += 1
        if tops:
            print("  %s: %d top concept(s) added" % (path, tops))

        for local in () if args.unchanged else RETYPED:
            term = URIRef(namespace + local)
            if (term, RDF.type, OWL.ObjectProperty) in out:
                out.remove((term, RDF.type, OWL.ObjectProperty))
                out.add((term, RDF.type, OWL.AnnotationProperty))
                print("  %s: %s retyped as an annotation property" % (path, local))
        # BPO's slice headers cite the framework without its release, and
        # those of PCF 5 and 6 not at all; every row came from the release
        # the catalog names.
        if not args.unchanged and any(
                out.subject_objects(URIRef(namespace + "apqcSourceText"))):
            out.add((header, DCTERMS.source, Literal(PCF_RELEASE)))
        for local, text in ({} if args.unchanged else DEFINITIONS).items():
            term = URIRef(namespace + local)
            if (term, RDF.type, None) in out:
                out.add((term, SKOS.definition, Literal(text)))
        graphs.append((path, out))

        for s, kind in out.subject_objects(RDF.type):
            if kind in KINDS:
                kinds.setdefault(str(s), KINDS[kind])
        for p in (RDFS.label, SKOS.prefLabel):
            for s, label in out.subject_objects(p):
                labels.setdefault(str(s), str(label))
        target.parent.mkdir(parents=True, exist_ok=True)
        data = out.serialize(format="turtle").encode("utf-8").replace(b"\r\n", b"\n")
        target.write_bytes(data)
        written.append((path, len(out)))

    for path, n in written:
        print("  wrote %-32s %6d triples" % (path, n))
    print("  %d duplicate statement(s) written once (inlined act genera, "
          "recurring roles)" % duplicates)
    print("  %d BPO header(s) replaced" % len(dropped_headers))
    print("  %d statement(s) about upstream terms dropped:" % len(dropped_bridges))
    for source, s, p, o in dropped_bridges:
        print("    %s  %s %s %s" % (source, s, p, o))
    print("  %d BPO IRI(s) renamed" % len(renamed))
    print("  wrote %s, %d row(s)" % (SSSOM, write_mapping(namespace, renamed, kinds, labels)))
    rows = drift(namespace, graphs)
    (ROOT / DRIFT).write_bytes(("\n".join(
        ["\t".join(("term", "property", "module", "value"))]
        + ["\t".join(row) for row in rows]) + "\n").encode("utf-8"))
    print("  wrote %s, %d variant(s) of %d term/property pair(s)"
          % (DRIFT, len(rows), len({row[:2] for row in rows})))
    return 0


#: The ten BPO properties carry rdfs:comment and no skos:definition, which
#: the site refuses. Definitions approved by the PO, 2026-10-26, verbatim;
#: the comments are kept as they were.
DEFINITIONS = {
    "apqcSourceText": "An annotation property that relates an ontology term to the verbatim element description of its source row in a specified release of the APQC Process Classification Framework.",
    "designatesProcessType": "An annotation property that relates an APQC PCF catalog concept to an OWL class representing the Process type or Organization Capability type designated by that concept.",
    "hierarchyID": "An annotation property that relates an ontology term to the dotted-decimal hierarchy identifier assigned to its source row in a particular release of the APQC Process Classification Framework, whose value may change between releases.",
    "pcfID": "An annotation property that relates an ontology term to the unique process element identifier assigned by APQC to its source row, which remains stable across PCF releases while the conceptual meaning of the element remains unchanged.",
    "requiresCapability": "An annotation property that relates a Process class to an Agent Capability class whose instances must be borne by an agent assigned to perform a process of that type.",
    "requiresRole": "An annotation property that relates a Process class to a Role class whose instances must be borne by an agent performing a process of that type in the required capacity.",
    "requiresPermission": "An annotation property that relates a Process class to an Action Permission class whose applicable instances must permit processes of that type for their execution to be authorized.",
    "bearsPermission": "An annotation property that relates a Role class to an Action Permission class whose applicable instances authorize processes performed by agents bearing that Role, subject to the governing regulations.",
    "enablesProcess": "An annotation property that relates an Agent Capability class to a Process class for which bearing an instance of that capability type is a necessary condition for an agent's performance, providing the authored direction of the class-level capability requirement mapping.",
    "routable": "An annotation property whose Boolean value indicates whether a Process class is eligible for routing by the composer to a registered agent, independently of whether a particular agent satisfies the requirements for its execution.",
}

#: BPO declared these owl:ObjectProperty but asserts them only between
#: classes, which OWL reads as punning, not as a class-level requirement.
#: Annotation properties, on the PO's decision of 2026-10-26; instance-level
#: modelling would use CCO's has capability, has agent, permits.
RETYPED = ("requiresCapability", "requiresRole", "requiresPermission")

#: The release every BPO row was taken from: BPO's catalog header, its
#: README and its source spreadsheet all name it.
PCF_RELEASE = "APQC Process Classification Framework (Cross-Industry) v7.4"

DRIFT = "config/annotation-drift.tsv"
DRIFTING = (RDFS.label, SKOS.prefLabel, SKOS.definition, RDFS.comment)


def drift(namespace: str, graphs: list) -> list[tuple[str, str, str, str]]:
    """Every term whose label, definition or comment reads differently in
    different places: each variant with the module it is in.

    BPO's slices each restated the shared terms they used; the copies
    drifted. The values are kept as they are -- choosing one text is the
    architect's -- and listed here, so that a test can hold the set fixed.
    Values are compared with whitespace normalized.
    """
    seen: dict = {}
    for path, graph in graphs:
        for prop in DRIFTING:
            for s, value in graph.subject_objects(prop):
                if str(s).startswith(namespace):
                    text = " ".join(str(value).split())
                    seen.setdefault((str(s), str(prop)), set()).add((path, text))
    rows = []
    for (s, prop), variants in seen.items():
        if len({text for _, text in variants}) > 1:
            for path, text in variants:
                rows.append(("bpot:" + s[len(namespace):],
                             prop.rsplit("#", 1)[-1], path, text))
    return sorted(rows)


SSSOM = "mappings/bpo.sssom.tsv"

#: The SSSOM entity type of each kind of term, as tools/ontology/mappings.py
#: reads it.
KINDS = {
    OWL.Class: "owl class",
    OWL.ObjectProperty: "owl object property",
    OWL.DatatypeProperty: "owl data property",
    OWL.AnnotationProperty: "owl annotation property",
    SKOS.Concept: "skos concept",
    SKOS.ConceptScheme: "skos concept",
}


def write_mapping(namespace: str, renamed: dict, kinds: dict,
                  labels: dict) -> int:
    """Every ported term to the BPO term it was, one row each.

    The checker wants the subject to be a term declared here, so the rows
    run new -> old. A namespace move has no SEMAPV justification of its
    own: UnspecifiedMatching, with the tool and the reason stated.
    """
    head = [
        "# mapping_set_id: https://fandaws.com/ontology/bpot/mappings/bpo",
        "# mapping_set_description: Every term of this ontology to the term of the "
        "Business Process Ontology (Skreen5hot/BusinessProcessOntology, commit "
        "bc64e91) it was ported from. Same term, same local name, new namespace.",
        "# license: https://opensource.org/licenses/MIT",
        "# creator_label:",
        "#   - Aaron Damiano",
        "# mapping_tool: tools/port_from_bpo.py",
        "# curie_map:",
        "#   bpot: %s" % namespace,
        "#   bpo: %s" % OLD,
        "#   apqc: %s" % OLD_SCHEME,
        "#   skos: http://www.w3.org/2004/02/skos/core#",
        "#   semapv: https://w3id.org/semapv/vocab/",
        "\t".join(("subject_id", "subject_label", "predicate_id", "object_id",
                   "mapping_justification", "object_type", "comment")),
    ]
    rows = []
    for new, old in sorted(renamed.items()):
        kind = kinds.get(new)
        if kind is None:
            raise SystemExit("%s is renamed but declared as no term" % new)
        local = new[len(namespace):]
        prefix = "apqc" if old.startswith(OLD_SCHEME) else "bpo"
        rows.append("\t".join((
            "bpot:" + local, labels.get(new, ""), "skos:exactMatch",
            "%s:%s" % (prefix, old.split("#", 1)[1]),
            "semapv:UnspecifiedMatching", kind,
            "namespace move: the same term, ported unchanged")))
    (ROOT / SSSOM).write_bytes(("\n".join(head + rows) + "\n").encode("utf-8"))
    return len(rows)


if __name__ == "__main__":
    sys.exit(main())
