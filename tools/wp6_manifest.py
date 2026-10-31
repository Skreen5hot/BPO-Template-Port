"""What a WP6 state was built and measured with, so it can be rebuilt.

    python tools/wp6_manifest.py STATE TAG BPO_COMMIT INSTRUMENT

The memo of 2026-10-31: the BPO commit, the template revision, the
dependency versions and the validation configuration are recorded for each
state. Writes research/wp6/measure/<STATE>/manifest.tsv, one item per row:

  state        TAG's commit (the content), the BPO commit it was ported
               from, its corpus digest, and INSTRUMENT: the commit of
               this branch that measured it (amendment A3: content from
               the tag, checks from the instrument)
  template     the template revision of the instrument
               (config/template-manifest.json at INSTRUMENT)
  python       the interpreter and every installed distribution, by version
  java, robot  the JVM, and the ROBOT pin with its sha256
  upstream     each pinned upstream: release, commit, artifact digests
  digest       sha256 at INSTRUMENT of every file that decides a finding:
               the checks (tools/), the shapes and their fixtures, config/
               (not the findings register: dispositions, not checks)
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DECIDING = ("tools/", "shapes/", "config/", "requirements-dev.txt")
SKIP = ("config/findings-register.yaml",)  # the dispositions, not the checks


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def main(argv) -> int:
    state, tag, bpo, instrument = argv
    content = git("rev-parse", tag + "^{commit}").strip()
    commit = git("rev-parse", instrument + "^{commit}").strip()
    raw = subprocess.run(["git", "show", "%s:config/corpus-digest.json"
                          % content], cwd=ROOT, capture_output=True).stdout
    merged = json.loads(raw)["merged"]
    rows = [("state", "content_commit", content), ("state", "bpo_commit", bpo),
            ("state", "corpus_digest_file", hashlib.sha256(raw).hexdigest()),
            ("state", "corpus_ground_sha256", merged["ground_sha256"]),
            ("state", "corpus_blank_node_shape_sha256",
             merged["blank_nodes"]["shape_sha256"]),
            ("state", "corpus_triples", str(merged["triples"])),
            ("state", "instrument_commit", commit)]
    manifest = json.loads(git("show", "%s:config/template-manifest.json"
                              % commit))
    for key in ("label", "template_commit", "template_repository", "digest"):
        rows.append(("template", key, str(manifest.get(key, ""))))
    rows.append(("python", "version", platform.python_version()))
    for dist in sorted(metadata.distributions(),
                       key=lambda d: d.metadata["Name"].lower()):
        rows.append(("python", dist.metadata["Name"], dist.version))
    java = subprocess.run(["java", "-version"], capture_output=True,
                          text=True).stderr.splitlines()
    rows.append(("java", "version", java[0] if java else "not found"))
    reasoning = yaml.safe_load(git("show", "%s:config/reasoning.yaml"
                                   % commit))
    rows.append(("robot", reasoning["robot"]["version"],
                 reasoning["robot"]["sha256"]))
    rows.append(("robot", "reasoner", reasoning["reasoner"]))
    pins = yaml.safe_load(git("show", "%s:config/upstream-sources.yaml"
                              % commit))
    for src in pins.get("sources") or []:
        rows.append(("upstream", src["id"], "%s %s" % (
            src.get("release", ""), src.get("commit", ""))))
        for f in src.get("files") or ([src] if src.get("url") else []):
            rows.append(("upstream", "%s file" % src["id"], "%s %s" % (
                f.get("path", f.get("url", "")), f.get("sha256", ""))))
    for path in sorted(git("ls-tree", "-r", "--name-only", commit, "--",
                           *DECIDING).split()):
        if path in SKIP:
            continue
        blob = subprocess.run(["git", "show", "%s:%s" % (commit, path)],
                              cwd=ROOT, capture_output=True).stdout
        rows.append(("digest", path, hashlib.sha256(blob).hexdigest()))
    out = ROOT / "research" / "wp6" / "measure" / state / "manifest.tsv"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("kind\titem\tvalue\n" + "".join(
        "\t".join(str(c).replace("\t", " ") for c in r) + "\n" for r in rows),
        encoding="utf-8", newline="\n")
    print("  %s: %d row(s) -> %s" % (state, len(rows), out.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
