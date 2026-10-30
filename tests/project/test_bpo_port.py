# SPDX-License-Identifier: MIT
"""What the port of the Business Process Ontology must keep true.

Project-owned, not the template's: the conditions the PO set on 2026-10-26
when approving the property definitions (research/port-report.md, section
6). Each test reads the modules as they stand.
"""

from __future__ import annotations

import glob

import pytest
import rdflib
from rdflib import XSD, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS

from conftest import ROOT, load_tool

#: BPO's ten properties: all relate classes to classes, or classes to
#: literals, so none may be an object property.
PROPERTIES = ("apqcSourceText", "designatesProcessType", "hierarchyID",
              "pcfID", "requiresCapability", "requiresRole",
              "requiresPermission", "bearsPermission", "enablesProcess",
              "routable")


@pytest.fixture(scope="module")
def port():
    return load_tool("t_port", "tools/port_from_bpo.py")


@pytest.fixture(scope="module")
def modules():
    return [(path[len(str(ROOT)) + 1:].replace("\\", "/"),
             rdflib.Graph().parse(path))
            for path in sorted(glob.glob(str(ROOT / "ontology" / "*.ttl"))
                               + glob.glob(str(ROOT / "ontology" / "sections" / "*.ttl")))]


@pytest.fixture(scope="module")
def merged(modules):
    graph = rdflib.Graph()
    for _, module in modules:
        graph += module
    return graph


@pytest.fixture(scope="module")
def ns(project):
    return rdflib.Namespace(project.namespace())


@pytest.mark.parametrize("local", PROPERTIES)
def test_each_bpo_property_is_an_annotation_property(merged, ns, local):
    kinds = set(merged.objects(ns[local], RDF.type))
    assert kinds == {OWL.AnnotationProperty}, (local, kinds)


@pytest.mark.parametrize("local", PROPERTIES)
def test_each_bpo_property_carries_its_approved_definition(merged, ns, port, local):
    assert list(merged.objects(ns[local], SKOS.definition)) == [
        Literal(port.DEFINITIONS[local])]


def test_no_object_property_is_minted_here(merged, ns):
    # A class-to-class requirement as an object property is punning; the
    # instance-level relations are CCO's (has capability, has agent, permits).
    minted = [s for s in merged.subjects(RDF.type, OWL.ObjectProperty)
              if str(s).startswith(str(ns))]
    assert minted == []


def test_requires_capability_is_exactly_the_mirror_of_enables_process(merged, ns):
    # enablesProcess is authored; requiresCapability is derived from it by
    # a transformation rule, not an owl:inverseOf (annotation properties
    # have no inverses). Neither may hold a pair the other lacks.
    enabled = {(process, capability) for capability, process
               in merged.subject_objects(ns.enablesProcess)}
    required = set(merged.subject_objects(ns.requiresCapability))
    assert enabled and enabled == required, (
        sorted(enabled - required)[:5], sorted(required - enabled)[:5])


def test_every_routable_value_is_a_boolean(merged, ns):
    values = list(merged.objects(None, ns.routable))
    assert values
    assert all(isinstance(v, Literal) and v.datatype == XSD.boolean
               for v in values), values


def test_the_catalog_names_the_pcf_release_it_was_built_from(modules):
    catalog = dict(modules)["ontology/catalog.ttl"]
    header = next(catalog.subjects(RDF.type, OWL.Ontology))
    cited = {str(v) for v in catalog.objects(header, DCTERMS.source)
             if isinstance(v, Literal)}
    assert "APQC Process Classification Framework (Cross-Industry) v7.4" in cited


def test_every_source_description_is_in_a_module_that_names_the_release(modules, ns, port):
    # apqcSourceText is defined as the text of a row "in a specified
    # release"; the release is specified by the module that holds it.
    holding = [(path, module) for path, module in modules
               if any(module.subject_objects(ns.apqcSourceText))]
    assert holding
    for path, module in holding:
        header = next(module.subjects(RDF.type, OWL.Ontology))
        assert Literal(port.PCF_RELEASE) in set(
            module.objects(header, DCTERMS.source)), path


def test_the_drift_is_exactly_the_recorded_drift(modules, ns, port):
    # Carried over from BPO and kept as it was: one row per variant. A new
    # variant fails; so does a harmonization until the file is regenerated,
    # so the reduction shows in a diff.
    recorded = (ROOT / port.DRIFT).read_bytes().decode("utf-8").splitlines()[1:]
    recorded = {tuple(line.split("\t")) for line in recorded if line}
    now = set(port.drift(str(ns), modules))
    assert now == recorded, (sorted(now - recorded)[:5],
                             sorted(recorded - now)[:5])


def test_the_drift_check_finds_drift(port, ns):
    # The check above could pass by finding nothing. Two modules that say
    # different things about one term must be reported, variant by variant.
    term = URIRef(str(ns) + "Example")
    a, b = rdflib.Graph(), rdflib.Graph()
    a.add((term, RDFS.comment, Literal("One reading.")))
    b.add((term, RDFS.comment, Literal("Another  reading.")))
    c = rdflib.Graph()
    c.add((term, RDFS.comment, Literal("One   reading.")))
    rows = port.drift(str(ns), [("a.ttl", a), ("b.ttl", b), ("c.ttl", c)])
    assert {row[2] for row in rows} == {"a.ttl", "b.ttl", "c.ttl"}
    assert {row[3] for row in rows} == {"One reading.", "Another reading."}
    assert port.drift(str(ns), [("a.ttl", a), ("c.ttl", c)]) == []
