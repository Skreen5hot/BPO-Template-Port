"""Try one candidate change in BPO itself, without committing it (WP6 Phase B).

    python tools/wp6_backport_trial.py BPO_CHECKOUT COMMIT CANDIDATE [corpus]

With `corpus`, only corpus_check.sh runs, written to <CANDIDATE>.corpus.tsv.

The memo of 2026-10-31: the back-port candidates are evaluated as candidate
improvements before anything is changed in BPO, and B6 against BPO's own
SHACL C5-C7. This makes a scratch worktree of BPO at COMMIT, applies one
candidate to it, runs BPO's own gates there, and writes what they said to
research/wp6/phase-b/trials/<CANDIDATE>.tsv. BPO's branches are untouched;
the worktree is removed after.

Candidates, each the change the port applies (tools/port_from_bpo.py), in
BPO's namespace:

  none   nothing: the baseline every other trial is read against
  b3     dct:source naming release 7.4 on every module with APQC text
  b5     the PO's skos:definition on each of BPO's ten properties
  b6     requiresCapability/Role/Permission typed owl:AnnotationProperty
  b12    skos:hasTopConcept / topConceptOf for the 13 PCF categories
  b13    the 216 redundant asserted parents removed
         (research/wp6/phase-b/b13-parents.tsv)

The gates (CLAUDE.md of BPO, "Validation"): Gates A-D on each of the 13
slices; corpus_check.sh (ELK over the corpus, then Gate F); validate_caps.py
(C1-C7); matchability.py; consistency_audit.py. A changed file is
re-serialized by rdflib: its formatting changes, its statements only as
the candidate says.
"""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import port_from_bpo  # noqa: E402

BPO = "https://fandaws.com/ontology/bpo#"
PORT = "https://fandaws.com/ontology/bpot#"
CCO = "https://www.commoncoreontologies.org/"
OBO = "http://purl.obolibrary.org/obo/"
#: Git for Windows' bash: a bare `bash` can resolve to WSL's, which has
#: neither this Python nor a path to a Windows worktree's .git.
BASH = ("C:/Program Files/Git/bin/bash.exe"
        if os.name == "nt" else "bash")
IGNORED = ["vendor/cco/CommonCoreOntologiesMerged.ttl", "tools/robot.jar"]


def bpo_files(wt: Path) -> list[Path]:
    return sorted((wt / "ontology").glob("*.ttl")) + sorted(
        (wt / "ontology" / "slices").glob("apqc_*_0.ttl"))


def rewrite(path: Path, change) -> bool:
    g = Graph()
    g.parse(path)
    before = len(g)
    snapshot = set(g)
    change(g)
    if set(g) == snapshot:
        return False
    g.serialize(path, format="turtle")
    print("    %s: %d -> %d statement(s)" % (path.name, before, len(g)))
    return True


def expand(curie: str) -> URIRef:
    prefix, local = curie.split(":", 1)
    return URIRef({"bpot": BPO, "cco": CCO, "obo": OBO}[prefix] + local)


def apply(candidate: str, wt: Path) -> None:
    files = bpo_files(wt)
    if candidate == "none":
        return
    if candidate == "b6":
        def change(g):
            for local in port_from_bpo.RETYPED:
                t = URIRef(BPO + local)
                if (t, RDF.type, OWL.ObjectProperty) in g:
                    g.remove((t, RDF.type, OWL.ObjectProperty))
                    g.add((t, RDF.type, OWL.AnnotationProperty))
    elif candidate == "b5":
        def change(g):
            for local, text in port_from_bpo.DEFINITIONS.items():
                t = URIRef(BPO + local)
                if (t, RDF.type, None) in g:
                    g.add((t, SKOS.definition, Literal(text)))
    elif candidate == "b3":
        def change(g):
            if any(g.subject_objects(URIRef(BPO + "apqcSourceText"))):
                for header in g.subjects(RDF.type, OWL.Ontology):
                    g.add((header, DCTERMS.source,
                           Literal(port_from_bpo.PCF_RELEASE)))
    elif candidate == "b12":
        def change(g):
            for scheme in list(g.subjects(RDF.type, SKOS.ConceptScheme)):
                for c in list(g.subjects(SKOS.inScheme, scheme)):
                    if (c, SKOS.broader, None) not in g:
                        g.add((scheme, SKOS.hasTopConcept, c))
                        g.add((c, SKOS.topConceptOf, scheme))
    elif candidate == "b13":
        table = ROOT / "research" / "wp6" / "phase-b" / "b13-parents.tsv"
        with open(table, encoding="utf-8", newline="") as f:
            gone = {(expand(r["class"]), expand(r["parent"]))
                    for r in csv.DictReader(f, delimiter="\t")
                    if r["status"] == "redundant"}

        def change(g):
            for c, p in gone:
                g.remove((c, RDFS.subClassOf, p))
    else:
        raise SystemExit("unknown candidate %r" % candidate)
    changed = [f for f in files if rewrite(f, change)]
    if not changed:
        raise SystemExit("the candidate changed no file")


def run(name, args, wt, rows, env, logs):
    start = time.monotonic()
    done = subprocess.run(args, cwd=wt, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env)
    logs.append("===== %s (exit %s)\n%s%s" % (name, done.returncode,
                                              done.stdout, done.stderr))
    out = (done.stdout + done.stderr).strip().splitlines()
    tail = " / ".join(line.strip() for line in out[-3:])
    rows.append((name, str(done.returncode),
                 "%.0f" % (time.monotonic() - start), tail.replace("\t", " ")))
    print("  %-28s exit %s  %s" % (name, done.returncode, tail[:150]),
          flush=True)


def main(argv) -> int:
    bpo, commit, candidate = Path(argv[0]).resolve(), argv[1], argv[2]
    only_corpus = argv[3:] == ["corpus"]
    wt = Path(tempfile.mkdtemp(prefix="bpo-trial-")) / "bpo"
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(wt),
                    commit], cwd=bpo, check=True)
    try:
        for rel in IGNORED:
            shutil.copy2(bpo / rel, wt / rel)
        print("  %s at %s, candidate %s" % (wt, commit, candidate))
        # A Windows checkout gives the shell scripts CRLF endings, which
        # bash refuses; the scratch copy's scripts are made LF, nothing else.
        for script in (wt / "scripts").glob("*.sh"):
            script.write_bytes(script.read_bytes().replace(b"\r\n", b"\n"))
        apply(candidate, wt)
        env = dict(os.environ, PYTHONPATH="src", PYTHONIOENCODING="utf-8")
        py = sys.executable
        rows: list = []
        logs: list = []
        for n in range(1, 0 if only_corpus else 14):
            run("gates A-D slice %d" % n,
                [py, "-m", "apqc_transform.validate",
                 "ontology/slices/apqc_%d_0.ttl" % n], wt, rows, env, logs)
        run("corpus_check (ELK, Gate F)", [BASH, "scripts/corpus_check.sh"],
            wt, rows, env, logs)
        if not only_corpus:
            run("validate_caps (C1-C7)", [py, "scripts/validate_caps.py"],
                wt, rows, env, logs)
            run("matchability", [py, "scripts/matchability.py"], wt, rows,
                env, logs)
            run("consistency_audit", [py, "scripts/consistency_audit.py"],
                wt, rows, env, logs)
        diff = subprocess.run(["git", "diff", "--stat", "--", "ontology"],
                              cwd=wt,
                              capture_output=True, text=True).stdout.strip()
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=bpo)
        shutil.rmtree(wt.parent, ignore_errors=True)
    out = ROOT / "research" / "wp6" / "phase-b" / "trials"
    out.mkdir(parents=True, exist_ok=True)
    name = candidate + (".corpus" if only_corpus else "")
    (out / ("%s.tsv" % name)).write_text(
        "# BPO %s, candidate %s\n# %s\n" % (
            commit, candidate, (diff.splitlines() or ["no change"])[-1])
        + "gate\texit\tseconds\tlast_lines\n"
        + "".join("\t".join(r) + "\n" for r in rows),
        encoding="utf-8", newline="\n")
    (out / ("%s.log.txt" % name)).write_text(
        "\n".join(logs), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
