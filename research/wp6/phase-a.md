# WP6 Phase A — record

The BPO Testing Team's record of WP6 Phase A, run on branch `wp6` of this repository under
the protocol as amended by A1 to A7 (template decision 20,
`EXAMPLE-BPOT-2026-10-30-wp6-amendments-decided`). Instrument: template v0.1.0
(`ee4353db68c2c9dc36f6531e7e531123e01316bf`).

Started 2026-10-30 09:44 (America/New_York). Times below are wall clock, the same zone.

## 1. Pins, checked by hand

`tools/pins.py` exists on the template's `main` (`cc64f6d`) but is not in v0.1.0 (A7), so each
pin of the instrument was checked by hand on 2026-10-30, 09:44–09:50, against v0.1.0's files.
Raw output: `research/wp6/pins/`.

| Pin | Pinned | Upstream check | Result |
|---|---|---|---|
| actions/checkout | v7.0.1 `3d3c42e5` | tag resolves to the pinned commit; latest release v7.0.1 | current |
| actions/setup-python | v7.1.0 `6d4fd22b` | tag → pinned commit; latest v7.1.0 | current |
| actions/setup-java | v6.1.0 `b843ebf9` | tag → pinned commit; latest v6.1.0 | current |
| actions/cache | v6.1.0 `55cc8345` | tag → pinned commit; latest v6.1.0 | current |
| actions/configure-pages | v6.0.0 `45bfe019` | tag → pinned commit; latest v6.0.0 | current |
| actions/upload-pages-artifact | v5.0.0 `fc324d35` | tag → pinned commit; latest v5.0.0 | current |
| actions/upload-artifact | v7.0.2 `cf430e03` | tag → pinned commit; latest v7.0.2 | current |
| actions/deploy-pages | v5.0.1 `368f8252` | tag → pinned commit; latest v5.0.1 | current |
| pytest | 9.2.0 | PyPI latest 9.2.0; osv.dev: no advisory at the pin | current |
| PyYAML | 6.0.3 | latest 6.0.3; no advisory | current |
| rdflib | 7.6.0 | latest 7.6.0; no advisory | current |
| pyshacl | 0.40.2 | latest 0.40.2; no advisory | current |
| pyoxigraph | 0.5.13 | latest 0.5.13; no advisory | current |
| Markdown | 3.11.2 | latest 3.11.2; no advisory | current |
| BFO | release-2024-01-29 `044490fc` | tag → pinned commit; no later release | current |
| CCO | v2.0-2024-11-06 `510dad76` | tag → pinned commit; **v2.2 released 2026-08-14** | kept by decision: BPO's own pin, shared with the BCO (CLAUDE.md, "CCO pin") |
| ROBOT | 1.9.11 | tag → pinned `37d514d2`; GitHub's asset digest equals the pinned sha256; latest 1.9.11 | current |

The BFO and CCO artifacts' digests were verified again by `vendor_upstream.py --rebuild` during the
upgrade (§2), which refuses a digest that does not match.

**Not covered by any pin:** the transitive Python dependencies. A clean install of
`requirements-dev.txt` also installed `owlrl 7.6.2`, `html5rdf 1.2.1`, `prettytable 3.18.0`,
`packaging 26.3`, `pyparsing 3.3.3` and others, unpinned. The file's own comment says owlrl is
"not pinned" because nothing imports it; pyshacl does. Finding P-A1.

## 2. The upgrade to v0.1.0 (09:50–10:30)

**The template documents no upgrade procedure** (finding P-A2). `template_status.py --against`
reports only files declared `owned`. A project's checks, though, are partly in files v0.1.0's
layout contract declares the *project's own*: the four shape sets, their three fixtures,
`config/annotation-profile.yaml`, `config/naming.yaml`, and `config/reasoning.yaml`, which
carries the ROBOT pin that decision 18 moved. `--against` therefore said nothing about over 300
changed lines in the checks themselves, or about the reasoner moving from 1.9.10 to 1.9.11
(finding P-A3). A project that follows the documented route keeps the old checks under a new
manifest.

The upgrade was done by `tools/upgrade_to_v010.py`, a three-way merge of every file the
template changed between `2455bcc` and `ee4353d`:

- **base:** the old template, as the old init instantiated it for `bpot`;
- **ours:** the port;
- **theirs:** v0.1.0 under v0.1.0's init.

Result:

- 54 files taken from v0.1.0;
- 2 merged (`config/project.yaml`, the layout contract);
- **0 conflicts**;
- 12 skipped: template-only files, and the template's own correspondence with Legal;
- 3 decided by hand:
  - `validate.py` takes v0.1.0, so our patch `056403f` gives way to `sparql_constraints.py`;
  - the manifest is v0.1.0's;
  - `validation-baseline.json` is removed in favour of the findings register.

Also: `tests/test_bpo_port.py` moved to `tests/project/`, as v0.1.0 provides (T16).

**The ontology did not move.** `git diff s1 -- ontology mappings` is empty. Every generator
rebuilds byte-identical. The corpus digest equals S1's. The port tool, re-run on BPO
`bc64e91`, reproduces S1 byte for byte.

One real finding against our own placement: the suite's research check refused the upgrade
script in `research/`, which holds notes, not code. Moved to `tools/` and declared (correct
behaviour by the template).

Commit `4d111ab`.

## 3. S0 (10:30–10:37)

`tools/port_from_bpo.py --unchanged` on BPO `bc64e91`. It keeps the port's mechanics and
switches off the four PO-approved changes: top concepts, re-typed properties, property
definitions, and the release on every module.

Tagged `s0` at `3690d2a`, built on `s1` so that only the ontology, the mapping set and the
corpus digest differ.

**Lossless check** (`tools/lossless_check.py`, PORTING.md §4's method):

- **S0:** 49,336 = 49,336 statements, **none missing, none extra**.
- **S1:** against the same source, 3 missing (the `owl:ObjectProperty` types) and 39 extra (3
  annotation-property types, 10 definitions, 13 + 13 top-concept links). That is **exactly the
  approved changes**, as the port report recorded on 10-26.

Producing S0 exposed one defect of ours in S1 (G3 in the classification): the three re-typed
properties' SSSOM rows still say "ported unchanged".

## 4. S0 and S1 measured with v0.1.0 (10:37–10:59)

`tools/wp6_measure.py`. Before measuring, each state's ontology, mapping set and drift
inventory were checked out from its tag. Two checks were required to pass first (A3): the
content byte-identical, and the instrument's corpus digest equal to the one committed at the
tag. Both passed for both states. The working tree was restored and checked after each run.

Every finding is recorded by register identity in `research/wp6/measure/<state>/findings.tsv`,
and each check's exit code and time in `checks.tsv`.

| | S0 | S1 |
|---|---:|---:|
| Findings, by identity | **4,323** | **3,749** |
| In both states | 3,749 | 3,749 |
| Only in this state | 574 | **0** |
| Validation violations (wellformedness / realist / SKOS) | 67 / 563 / 1 | 57 / 0 / 0 |
| Warnings (profile / realist / naming) | 3,172 / 480 / 39 | 3,172 / 480 / 39 |
| IRI lint | 1 | 1 |
| Reasoner | consistent, nothing unsatisfiable | same |
| Mappings | 5,051, 0 findings | same |
| Site build and check | pass | pass |
| Release build | **pass, 210 s** | **pass, 145 s** |

**S1 introduces no finding.** The 574 that S1 removes are the PO's changes: 563 class-to-class
object-property assertions (re-typing), 10 properties without a definition, and 1 scheme
without a top concept.

Local times (Windows, Python 3.12.10):

- validation: 109 s (S0), 83 s (S1);
- release build: 210 s (S0), 145 s (S1).

For comparison:

- **The ladder:** at `2455bcc` it did not finish in 1 h 56 min unpatched, and took 35 min
  with our patch.
- **The release build:** it ran 5 h 22 min without finishing.

**T1 and T2 are fixed at BPO scale.**

The figures differ from the Template Team's §3 counts (3,119 + 540 + 57 = 3,716). v0.1.0
measures more:

- comment agreement, 53;
- the placement shape, 563 at S0;
- the configured scheme rule, 39.

The genus check is also broader: every asserted parent must be named, giving 233 where
`2455bcc` gave 13. And the qualifier check reports the label rather than every child: 18,
not 78.

On their corrected figures:

- **T11:** confirmed, **18** qualifier warnings.
- **T23:** confirmed for S0. 14 of the 15 modules holding APQC text name no release; S1 names
  it on all 15. No v0.1.0 check measures this (G1).
- **T10:** "2 used properties in 494 assertions on 453 classes" is not what v0.1.0 reports on
  BPO. It reports 563 placement findings, one per (class, property, class) assertion, at S0.

## 5. BPO's D7 scheme rule (10:37)

`config/naming.yaml` gains `capability-as-process`: a `P[0-9]+` class must not sit under
Organization Capability (`cco:ont00000568`). Severity warning, because BPO's own gate holds
these 39 at baseline rather than failing on them.

**It reproduces BPO Gate F's 39 exactly,** at S0 and S1, and the same 39 IRIs are found
asserted-only and transitively.

BPO's second D7 rule cannot be configured: a non-capability class with a `pcfID` must be
named `P<pcfID>`. It compares a local name with a literal, which a scheme rule cannot state
(finding P-A4). Measured outside the instrument, it holds: 0 at S0 and S1.

Commit `e61ae06`.

## 6. CI on GitHub's standard runner

Both runs were on branch `wp6` at `e61ae06` (S1 content, v0.1.0), dispatched by hand.
Runner `ubuntu-24.04`, image version 20261025.353.1, runner 2.338.0, Python 3.12.15,
Java 21. Private-repository minutes.

| Job | Run 1 (cold) | Run 2 (warm) |
|---|---|---|
| Checks: Contract, licensing, tests | **8 min 41 s** (run 41073682960) | **6 min 46 s** (run 41076561290) |
| of which: install | 5 s | 6 s |
| of which: validation (`--gate`) | 15 s | 12 s |
| of which: IRI lint | 4 s | 3 s |
| of which: site build + check | 16 s | 12 s |
| of which: tests | 7 min 40 s (392 passed, 4 failed) | 5 min 55 s (same) |
| Checks: Extracts rebuild | 19 s | 33 s |
| Reasoning (ROBOT 1.9.11, ELK) | **59 s**, cache miss (run 41073705706) | **64 s**, cache hit (run 41076566073) |
| of which: reasoner on the corpus | 9 s | 14 s |

**Within the 30-minute budget,** at about a quarter of it.

**Fail-fast is gone (T5).** Every check ran, and the verdict step names the three that did not
pass: `validate`, `iri_lint`, `tests`. All three fail for one reason: v0.1.0's findings
register is empty, so every accepted finding is new until it is entered (§8).

**Run 3, with the register filled** (`0f4c5e3`, S1 content; run 41106582545, 18:23:53Z to
18:32:13Z): **green, 8 min 20 s.** The verdict step reads "every check passed". Validation:
3,748 accepted, 0 new, 0 stale. IRI lint: 1 accepted. Tests: 396 passed, 0 failed, in 7 min
12 s, so the 4 earlier test failures were all the empty register. The 3.1 MB register
does not measurably slow the job.

## 7. The explorer (11:00–11:03)

Built from S1 with v0.1.0. The explorer's data (`data/terms.json`) was checked against
`config/annotation-drift.tsv`:

- **All 137 label and definition variants** of the 51 drifted classes are present, each with
  the module(s) it comes from, and each such class carries a conflict note. T7 is fixed.
- **No comment is shown at all.** The explorer has no comment field, so the 129 comment
  variants of 53 terms, which the validator reports (53 warnings), cannot be seen on the site
  (finding P-A5).

**The visual run in a browser:** the BPO architect inspected the explorer in a browser on
2026-10-30 and found it good. This is an inspection, not the fuller evidence planned: no
screenshots, no per-term checklist and no planted conflict were recorded. The data check
above is the per-term evidence.

## 8. Classification (11:03–11:09), approved; register committed 14:21, dispose stage 14:22–14:54

`research/wp6/classification.md`. Every one of the 4,323 S0 findings is in exactly one of 17
classes (`tools/wp6_classify.py`; `measure/s0/classes.tsv`). Each class has a proposed
classification, owner and reason, and six detection gaps are listed.

Proposed:

| Classification | Findings |
|---|---:|
| real | 4,301 |
| upstream | 5 |
| false alarm | 9 |
| unsure | 8 |
| template bug | 0 |

**Approved.** The BPO architect approved every class as proposed, on 2026-10-30 (A5). The
classification is now fixed for S2 (A6).

**The register** (`0f4c5e3`): 3,749 entries, one per S1 finding (validate 3,748, iri_lint 1),
each with its class's classification, reason and owner, review 2027-04-30. The 5 K13
entries name the upstream (`CCO …/ont00001180`). K02, K14 and K15 have no entries: S1 fixed
them. `--propose` takes one reason, owner and review for all of a check's new findings, so it
cannot write a reason per class (finding P-A6). `tools/wp6_register.py` calls the template's
own `findings.propose()` once per class instead. Writing 3,749 entries took 1 min 28 s;
`findings.py` reads them without complaint.

**The dispose stage, exercised** on S1 with the register filled. `validate.py --gate` locally
(1 min 31 s):

| Plant | Count | Gate | What it names |
|---|---:|---|---|
| none | 3,748 | pass | 3,748 accepted, 0 new, 0 stale |
| A. a new class with no definition source | 3,749 | **fail** | `NEW Warning … WP6PlantedClass` |
| B. a finding fixed (definition source added), its entry left | 3,747 | **fail** | `STALE … AccountApprovalDecision -- it matches nothing; if it was fixed, remove the entry in this commit` |
| C. one entry deleted | 3,748 | **fail** | `NEW Warning … AccountApprovalDecision` |
| A + B together | **3,748** | **fail** | both, by name |

A + B is the case the count-based gate at `2455bcc` passed: one fixed, one introduced, the
same total. It now fails. Each plant was reverted; the working tree was clean after.

The tests passed locally too (396 passed; 27 min 52 s on this machine, against 7 min 12 s on
the runner).

## 9. The template-controls verdict, re-rated

The S1 evaluation's six stages (§3 there), re-rated for v0.1.0 on BPO:

| Stage | At `2455bcc` | At v0.1.0 | Evidence |
|---|---|---|---|
| Detect | strong for structure, missing punning, licensing, scheme rules | **stronger**: placement (563), comment drift (53), scheme rule (39), properties' definitions (10) now automatic | §4, §5 |
| Report | one count per check; 20-sample JSON; fail-fast | **by identity**, every finding, every check run | §4, §6 |
| Evaluate | nowhere to classify | **used**: every finding in one of 17 classes, approved per class, carried by reason, owner, review and `upstream`. Weakness: no field for the classification itself (real, false alarm, unsure), so it lives in the reason text (P-A7) | §8, `classification.md` |
| Dispose | count per rung; IRI lint none | **works at BPO scale, by identity**: 3,749 entries; a new finding, a stale entry and a fix-plus-new at an unchanged count each fail, by name; Checks green with every finding answered for. Weakness: `--propose` writes one reason per run, not per class (P-A6) | §6, §8 |
| Correct | — | unchanged: the template reports, people fix | — |
| Verify | checks did not finish at BPO size | **finish**: validation 15 s, Checks 6–9 min, release 2.5–3.5 min | §4, §6 |
| Keep up with the template | — | **no procedure**; the checks are not covered by `--against` | §2 |

**Remaining detection gaps on BPO:** APQC text and its release (G1, G2), pending declaration
and Legal; and property semantics (G4), which needs review by design.

**Phase A status:** done. Every step is complete; step 7's browser run was an inspection by
the BPO architect, without screenshots or checklist (§7).

## Findings of Phase A

| Id | Finding | Kind |
|---|---|---|
| P-A1 | Transitive Python dependencies are unpinned (owlrl, html5rdf, prettytable, …). `requirements-dev.txt` says owlrl is unpinned because nothing imports it, but pyshacl does | template |
| P-A2 | No documented upgrade procedure for a project | template |
| P-A3 | `template_status.py --against` does not cover the checks a project runs: shapes, fixtures, profile, naming and reasoning config are project-owned. A ROBOT move is invisible to it | template |
| P-A4 | A scheme rule cannot relate a local name to a literal (BPO's second D7 rule) | template (expressiveness) |
| P-A5 | The explorer shows no comments, so comment drift reported by the validator is invisible on the site | template |
| P-A6 | `--propose` takes one reason, owner and review for every new finding of a check, so a project that disposes by class (A5) cannot use it as it stands. A filter (by rule, or by a list of identities) would do | template |
| P-A7 | The register has no field for a finding's classification (real, false alarm, unsure; `upstream` alone has one). The S2 verdict counts real defects, which then has to be read from the reason text or from our `classes.tsv` | template |
| G3 | S1's mapping rows say "ported unchanged" for 3 re-typed properties | ours (port) |
