# Port report: Business Process Ontology onto the Ontology Template

Fill this in as you go. Write "none" rather than leaving a section empty, so we
can tell nothing happened from nothing recorded. Commands to run are given where a
figure can be measured instead of estimated.

## 1. Setup

| | |
|---|---|
| Source ontology | Business Process Ontology, `Skreen5hot/BusinessProcessOntology` at commit `bc64e91839378e1926189c01bf184d6a22d5c1b7` |
| New repository | `Skreen5hot/BPO-Template-Port` (private). The form names `Skreen5hot/Business-Process-Ontology`; the name was agreed with the PO before the form arrived, see §7 |
| Template commit used | `2455bcc84b9299a4ad6967dd2e6f6fc908939ff4` (template `main` HEAD at copy time; manifest digest `f1412848…3424c63`). `config/template-manifest.json` carries no commit sha, see §7 |
| Who did the port | BPO developer (Claude Code agent), with Aaron Damiano (lead architect / PO) answering questions. Had not seen the template before; the README was deliberately not read until the repository existed |
| AI assistance used | Claude Code (Claude Opus 5.5) did the whole port: commands, porting scripts, this report |

Agreed before starting: namespace id `bpot` (`https://fandaws.com/ontology/bpot#`); scope is the full
corpus (13 slices, `apqc-ext`, catalog, shapes, capability layer, delivery processes), and the BPO Python
pipeline (`src/apqc_transform`, `scripts/`) is not ported; timebox 3 working days; targets: first green CI
in 2 hours, complete port in 2 days.

## 2. Clock

Local time (EDT, UTC−4) at each milestone. Leave a milestone blank if you never reached it,
and say why in §8.

| Milestone | Date and time | Notes |
|---|---|---|
| Started: clicked "Use this template" | 2026-10-24 13:17 | `gh repo create --template` |
| `tools/init_project.py` ran cleanly | 2026-10-24 13:23 | Clean on first run (dry run first). Fetched BFO/CCO, regenerated, recorded baseline. ~1 min |
| First green CI run (before any ontology content) | | |
| Pages enabled and the site live | | |
| All classes ported | | |
| All properties and axioms ported | | |
| Validation gate green (`tools/ontology/validate.py --gate`) | | |
| Reasoner green (Reasoning workflow) | | |
| Everything green, port complete | | |

Hands-on time in total, excluding waiting: ___ hours.

## 3. Coverage: did everything come across?

| | Source | Ported |
|---|---|---|
| Classes | | |
| Object properties | | |
| Data properties | | |
| Annotation properties | | |
| Logical axioms (subClassOf, equivalence, disjointness, restrictions) | | |

Source counts: from the source repository's own tooling or a reasoner report.
Ported counts: the site's `data/terms.json` (`counts`), and
`python tools/ontology/corpus_digest.py`.

Mapping set: `mappings/<file>.sssom.tsv`, ___ rows; `python tools/ontology/mappings.py`
passes: yes / no.

**Terms not carried over, or changed in meaning.** One row each.

| Old IRI | What happened | Why |
|---|---|---|
| | dropped / merged / split / re-parented / redefined | |

## 4. What the checks found

Run each one on the ported ontology before fixing anything, and record the first
result. Then classify every finding.

| Check | Command | Findings on first run |
|---|---|---|
| Validation ladder | `python tools/ontology/validate.py` | |
| IRI linter | `python tools/ontology/iri_lint.py` | |
| Reasoner | `python tools/ontology/reason.py` | |
| Competency questions | `python tools/ontology/competency.py` | |

Each finding gets one row. **Class** is one of: *real* (a defect in the source
ontology), *false alarm* (the check is wrong here), *template bug* (the check or
tool is broken), *unsure*.

| Check | Term | Finding (as printed) | Class | What you did |
|---|---|---|---|---|
| | | | | |

## 5. Template files you changed

The output of `python tools/template_status.py` at the end, pasted whole:

```
```

For each file it lists:

| File | What you changed | Why the template did not work as it was |
|---|---|---|
| | | |

## 6. Questions you had to ask

| When | Question | Who answered | Time lost | Was the answer in the docs? |
|---|---|---|---|---|
| 13:17 | Where is the report form? The request says it is attached; it was not, and the template has no `research/port-report.md` | Aaron (sent the form at 13:20) | ~0 (kept going, drafted structure meanwhile) | no (process gap in the request, not the template) |

## 7. Friction log

Every point where you got stuck, guessed, worked around something, or were
surprised, including small ones. One line each, as it happens.

| When | Where (file, command, doc section) | What happened | Time lost |
|---|---|---|---|
| 13:17 | request / `research/` | Report form not attached to the request and not in the template | 0 |
| 13:17 | README "Starting a project" step 1 | Step 1 is the web UI; `gh repo create <name> --template Skreen5hot/Ontology-Template --private --clone` works and isn't mentioned | 0 |
| 13:20 | report form §1 vs `config/template-manifest.json` | Form says to read the template commit from the manifest; the manifest holds file digests and an overall digest, no commit sha. Took the sha from the template's `main` via `gh api` | 2 min |
| 13:20 | report form §1 | Form pre-fills the repo name `Business-Process-Ontology`; the repo had already been created as `BPO-Template-Port` | 0 |
| 13:20 | `requirements-dev.txt` | Installed cleanly with Python 3.12.10 on Windows (Git Bash) | 0 |
| 13:20 | `config/project.yaml` | Says authored terms are "readable local names, not opaque ids"; the README describes the IRI linter as suggesting "the opaque id for a readable name". Which convention the template wants is unclear so far | 0 (noted) |
| 13:21 | README step 3 / `init_project.py` | Init refuses a dirty tree, but the request says to fill `research/port-report.md` as you go. Moved the report out of the tree, ran init, moved it back. `--allow-dirty` exists but the README doesn't mention it, and using it would blur `git diff` | 2 min |
| 13:29 | README step 4, `pytest tests/` | Suite: 1 failed, 298 passed, in **6 min 4 s**. `test_every_tracked_file_has_an_owning_component_or_a_stated_rule` names the 7 files init deleted/renamed (`docs/template/*`, `ontology/example.ttl`): the test reads `git ls-files`, and init changes the disk without staging. **Template bug**: init should `git rm`/`git mv`, or README step 4 should say to stage first. `git add -A`, re-ran the file: 14 passed | 3 min |
| 13:29 | README step 4 | The README gives no suite command for a project; used the one from "Working on the template itself" (`pytest tests/ -q -p no:randomly`). 6 minutes is long for a local loop | 0 |
| 13:30 | README step 5 | Pages enabled through the API, `gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow`; worked on a private repo (site is public). Not in the README, which describes only the web UI | 0 |
| 13:31 | `.githooks/` | README table promises the IRI linter "in a git hook", but `core.hooksPath` is unset after cloning and the README never says to run `git config core.hooksPath .githooks`. The hook is inactive by default | 0 (noted) |

## 8. Overall

- Did you finish within the timebox? If not, where did it stop?
- Would you start your next ontology from this template? Yes / with changes / no, and why.
- The three changes to the template that would have saved you the most time:
  1.
  2.
  3.
- Anything the template made easier than you expected:
