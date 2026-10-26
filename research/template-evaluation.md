# Evaluation: the Ontology Template on the Business Process Ontology

**For:** the Ontology Template Team. **From:** the BPO team. **Date:** 2026-10-26.
**Evidence base:** `research/port-report.md` in this repository (cited as §n).
**States compared:**

- **S0**: original published BPO, `Skreen5hot/BusinessProcessOntology` at `bc64e91`.
- **S1**: migrated BPO, this repository at `c062662`.
- **S2**: improved BPO, the target once the actions below are done.

Because the port is lossless (§3), the template's checks run on the port *before* the
approved changes measure S0 itself. Those first-run figures are the S0 baseline.

## Summary

| Question | Answer | Confidence |
|---|---|---|
| 1. Was BPO migratable? | **Yes, with limits.** All 5,051 terms and 49,336 statements carried over, and the port is reasoned, validated against a recorded baseline and published. **Full template compatibility was not reached:** releases cannot be built, and validation finishes only with a patched template file | High (measured) |
| 2. Did it surface issues? | **Yes.** 18 BPO findings and 21 template deficiencies. 9 of the BPO findings were reported automatically by template checks. The rest came from manual inspection, the PO's review, or tests the project added | High |
| 3. Does the template support addressing them? | **Partly.** It detects and reports well. It cannot record a decision against a specific finding (its validation baseline counts findings per check, and two checks have no baseline at all). It has no check for property punning, licensing inside a file, or BPO's capability-as-process rule. Its checks do not run at BPO's size without changes | High |
| 4. What must be done? | 37 open register entries (§4 below: 16 BPO, 21 template/process; B12 and B17 are already resolved). **12 decisions for the BPO architect, PO or Legal**, **6 template changes that block repeatability** (T1–T6), and the rest lower priority | High |
| 5. Is BPO higher quality because of the template? | **Not yet demonstrated.** Issue visibility improved measurably. The ontology improved in **5 bounded respects**, mostly through the PO's review rather than template checks. The defects that matter most, definition drift and APQC attribution, are visible but **unchanged** | High |

**The success criterion is not yet met.** The template has shown it can *identify* quality
deficiencies in a real ontology, including some BPO's own gates missed. It has not yet shown that it can
*support their correction, verify the improvement, and prevent recurrence* at this scale.

---

## 1. Was BPO successfully migratable?

### What succeeded

| Aspect | Result | Evidence |
|---|---|---|
| Completeness | 3,119 classes, 3 object + 7 annotation properties, 1,921 SKOS concepts + 1 scheme: all ported. 5,051 terms, each with a row in `mappings/bpo.sssom.tsv` (new IRI to old IRI), mapping checker clean | §3 |
| Preservation of content | 49,336 statements in the source, 49,336 in the port, with blank-node restrictions compared structurally: none lost, none added. Re-running the port gives byte-identical modules | §3 |
| Preservation of meaning | Local names, labels, definitions and axioms unchanged. 3,343 named subclass axioms and 4,381 existential restrictions on both sides. ELK over the full pinned BFO 2020 + CCO v2.0: consistent, nothing unsatisfiable | §3, §4 |
| Statements dropped, by design | 3 local "CCO superclass bridge" axioms. Each is asserted verbatim in the pinned CCO, so the entailments are unchanged. BPO's 18 module headers, replaced by one header per new module | §3 |
| Publication | Site live, with 3,129 authored terms indexed (3,119 classes + 10 properties) | §2 |
| Time | First green CI in 26 min (target 2 h). Complete port 1 day 15 h after start (target 2 days). About 7 h hands-on | §2 |

### Required changes, each with its justification

All were approved by the PO (§6). The rule this evaluation applies: **no ontology content is
changed only to satisfy a template check without an ontological justification.**

| Change | What prompted it | Ontological justification | Assessment |
|---|---|---|---|
| 3 `requires…` properties re-typed from object to annotation properties | PO review | BPO asserts them only between classes, which in OWL DL is punning, not a class-level requirement | Justified on its own terms |
| `skos:definition` added to the 10 properties | Site build refused to run | Definitions written to the realist contract; corrects `bearsPermission` (an Action Permission is a Directive ICE, not something a role bears) and narrows `enablesProcess` | Prompted by a check, **justified by the review**; the texts are content, not padding |
| PCF v7.4 release cited on the 14 modules holding APQC text | PO's provenance test | Every row came from v7.4; BPO named the release only in its catalog | Justified |
| 13 PCF categories made top concepts of the scheme | SKOS shape | They are the framework's top level, a structural fact | **The change most driven by a check.** Correct, but it adds no meaning; count it as conformance, not as a quality gain |

### Limitations: migrated is not the same as compatible

| Limitation | Effect | Evidence |
|---|---|---|
| **Releases cannot be built.** `tools/release.py` canonicalizes blank nodes with rdflib; on 4,381 similar restrictions one build had not finished after 5 h 22 min | Releases blocked; the 8 release-build tests deselected | §7 |
| Validation finishes only with a template-owned file patched (`validate.py`) | Unpatched: did not finish in 1 h 56 min. Patched: 35 min. Results proved identical on every fixture | §5, §7 |
| The test suite does not scale | 6 min on the empty template; on BPO, 15 h 29 min and only half done | §7 |
| CI Checks is red by decision | One IRI-lint exception is kept, and the Checks job stops at its first failure, so 7 of its 17 steps never run in CI (they were run locally) | §4, §7 |
| Header metadata only partly carried | BPO's header titles, `versionInfo 0.4.1` and header comments are not in the new headers | §3 |

---

## 2. Did the template and the migration surface issues?

Yes. **How each issue was found** matters as much as the issue itself:

- **Auto**: a template check reported it unprompted.
- **Auto, consequential**: a template tool failed, and someone had to diagnose why.
- **Project test**: found by a test the project added at the PO's direction.
- **Manual**: found by reading, review or troubleshooting.

### BPO issues (content and modelling)

| ID | Issue | How found | Did BPO's own tooling catch it? |
|---|---|---|---|
| B1 | 50 shared classes carry conflicting definitions/labels across slices (57 violations); 110 term/property pairs and 266 variants once comments are counted | Auto (wellformedness shapes) for definitions and labels; project test for comments | **No.** Each slice is validated alone, and the consistency audit checks anchors, not text |
| B2 | 3,757 verbatim APQC passages published under MIT, with no APQC attribution | Manual | No |
| B3 | PCF release named only on the catalog; slices 5 and 6 cite no source | Project test | No |
| B4 | `P10530_SuggestionProgram`: a non-PCF class with a PCF-style IRI and an underscore | Auto (IRI lint) | No (BPO's Gate F accepted it) |
| B5 | All 10 properties lack `skos:definition` | Auto, consequential (site build) | No |
| B6 | `requiresCapability/Role/Permission` declared as object properties but used class-to-class (punning) | Manual (PO review) | No |
| B7 | `bearsPermission` says a role *bears* a permission; CCO's Action Permission is a Directive ICE | Manual (PO review) | No |
| B8 | `enablesProcess` means "can enable" but is used to derive a *requirement* | Manual (PO review) | No |
| B9 | 13 definitions whose genus is not the asserted parent (e.g. P20799 "An Act of Design" ⊑ Act of Formulation) | Auto (realist, warning) | No |
| B10 | Editorial qualifiers in labels: "(shared anchor)" (5 classes affected) and "(discernment sense)" (73 affected) | Auto (realist, warning) | No |
| B11 | Organizations placed where CCO requires an Agent (5): CCO 2.0's Organization is not an Agent | Auto (realist, warning) | Known and documented in BPO, not tested |
| B12 | The concept scheme declares no top concept | Auto (SKOS shapes) | No |
| B13 | 224 second parents co-asserted for BPO's offline SHACL; many redundant once CCO is in scope | Auto (realist, warning) | By design |
| B14 | No class names a definition source (3,119) | Auto (annotation profile, warning) | No |
| B15 | 39 capabilities wearing process IRIs (BPO's tracked backlog) | **Not detected by the template** | **Yes** (BPO Gate F) |
| B16 | Comment prose still cites the old `bpo:` CURIEs | Manual | — |
| B17 | 3 local re-statements of CCO axioms | Manual (port) | By design |
| B18 | Header metadata not carried in full (titles, version, notes) | Manual (found while writing the provenance test) | — |

**Count:** 18 BPO issues. **9 auto-detected** by the template: B1 (definitions and labels), B4, B5,
B9–B14. **4 from the PO's review or the project's tests:** B3, B6, B7, B8. **5 manual:** B2,
B16, B17, B18, and the comment half of B1. **1 missed by the template that BPO's own tooling
catches:** B15.

### Template deficiencies

| ID | Deficiency | How found |
|---|---|---|
| T1 | Validation does not scale: pyshacl pre-binds `$this` and rdflib applies the binding late, so cost grows ~O(n²) | Auto, consequential; manual diagnosis (1 h 15 min) |
| T2 | Release builds do not scale (`to_canonical_graph` over thousands of similar blank nodes) | Auto, consequential (test hung); manual diagnosis |
| T3 | The test suite does not scale (one setup took 51 min; release tests run for hours); no size benchmark | Auto, consequential |
| T4 | The validation baseline is one count per check: a fix and an unrelated new finding cancel out | Manual |
| T5 | The IRI linter has no exception mechanism, and Checks is fail-fast: one accepted finding hides 7 steps | Manual |
| T6 | The site requires `skos:definition` and one value per language on every term; the shapes require neither for properties, so the failure shows only at deploy | Auto, consequential |
| T7 | The site reads each module alone, so it publishes one module's text for a drifted class and hides the conflict | Manual |
| T8 | No check for differing labels, definitions or comments across modules | Manual (filled by a project test) |
| T9 | Licensing is decided per file: third-party text inside an authored module passes as MIT | Manual |
| T10 | No check for punning or for annotation-versus-object property misuse | Manual |
| T11 | The genus check cannot match a label carrying a parenthetical qualifier | Manual (analysis of 540 warnings) |
| T12 | No rule matching BPO's/IRI_Linter's capability-as-process check: a regression against the source's own gates | Manual |
| T13 | `init_project.py` deletes files without staging the deletion, so the suite fails before the first commit | Auto |
| T14 | `init_project.py` refuses a dirty tree, which conflicts with keeping a report as you go | Auto |
| T15 | README gaps: `gh` route, Pages via the API, `core.hooksPath`, suite command and expected times; the rendered CLAUDE.md forbids the push README step 5 requires | Manual |
| T16 | Project-specific tests have no home: `tests/` is template-owned, so a project test counts as divergence | Auto (`template_status.py`) |
| T17 | No guidance for porting a predecessor ontology: SSSOM direction and justification for a namespace move, carrying header metadata | Manual |
| T18 | The "readable local names" decision is not enforced, and conflicts with sources that use identifier-based IRIs | Manual |
| T19 | Pinned actions were already stale at copy time (a Dependabot PR at minute 2) | Auto |
| T20 | `validate.py` prints no progress, and its JSON keeps only 20 sample warnings | Manual |
| T21 | The report form points to a commit SHA the manifest does not hold, and the form is not in the template | Manual |

---

## 3. Does the template provide the framework to address them?

Each issue goes through six stages, rated **✓** supported, **◐** partly supported or needs a workaround, **✗** missing:

- **Detect**: a check finds it.
- **Report**: it reaches a person with location and reason.
- **Evaluate**: there is somewhere to classify it.
- **Dispose**: a decision can be recorded against *that* finding.
- **Correct**: the template helps make the fix.
- **Verify**: a check proves it fixed and keeps it fixed.

| Finding | Detect | Report | Evaluate | Dispose | Correct | Verify | Gap |
|---|---|---|---|---|---|---|---|
| B1 drift (definitions/labels) | ✓ | ✓ | ◐ | ◐ count only | ◐ | ◐ | The baseline holds "57", not *which* 57 (T4); the site hides the drift (T7) |
| B1 drift (comments) | ✗ | ✗ | ✗ | ✗ | ✗ | ◐ project test | T8 |
| B2 APQC attribution | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | T9 |
| B3 release provenance | ✗ | ✗ | ✗ | ✗ | ◐ | ◐ project test | No provenance shape |
| B4 IRI naming | ✓ | ✓ | ◐ | ✗ no exception | ◐ rename via SSSOM | ◐ | T5 |
| B5 property definitions | ◐ site only | ◐ at deploy | ◐ | ✗ | ✓ | ✓ site test | T6 |
| B6 punning | ✗ | ✗ | ✗ | ✗ | ✗ | ◐ project test | T10 |
| B7/B8 property semantics | ✗ | ✗ | ✗ | ◐ `docs/decisions/` | ✗ | ◐ project test | Needs review; no tool can catch it |
| B9 genus mismatch | ✓ warning | ✓ | ◐ | ✗ warnings not baselined | ✗ | ◐ | Warnings are invisible to the gate |
| B10 label qualifiers | ◐ | ✓ | ◐ | ✗ | ✗ | ◐ | T11 |
| B11 Organization ⊄ Agent | ✓ warning | ✓ | ◐ | ✗ | ✗ | ◐ | Upstream (CCO) issue; no place to record it |
| B12 top concept | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — (the one end-to-end success) |
| B13 co-parents | ✓ warning | ✓ | ◐ | ✗ | ✗ | ◐ | — |
| B14 definition source | ✓ warning | ✓ | ◐ | ✗ | ◐ | ◐ | Profile annotation not mapped to BPO's provenance |
| B15 capability-as-process | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | T12 |
| T1–T3 scale | ◐ by failing | ✗ no timings | ✗ | ✗ | ✗ | ✗ | No benchmark |

**Strengths, as measured:**
- Detection and reporting are strong for structure and well-formedness (B1, B4, B9–B14). The template found real defects that BPO's own gates missed.
- The reasoning job and the mapping checker work at full scale.
- The falsification fixtures made it possible to *prove* the `validate.py` patch changed no result.
- Refusing to raise a baseline without a written reason forced every accepted finding into words.

**Gaps:**
1. **Disposition at finding level.** Every accepted finding needs one record: identity, check, reason, owner, review date. Today the validation gate keeps a count per check, IRI lint keeps nothing, and the site refuses outright.
2. **Verification of semantics.** Punning, property misuse and licensing inside a file all needed a human review or a project test.
3. **Scale**, which undermines everything else: a check that never finishes verifies nothing.

---

## 4. Findings register: actions required

Columns:
- **Kind**: BPO content (C), template deficiency (T), process (P).
- **Sig**: significance (Critical / High / Medium / Low).
- **Owner**: who disposes of it.
  - **BPO**: the BPO team.
  - **Arch**: the BPO architect / PO, for modelling decisions.
  - **TT**: the Ontology Template Team.
  - **Legal**: whoever decides licensing.

**No BPO content change is proposed only to satisfy a check.** Each C row needs the
architect's ontological judgement first.

### BPO content and modelling

| ID | Kind | Sig | Evidence | Recommended disposition | Owner | Verified when |
|---|---|---|---|---|---|---|
| B1 | C | **High** | 57 violations; 266 variants (`config/annotation-drift.tsv`) | Harmonize one definition and label per class, and decide whether shared comments should be per-module or canonical. Do it in BPO first, then re-port | Arch, BPO | Wellformedness rung 0; drift file down to accepted per-module comments only; baseline re-recorded lower |
| B2 | C | **High** | 3,757 `apqcSourceText` literals; licensing check passed | Establish APQC's terms; add attribution (or a licence statement) to the annotation property or catalog header, or move verbatim text out of the redistributed ontology | Legal, PO | Attribution present in released artefacts; licensing disposition per annotation (needs T9) |
| B3 | C | Medium | `test_every_source_description_is_in_a_module_that_names_the_release` | Done in the port; back-port to BPO's slice headers | BPO | Same test against BPO |
| B4 | C | Medium | IRI lint, `pcf_7.ttl:944` | Decide: rename to a non-PCF readable IRI with an SSSOM replacement row, or keep as a recorded exception once T5 exists | Arch | IRI lint clean, or an exception with identity and reason |
| B5 | C | Medium | Site refusal; 10 definitions added | Done in the port; back-port to BPO | BPO | Site test; BPO index has definitions |
| B6 | C | High | PO review; 0 restrictions use them | Done in the port; back-port to BPO **and check the effect on BPO's SHACL C5–C7**, which assume object properties | BPO | BPO C5–C7 still pass; no `ObjectProperty` minted between classes |
| B7 | C | High | Action Permission ⊑ Process Regulation ⊑ Directive ICE (verified) | Definition corrected. Decide on a label change (`permissionApplicableToRole` proposed) with a deprecation row | Arch | Label decision recorded; SSSOM row if renamed |
| B8 | C | High | 361 `enablesProcess` pairs | Audit `capabilities/capability_scope.json`: does every pair mean *required*? Split "can enable" from "requires" if not | BPO, Arch | Audit recorded; mirror test still holds |
| B9 | C | Low | 13 realist warnings, listed in §4 | Align each definition's genus with the asserted parent, or re-parent | Arch | Those 13 warnings gone |
| B10 | C | Low | 78 warnings | Move qualifiers to `skos:altLabel`/comment, or accept once T11 is fixed | Arch | Warnings gone, or justified |
| B11 | C | Medium | 5 warnings | Decide the pattern for organizations acting as agents under CCO 2.0, and record it as a decision | Arch | Decision in `docs/decisions/`; warnings disposed of |
| B13 | C | Low | 224 warnings | Remove co-parents made redundant by the full CCO, after BPO decides whether its standalone-slice validation still needs them | Arch | Warning count reduced; reasoner unchanged |
| B14 | C | Medium | 3,119 warnings | Map BPO's provenance (`pcfID`, `apqcSourceText`, or a citation) to the profile's definition-source annotation | Arch | Warning count 0 or justified |
| B15 | C | Medium | BPO Gate F baseline: 39 | Keep tracking in BPO until T12 exists; then dispose here | BPO | Rule present; count recorded with identity |
| B16 | C | Low | Comments cite `bpo:` | Accept as provenance, or annotate "(old prefix)"; do not rewrite silently | PO | Decision recorded |
| B18 | C | Low | §3 | Decide whether BPO's titles, version and design notes belong in the new headers | PO | Decision recorded |

### Template and process

| ID | Kind | Sig | Evidence | Recommended disposition | Owner | Verified when |
|---|---|---|---|---|---|---|
| T1 | T | **Critical** | Unpatched ladder did not finish in 1 h 56 min; patch proved equivalent | Adopt the inline-`$this` fix (commit `056403f`) or an upstream fix | TT | Ladder on BPO in under 15 min; fixture results unchanged |
| T2 | T | **Critical** | One release build ran 5 h 22 min unfinished | Replace `to_canonical_graph` with a canonicalization that scales (e.g. hash-based labelling of restriction trees, or RDFC-1.0) while keeping byte-identical builds | TT | `release.py build` on BPO in under 15 min, byte-identical across seeds |
| T3 | T | High | Suite 6 min → 15 h+ | Add a size benchmark (≥3,000 classes, ≥4,000 restrictions) with time budgets per tool; mark corpus-wide tests | TT | Benchmark in the template's CI, within budget |
| T4 | T | High | Baseline `{"authored_findings": 57}` | Baseline by identity (focus + shape + message digest), each entry with a reason, owner and review date | TT | Swapping one finding for another fails the gate |
| T5 | T | High | 7 CI steps skipped | An exception register shared by IRI lint (and the site); run every Checks step and fail at the end with a summary | TT | A known exception passes; all steps report in CI |
| T6 | T | High | Site refusal at deploy | Move the site's term contract into shapes (a definition on every authored term, one per language) | TT | The ladder fails on the same inputs the site refuses |
| T8 | T | Medium | 110 pairs found by a project test | Ship a cross-module drift check (labels, definitions, comments) | TT | Template fixture with planted drift fails |
| T9 | T | Medium-High | 3,757 passages passed as MIT | Licensing disposition for annotation properties that carry third-party text, and a shape requiring attribution | TT | A fixture with unattributed third-party text fails |
| T10 | T | Medium | 3 properties | Shape: an object property used between two classes, or an annotation property in a restriction | TT | Fixture fails |
| T12 | T | Medium | BPO Gate F, 39 | Port IRI_Linter's capability-as-process (and pcf-without-id) rules, or document why not | TT | Rule runs; BPO count 39 reproduced |
| T7 | T | Medium | Site shows the first module's text | Site: refuse, or flag, a term described differently in two modules | TT | Fixture |
| T17 | T/P | Medium | §7 | "Porting an existing ontology" guide: SSSOM direction and justification for a namespace move, header carry-over, lossless check | TT | Next port follows it with no question about mapping |
| T16 | T | Low-Medium | `template_status`: `added tests/test_bpo_port.py` | Declare a project-owned tests location the suite collects | TT | A project test is not reported as divergence |
| T11 | T | Low | 78 warnings | Genus check ignores a trailing `(…)` qualifier, or the docs ask projects not to put qualifiers in labels | TT | Fixture |
| T13 | T | Low | First suite run failed | `init_project.py` stages deletions and renames | TT | Suite green straight after init |
| T14 | P | Low | §7 | Allow `research/` changes in init's clean-tree check, or ship the report form | TT | — |
| T15 | P | Low | §7 | README additions (listed in T15) and reconcile the "nothing pushed" rule with step 5 | TT | Next porter asks no setup question |
| T18 | T | Low | §7 | State whether identifier-based IRIs are acceptable for ported ontologies | TT | Documented |
| T19 | P | Low | Dependabot at minute 2 | Refresh pins before tagging template releases | TT | No day-0 Dependabot PR |
| T20 | T | Low | §7 | Progress output; full (or paginated) warning detail in JSON | TT | — |
| T21 | P | Low | §1 of the report | Put the form in the template; record the template commit SHA in the manifest | TT | — |

---

## 5. Is BPO of higher quality because of the template?

### Three kinds of improvement, kept apart

| Kind | Demonstrated? | Evidence |
|---|---|---|
| **Issue visibility** | **Yes, measurably.** 8 classes of real BPO defects are now reported by template checks (B1, B4, B5, B9, B10, B11, B12, B14). BPO's own gates reported none of them. One regression: B15 is visible to BPO's tooling and not to the template | §4 first-run findings |
| **The ontology itself** | **Partly, in 5 bounded respects, none of them the major defects:** (1) class-level punning removed (B6); (2) `bearsPermission` and `enablesProcess` given correct semantics (B7, B8); (3) all 10 properties defined (B5); (4) PCF release provenance complete (B3); (5) scheme top level declared (B12). (1)–(2) came from the PO's review, not from a template check; (3) and (5) were prompted by checks; (4) by a project test. B1 (drift) and B2 (attribution) are **unchanged** | §3 |
| **The development process** | **Not yet.** It is better in two ways: any new drift now fails a test, and any accepted validation finding needs a written reason. It is worse in three: CI runs only 10 of 17 Checks steps, a release cannot be built, and one run takes 35 min | §7 |

Passing the reasoner and the validation gate is **not** evidence of quality here: the gate passes
*because* 57 known defects are written into its baseline.

### Proposed measurement

**Principle:** count *confirmed real defects*, not check results. A finding counts only once it is
classified *real*. Measure every state with the **same** checks: the patched ladder, the IRI
linter, the reasoner, the site build, the project's drift and provenance tests. Report counts by
identity (which terms), not just totals.

| Metric | S0 original | S1 migrated | S2 target | How measured |
|---|---|---|---|---|
| Statements preserved | 49,336 | 49,336 (+39 / −3 approved) | as S1, plus recorded changes | lossless comparison script (§3) |
| Gated validation violations (real) | 58 (57 drift + 1 SKOS) | 57 | **0** | `validate.py` |
| Annotation drift, term/property pairs | 110 | 110 | **0**, or only per-module comments the architect accepted | `config/annotation-drift.tsv` |
| Authored terms without a definition | 10 | 0 | 0 | site build |
| Properties used as class-level punning | 3 | 0 | 0 | port test |
| Property definitions contradicting CCO (B7) | 1 | 0 | 0 | review + test |
| Modules citing the PCF release | 1 of 18 files | 14 of 14 | 14 of 14 | provenance test |
| Third-party text with attribution | 0 of 3,757 | 0 of 3,757 | **3,757 of 3,757** (or removed) | to be built (T9) |
| IRI naming violations | 1 | 1 | 0, or an exception with identity | IRI lint |
| Real genus mismatches | 13 | 13 | 0 | realist warnings, classified |
| Labels with editorial qualifiers | 78 terms affected | 78 | decision-dependent | realist warnings |
| Organization-in-Agent placements | 5 | 5 | 0, or a recorded pattern decision | realist warnings |
| Capability-as-process | 39 (BPO Gate F) | 39 (unmeasured by the template) | per BPO plan, measured by the template | T12 |
| Consistency / unsatisfiable classes | 0 / 0 | 0 / 0 | 0 / 0 | reasoner. **Necessary, not sufficient** |
| *Process:* full ladder time | did not finish (template unpatched) | 35 min | < 15 min | timing |
| *Process:* release build | n/a | > 5 h 22 min, unfinished | < 15 min, byte-identical | timing |
| *Process:* Checks steps running in CI | — | 10 of 17 | 17 of 17 | CI log |

**What would show BPO improved:** S2 strictly better than S0 on the rows marked **0** above,
with each change traced to an approved decision (`docs/decisions/`) and a check that now fails
if the defect comes back.

---

## What has been demonstrated, what remains, what happens next

**Demonstrated**
- BPO can be ported losslessly, reasoned and published from the template, quickly.
- The template's checks find real structural and well-formedness defects that BPO's own gates
  did not, notably the cross-slice drift.
- The template's falsification fixtures let a tool change be proved behaviour-preserving.

**Not demonstrated**
- That BPO's quality improved because of the template: the major defects are visible but uncorrected.
- That the template's process scales: validation needed a template-file patch, the release build and the test suite do not finish.
- That accepted findings can be disposed of individually, or that the template detects semantics or licensing issues.

**Unresolved**
- BPO decisions: B1, B2, B4, B7 label, B8 audit, B9–B11, B13, B14, B16, B18.
- Template work: T1–T21. T1, T2, T3, T4, T5 and T6 block a repeatable process.

**Next**
1. **Template Team:** triage this register, then fix T1 and T2 first (scale), then T4, T5 and T6 (finding-level disposition, full CI, one term contract), then T8, T9, T10 and T12 (detection gaps).
2. **BPO team, with the architect and Legal:** decide B1 and B2 first, then the remaining C rows. Make the corrections in BPO, recorded in `docs/decisions/`, then re-port with `tools/port_from_bpo.py`.
3. **Once the template fixes land:** re-run the affected tests (ladder timing, release build, full suite, CI with all steps), measure S2 against the table above, and send the final assessment of whether BPO's quality has demonstrably improved.
