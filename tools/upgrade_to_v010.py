"""Upgrade this project from the template it was made from (2455bcc) to v0.1.0.

WP6 Phase A, step 2. The template documents no upgrade procedure, and
tools/template_status.py --against reports only the files the template
declares `owned`. The checks a project runs are partly in files it
declares the project's own (the shapes and their fixtures, the annotation
profile, the naming and reasoning configuration), so those are merged here
too, from the template's history.

Every file the template changed between the two commits is merged three
ways:

  base    the old template's file as init made it for this project
          (2455bcc's own init transforms, applied with this project's values)
  ours    the file in this repository
  theirs  v0.1.0's file under the same transforms (v0.1.0's init)

ours == base: theirs is taken. ours == theirs: nothing to do. Otherwise
git merge-file, and a conflict is reported, never resolved here, unless
DECIDED names the file with the decision that resolves it.

Run from the repository root:

    python tools/upgrade_to_v010.py OLD_TREE NEW_TREE [--write]

OLD_TREE and NEW_TREE are checkouts of the template at 2455bcc and
ee4353d (v0.1.0). Without --write it reports and writes nothing.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

OLD_COMMIT = "2455bcc"
NEW_COMMIT = "ee4353d"

#: Files the merge does not decide, with the decision that does.
DECIDED = {
    "tools/ontology/validate.py": (
        "theirs",
        "our patch (056403f, inlining an IRI focus node) gives way to "
        "v0.1.0's T1 fix, tools/ontology/sparql_constraints.py, as our "
        "WP6 answer said"),
    "config/template-manifest.json": (
        "theirs",
        "the record of what the project is made from: after the upgrade, "
        "v0.1.0"),
    "config/validation-baseline.json": (
        "remove",
        "v0.1.0 replaces the per-rung count with config/findings-register.yaml "
        "(decision 11); the 57 accepted drift findings are re-entered there "
        "by identity, in their own commit"),
}

#: Generated files: regenerated after the merge, never merged.
GENERATED = ("config/corpus-digest.json", "config/upstream-extracts.json")

SKELETONS = {"README.md": "README.md", "CLAUDE.md": "CLAUDE.md",
             "docs/HANDOFF.md": "HANDOFF.md", "CITATION.cff": "CITATION.cff"}


def load(tree: Path, name: str):
    sys.path.insert(0, str(tree / "tools"))
    try:
        for cached in ("layout", "project"):
            sys.modules.pop(cached, None)
        spec = importlib.util.spec_from_file_location(
            name, tree / "tools" / "init_project.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        layout = sys.modules["layout"]
        return module, layout
    finally:
        sys.path.pop(0)


def changed(tree: Path) -> list[tuple[str, str]]:
    out = subprocess.run(
        ["git", "-C", str(tree), "diff", "--no-renames", "--name-status",
         OLD_COMMIT, NEW_COMMIT], capture_output=True, text=True, check=True)
    return [tuple(line.split("\t", 1)) for line in out.stdout.splitlines()]


def components(tree: Path):
    import yaml
    data = yaml.safe_load((tree / "config/repository-layout.yaml")
                          .read_text(encoding="utf-8"))
    return data["components"]


def under(path: str, prefixes) -> bool:
    return any(path == p or path.startswith(p + "/") for p in prefixes)


def main(argv: list[str]) -> int:
    old_tree, new_tree = Path(argv[0]), Path(argv[1])
    write = "--write" in argv
    root = Path.cwd()
    import yaml

    old_init, _ = load(old_tree, "old_init")
    new_init, _ = load(new_tree, "new_init")

    old_vals = yaml.safe_load((old_tree / "config/project.yaml").read_text(
        encoding="utf-8"))
    ours_vals = yaml.safe_load((root / "config/project.yaml").read_text(
        encoding="utf-8"))
    for vals in (old_vals, ours_vals):
        vals["iri_base"] = vals["namespace"].rstrip("#")
    new_vals = dict(old_vals)
    new_vals.update({k: ours_vals[k] for k in (
        "template", "id", "code", "title", "description", "namespace",
        "prefix", "iri_base", "repository", "licence_holder")})
    new_vals["correspondents"] = []

    template_only = {c["path"] for tree in (old_tree, new_tree)
                     for c in components(tree) if c.get("template") == "only"}
    turtle_paths = set()
    for tree in (old_tree, new_tree):
        for c in components(tree):
            if c.get("role") in old_init.TURTLE_ROLES:
                turtle_paths.add(c["path"])
    init_date = "2026-10-24"

    def instantiate(init, tree: Path, path: str):
        f = tree / path
        if not f.is_file():
            return None
        text = f.read_bytes().decode("utf-8")
        if path == "config/project.yaml":
            return init.project_file(text, new_vals)
        if path == "config/repository-layout.yaml":
            text = text.replace("    path: ontology/example.ttl\n",
                                "    path: ontology/%s.ttl\n" % new_vals["id"])
            return init.without_template_block(text)
        if path in SKELETONS:
            skeleton = tree / init.SKELETONS / SKELETONS[path]
            if not skeleton.is_file():
                return None
            rendered = init.render(skeleton.read_text(encoding="utf-8"),
                                   new_vals, "ontology/%s.ttl" % new_vals["id"],
                                   old_vals["repository"])
            return rendered.replace(dt.date.today().isoformat(), init_date)
        if under(path, turtle_paths) and path.endswith(".ttl"):
            return init.turtle(text, old_vals, new_vals)
        return text

    paths = sorted({p for _, p in changed(new_tree)} | set(SKELETONS))
    report = {"taken": [], "same": [], "merged": [], "conflict": [],
              "decided": [], "skipped": [], "removed": []}
    for path in paths:
        if under(path, template_only) and path not in SKELETONS:
            report["skipped"].append((path, "template only"))
            continue
        if under(path, ["communications"]) and not under(
                path, ["communications/" + c.lower()
                       for c in ours_vals.get("correspondents") or []]):
            report["skipped"].append(
                (path, "the template's own correspondence; init removes it"))
            continue
        if path in GENERATED:
            report["skipped"].append((path, "generated; regenerated after"))
            continue
        base = instantiate(old_init, old_tree, path)
        theirs = instantiate(new_init, new_tree, path)
        target = root / path
        ours = target.read_bytes().decode("utf-8") if target.is_file() else None

        if path in DECIDED:
            how, why = DECIDED[path]
            report["decided"].append((path, how, why))
            if write:
                if how == "remove":
                    target.unlink(missing_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(theirs.encode("utf-8"))
            continue
        if ours == theirs:
            report["same"].append(path)
            continue
        if ours == base:
            if theirs is None:
                report["removed"].append(path)
                if write:
                    target.unlink()
            else:
                report["taken"].append(path)
                if write:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(theirs.encode("utf-8"))
            continue
        if ours is None or base is None or theirs is None:
            report["conflict"].append(
                (path, "present: base=%s ours=%s theirs=%s" % (
                    base is not None, ours is not None, theirs is not None)))
            continue
        with tempfile.TemporaryDirectory() as tmp:
            files = []
            for name, text in (("ours", ours), ("base", base),
                               ("theirs", theirs)):
                f = Path(tmp) / name
                f.write_bytes(text.encode("utf-8"))
                files.append(str(f))
            run = subprocess.run(["git", "merge-file", "-p", "-L", "ours",
                                  "-L", "base", "-L", "theirs", *files],
                                 capture_output=True)
            if run.returncode == 0:
                report["merged"].append(path)
                if write:
                    target.write_bytes(run.stdout)
            else:
                report["conflict"].append(
                    (path, "%d conflict(s)" % run.returncode))
                if write:
                    target.write_bytes(run.stdout)

    for key, items in report.items():
        print("%s: %d" % (key, len(items)))
        for item in items:
            print("    " + (" | ".join(item) if isinstance(item, tuple)
                            else item))
    if not write:
        print("(dry run: nothing written)")
    return 1 if report["conflict"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
