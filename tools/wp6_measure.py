"""Measure one evaluation state with the instrument on this branch (WP6).

    python tools/wp6_measure.py STATE TAG

STATE names the output folder, research/wp6/measure/<STATE>/; TAG is the
state's git tag (s0, s1, s2).

Amendment A3: the instrument does not change content. The state's ontology,
mapping set and drift inventory are checked out from TAG into this working
tree, and before anything is measured the corpus digest the instrument
computes must equal the one committed at TAG, and the files must be
byte-identical to TAG's. Then every check of the instrument runs, each
timed, and each finding is written by the identity the findings register
uses (check, where, focus, rule, digest, severity), so states compare
finding by finding rather than by count.

The working tree is restored to HEAD's content at the end, and checked.

Writes:
  findings.tsv   every finding of validate.py and iri_lint.py, by identity
  checks.tsv     every check: exit code, seconds, last line of output
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "ontology"))

CONTENT = ["ontology", "mappings", "config/annotation-drift.tsv"]
DIGEST = "config/corpus-digest.json"
PY = sys.executable


def git(*args, check=True) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=check).stdout


def run(name: str, args: list[str], rows: list, timeout=7200):
    start = time.monotonic()
    try:
        done = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8",
                              errors="replace")
        code, out = done.returncode, (done.stdout + done.stderr)
    except subprocess.TimeoutExpired:
        code, out = "timeout", ""
    seconds = time.monotonic() - start
    last = [line.strip() for line in out.splitlines() if line.strip()]
    rows.append((name, str(code), "%.1f" % seconds,
                 (last[-1] if last else "").replace("\t", " ")[:200]))
    print("  %-22s exit %-7s %7s s  %s" % rows[-1], flush=True)
    return code, out


def same_as_tag(tag: str) -> list[str]:
    """What differs between the working tree's content and TAG's."""
    problems = []
    diff = git("diff", "--name-only", tag, "--", *CONTENT, DIGEST)
    if diff.strip():
        problems.append("differs from %s: %s" % (tag, diff.split()))
    untracked = git("ls-files", "--others", "--exclude-standard", "--",
                    *CONTENT)
    if untracked.strip():
        problems.append("untracked content: %s" % untracked.split())
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "digest.json"
        subprocess.run([PY, "tools/ontology/corpus_digest.py", "-o",
                        str(out)], cwd=ROOT, capture_output=True, check=True)
        measured = json.loads(out.read_text(encoding="utf-8"))
        committed = json.loads(git("show", "%s:%s" % (tag, DIGEST)))
        if measured != committed:
            problems.append("the instrument's corpus digest differs from "
                            "the one committed at %s" % tag)
    return problems


def main(argv) -> int:
    state, tag = argv[0], argv[1]
    out_dir = ROOT / "research" / "wp6" / "measure" / state
    out_dir.mkdir(parents=True, exist_ok=True)
    head = git("rev-parse", "HEAD").strip()
    if git("status", "--porcelain", "--", *CONTENT, DIGEST).strip():
        raise SystemExit("uncommitted changes to the content; refusing")

    git("checkout", tag, "--", *CONTENT, DIGEST)
    try:
        problems = same_as_tag(tag)
        if problems:
            raise SystemExit("A3 refused: " + "; ".join(problems))
        print("  %s: content byte-identical to %s (%s); corpus digest equal"
              % (state, tag, git("rev-parse", tag + "^{commit}").strip()[:12]))

        rows: list = []
        found: list = []
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "validation.json"
            # The Checks job's steps, in its order; validate.py --gate is
            # the measured run below, judged against the register after.
            run("project", [PY, "tools/project.py", "--check"], rows)
            run("layout", [PY, "tools/layout.py"], rows)
            run("disposition_all", [PY, "tools/licensing/disposition.py"],
                rows)
            run("vendor_upstream", [PY, "tools/ontology/vendor_upstream.py"],
                rows)
            run("validate", [PY, "tools/ontology/validate.py", "-o",
                             str(report)], rows)
            import validate
            record = json.loads(report.read_text(encoding="utf-8"))
            found += validate.register_findings(record)
            problems, verdict = validate.gate(record, validate.findings.load())
            rows.append(("validate_gate", "0" if not problems and
                         verdict["passed"] else "1", "0.0",
                         "%d new, %d stale, %d structural problem(s)"
                         % (len(verdict["new"]), len(verdict["stale"]),
                            len(problems))))
            print("  %-22s exit %-7s %7s s  %s" % rows[-1], flush=True)

            code, text = run("iri_lint", [PY, "tools/ontology/iri_lint.py",
                                          "--output", "json"], rows)
            import iri_lint
            lint = json.loads(text[text.index("{"):])
            found += iri_lint.register_findings(
                lint.get("violations", []), ROOT)

            run("reason", [PY, "tools/ontology/reason.py", "-o",
                           str(Path(tmp) / "reasoning.json")], rows)
            run("competency", [PY, "tools/ontology/competency.py"], rows)
            run("mappings", [PY, "tools/ontology/mappings.py"], rows)
            run("profile_shapes", [PY, "tools/ontology/profile_shapes.py",
                                   "--check"], rows)
            run("vocabulary", [PY, "tools/ontology/vocabulary.py",
                               "--check"], rows)
            run("protege", [PY, "tools/ontology/protege.py", "--check"], rows)
            run("normalize", [PY, "tools/ontology/normalize.py", "--check"],
                rows)
            run("disposition", [PY, "tools/licensing/disposition.py",
                                "--check"], rows)
            run("third_party", [PY, "tools/licensing/third_party.py"], rows)
            run("findings", [PY, "tools/findings.py"], rows)
            run("communications", [PY, "tools/communications.py"], rows)
            run("template_status", [PY, "tools/template_status.py",
                                    "--check"], rows)
            run("site_build", [PY, "tools/site/build_site.py", "-o",
                               str(Path(tmp) / "_site")], rows)
            run("site_check", [PY, "tools/site/check_site.py",
                               str(Path(tmp) / "_site")], rows)
            run("release", [PY, "tools/release.py", "--version", "0.0.0",
                            "--out", str(Path(tmp) / "release")], rows)
            reasoning = Path(tmp) / "reasoning.json"
            if reasoning.is_file():
                (out_dir / "reasoning.txt").write_text(
                    reasoning.read_text(encoding="utf-8"), encoding="utf-8",
                    newline="\n")

        keys = ("check", "where", "focus", "rule", "digest", "severity",
                "message")
        lines = ["\t".join(keys)] + sorted(
            "\t".join(str(f.get(k, "")).replace("\t", " ").replace("\n", " ")
                      for k in keys) for f in found)
        (out_dir / "findings.tsv").write_text("\n".join(lines) + "\n",
                                              encoding="utf-8", newline="\n")
        (out_dir / "checks.tsv").write_text(
            "\n".join(["\t".join(("check", "exit", "seconds", "last_line"))]
                      + ["\t".join(r) for r in rows]) + "\n",
            encoding="utf-8", newline="\n")
        print("  %d finding(s) -> %s" % (len(found), out_dir.relative_to(ROOT)))
    finally:
        git("checkout", head, "--", *CONTENT, DIGEST)
        if git("status", "--porcelain", "--", *CONTENT, DIGEST).strip():
            print("  WARNING: content not restored to HEAD", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
