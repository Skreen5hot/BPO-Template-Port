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
| First green CI run (before any ontology content) | 2026-10-24 13:43 | 26 min from start. Checks 44 s, Pages 43 s, **Reasoning 12 min 1 s** (empty ontology; ROBOT + full CCO) |
| Pages enabled and the site live | 2026-10-24 13:32 | Enabled via API at 13:30 before the first push; https://skreen5hot.github.io/BPO-Template-Port/ returned 200 after the first Pages run (template site, no BPO content yet) |
| All classes ported | 2026-10-24 13:37 | `tools/port_from_bpo.py`, one run, ~1 min. Lossless check 13:38; counts confirmed 15:57 (§3) |
| All properties and axioms ported | 2026-10-24 13:37 | Same run. Mapping set added 15:55 (5,051 rows, checker clean) |
| Validation gate green (`tools/ontology/validate.py --gate`) | 2026-10-26 04:06 | Local, 03:29–04:06 (37 min), with the PO-approved changes: "the baseline describes reality" (wellformedness 57 recorded, all other rungs 0 violations). Needed the `validate.py` patch (§5) to finish at all |
| Reasoner green (Reasoning workflow) | 2026-10-26 04:21 | CI run 40290127342, 14 min, on the full port. Locally green on the first run (10-24 13:58) |
| Everything green, port complete | not reached (port complete 2026-10-26 04:21) | Port complete and published; Pages green (04:10, site shows 3,129 authored terms), Reasoning green, Checks **red at one step by PO decision**: IRI lint on `bpot:P10530_SuggestionProgram` (§4, §6). Every Checks step before it passed in CI, the validation gate included; the 7 after it were skipped by fail-fast and were run locally instead (§7) |

Hands-on time in total, excluding waiting: **~7 hours** (10-24 13:17–16:40; 10-25 04:05–05:10 and 20:26–21:50; 10-26 03:20–04:30). Machine time on top: validation runs of 35 min to 2 h each (×5), a 15.5 h test run stopped unfinished, a 1 h test re-run. Waiting on PO answers: ~17 h overnight in total (§6). Calendar: 1 day 15 h from start to the complete port.

## 3. Coverage: did everything come across?

| | Source | Ported |
|---|---|---|
| Classes | 3,119 | 3,119 |
| Object properties | 3 | 0 (the 3 re-typed, PO decision 10-26) |
| Data properties | 0 | 0 |
| Annotation properties | 7 | 10 (7 + the 3 re-typed) |
| SKOS concepts (catalog) + scheme | 1,921 + 1 | 1,921 + 1 |
| Logical axioms: named subClassOf | 3,343 | 3,343 |
| Logical axioms: subClassOf an existential restriction | 4,381 distinct (4,401 raw; 20 are inlined copies of the same restriction in two files) | 4,381 |
| Logical axioms: equivalence / disjointness / AllDisjointClasses | 0 / 0 / 0 | 0 / 0 / 0 |

Source counts: rdflib over BPO's 18 ontology files at `bc64e91` (terms in the `bpo#`
namespace); BPO's `corpus_index.tsv` agrees (5,050 rows). Port counts: rdflib over the 17
modules. Site, after the push: `data/terms.json` counts **authored 3,129** (= 3,119 classes + 10 properties) and **upstream 152**; concepts are on the vocabulary page, not in the term index. `corpus_digest.py`: 62,677 triples merged, 45,153 ground, 4,381 blank nodes (17,524 triples touching).

Source counts: from the source repository's own tooling or a reasoner report.
Ported counts: the site's `data/terms.json` (`counts`), and
`python tools/ontology/corpus_digest.py`.

Mapping set: `mappings/bpo.sssom.tsv`, **5,051** rows (3,119 classes, 3 object properties,
7 annotation properties, 1,921 concepts, 1 concept scheme); `python tools/ontology/mappings.py`
passes: **yes** (first run, 0 findings). Rows run new → old (`bpot:X skos:exactMatch bpo:X`), see §7.

Losslessness after the approved changes (10-26): the port differs from the renamed source by exactly 3 removed statements (the three `owl:ObjectProperty` types) and 39 added (26 top-concept, 10 definitions, 3 `owl:AnnotationProperty` types); header metadata as below.

Losslessness of the first port (10-24), measured: every BPO statement, renamed and with blank-node
restrictions compared as trees, against the port: **49,336 = 49,336, none missing, none
extra.** Excluded by design and listed by the port tool: the 18 BPO `owl:Ontology` headers
(replaced by one header per module, each citing its BPO source in `dcterms:source`), and 3
statements about CCO terms (BPO's "1b. CCO superclass bridges": `371⊑228`, `402⊑228`,
`626⊑853`). Each of the 3 is asserted verbatim in the pinned CCO (checked in
`.upstream-cache/cco.ttl`), so nothing is lost once CCO is loaded. Re-running
`tools/port_from_bpo.py` gives byte-identical modules.

**Terms not carried over, or changed in meaning.** One row each.

| Old IRI | What happened | Why |
|---|---|---|
| none | No term dropped, merged, split, re-parented or redefined. All 5,051 kept their local name, labels, definitions and axioms | Namespace move only |
| `cco:ont00000371 ⊑ cco:ont00000228`, `cco:ont00000402 ⊑ cco:ont00000228`, `cco:ont00000626 ⊑ cco:ont00000853` (statements, not terms) | dropped | BPO restated these upstream axioms so a slice could pass SHACL without CCO. Here CCO is in scope; each is asserted verbatim in the pinned CCO, so the entailments are unchanged |
| 18 BPO `owl:Ontology` headers (`…/bpo/slice/…`, `…/bpo/capabilities`, …) | replaced | One header per new module; each cites its BPO header IRI and its `dct:source` literal(s) in `dcterms:source`. **Correction (10-26):** the first port dropped the headers' metadata, including the catalog's PCF release ("… (Cross-Industry) v7.4"); found while writing the PO's provenance test, now carried. Still not carried: BPO's header titles, `owl:versionInfo "0.4.1"` and header comments (design notes such as "Self-contained: the shared act genera it uses are inlined…", no longer true here) |
| `bpo:requiresCapability`, `bpo:requiresRole`, `bpo:requiresPermission` | **re-typed**: `owl:ObjectProperty` → `owl:AnnotationProperty` | PO decision 10-26: BPO asserts them only class-to-class, which OWL reads as punning, not a class-level requirement. No restriction used them; instance-level modelling would use CCO `has capability` (`ont00001954`), `has agent` (`ont00001833`), `permits` (`ont00001910`), all verified in the pinned CCO. SSSOM `object_type` follows |
| the 10 BPO properties | `skos:definition` **added** (PO's text, verbatim); `rdfs:comment` unchanged | The site build refuses a term with no definition. `bearsPermission` is now defined as a policy association, not a permission borne by a role: Action Permission (`ont00000751`) is a Process Regulation, a Directive ICE (verified), not something an agent bears. `enablesProcess` narrowed to a *required* capability so `requiresCapability` can be derived from it |
| `bpot:PCF` scheme + 13 category concepts | `skos:hasTopConcept`/`skos:topConceptOf` **added** (26 triples) | PO decision 10-25 (SKOS finding) |
| every module carrying `apqcSourceText` (14) | `dcterms:source "APQC Process Classification Framework (Cross-Industry) v7.4"` **added** | BPO named the release only on the catalog; slices cited the framework without a release, and PCF 5 and 6 cited nothing (found by the provenance test) |
| `ontology/reference/apqc_1_1_1.ttl` (readable-IRI reference template) | not ported | Marked FROZEN / SUPERSEDED in BPO itself; not part of BPO's validated corpus |
| BPO SHACL shapes (`apqc_shapes.ttl` S1–S8, `capabilities_roles_shapes.ttl` C1–C7) and `apqc_bad_examples.ttl` | not ported yet | Validation, not ontology terms; would be a new shape set needing its fixture and a test (template rule). Revisit if time allows |

## 4. What the checks found

Run each one on the ported ontology before fixing anything, and record the first
result. Then classify every finding.

| Check | Command | Findings on first run |
|---|---|---|
| Validation ladder | `python tools/ontology/validate.py` | (`--gate` green locally 10-26 04:06 and in CI 04:21.) Unpatched: **did not finish** (13:43 → killed 15:39, 1 h 56 min; see §5, §7). Patched: 34 min 52 s, exit 1, `passed: False`. Violations (gated): wellformedness **57**, skos **1**, realist 0, annotation-profile 0. Warnings (not gated): realist **540**, annotation-profile **3,119**. All four fixtures still rejected (9/25/10/10) |
| IRI linter | `python tools/ontology/iri_lint.py` | exit 1; 21 files, **1 finding**: `ontology/sections/pcf_7.ttl:942 naming_convention bpot:P10530_SuggestionProgram`. No `unverified`, no `readable_label`, no undeclared authored IRI across 5,051 terms |
| Reasoner | `python tools/ontology/reason.py` | exit 0, **0 findings**: "ROBOT 1.9.10, ELK, over 17 module(s) and bfo.ttl, cco.ttl -- consistent; nothing unsatisfiable". ~1 min locally (13:57 → 13:58), so CI's 12 min on an empty ontology is mostly setup, not reasoning |
| Competency questions | `python tools/ontology/competency.py` | exit 0, "no competency questions yet". BPO has none in this form; vacuously green |

Each finding gets one row. **Class** is one of: *real* (a defect in the source
ontology), *false alarm* (the check is wrong here), *template bug* (the check or
tool is broken), *unsure*.

| Check | Term | Finding (as printed) | Class | What you did |
|---|---|---|---|---|
| IRI linter | `bpot:P10530_SuggestionProgram` | `naming_convention` | *real* (minor). A supporting class BPO split out of compound row P10530; it carries no PCF id yet wears a PCF-style `P` IRI, plus an underscore. Breaks the template's UpperCamelCase rule and BPO's own D7 intent (`P<id>` = a PCF row) | Asked the PO (§6); decision: keep. **Real, not fixed**, carried over as-is; the finding stays open and CI's IRI-lint step stays red by decision (§7, 14:05) |
| Validation (wellformedness) | `bpot:ActOfForecasting` | carries two different skos:definition values in the same language (2 texts: bpot, pcf_10) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ActOfReporting` | carries two different skos:definition values in the same language (2 texts: bpot, pcf_13) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:Auditor` | carries two different skos:definition values in the same language (2 texts: pcf_12, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:Budget` | carries two different skos:definition values in the same language (3 texts: pcf_10, pcf_12, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:BusinessCase` | carries two different skos:definition values in the same language (2 texts: pcf_13, pcf_2) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:BusinessStrategy` | carries two different skos:definition values in the same language (3 texts: pcf_1, pcf_10, pcf_2) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:CompetitorData` | carries two different skos:definition values in the same language (2 texts: pcf_1, pcf_3) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:CompliancePolicy` | carries two different rdfs:label values in the same language (2 texts: pcf_11, pcf_12) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:CompliancePolicy` | carries two different skos:definition values in the same language (2 texts: pcf_11, pcf_12) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ComplianceReport` | carries two different rdfs:label values in the same language (2 texts: pcf_11, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ComplianceReport` | carries two different skos:definition values in the same language (2 texts: pcf_11, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ConsensusDemandForecast` | carries two different skos:definition values in the same language (2 texts: pcf_4, pcf_5) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:CostAnalysis` | carries two different skos:definition values in the same language (2 texts: pcf_3, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:CostData` | carries two different skos:definition values in the same language (2 texts: pcf_3, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:Customer` | carries two different skos:definition values in the same language (7 texts: pcf_1, pcf_2, pcf_3, pcf_4, pcf_5, pcf_6, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:CustomerData` | carries two different skos:definition values in the same language (2 texts: pcf_1, pcf_3) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:CustomerFeedback` | carries two different skos:definition values in the same language (5 texts: pcf_1, pcf_2, pcf_3, pcf_5, pcf_6) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:CustomerProfile` | carries two different skos:definition values in the same language (2 texts: pcf_1, pcf_6) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:DemandForecast` | carries two different skos:definition values in the same language (2 texts: pcf_4, pcf_5) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:DispositionDecision` | carries two different rdfs:label values in the same language (2 texts: pcf_10, pcf_4) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:DispositionDecision` | carries two different skos:definition values in the same language (2 texts: pcf_10, pcf_4) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:Employee` | carries two different skos:definition values in the same language (2 texts: pcf_7, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:FinancialData` | carries two different skos:definition values in the same language (2 texts: pcf_12, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:FinancialStatement` | carries two different skos:definition values in the same language (2 texts: pcf_1, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:Invoice` | carries two different skos:definition values in the same language (2 texts: pcf_12, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:MaintenanceSchedule` | carries two different skos:definition values in the same language (2 texts: pcf_10, pcf_4) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ManagementPersonnel` | carries two different skos:definition values in the same language (3 texts: pcf_4, pcf_6, pcf_7) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:MarketData` | carries two different skos:definition values in the same language (4 texts: pcf_1, pcf_10, pcf_2, pcf_3) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:PerformanceData` | carries two different skos:definition values in the same language (2 texts: pcf_13, pcf_7) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:PerformanceIndicatorSpecification` | carries two different skos:definition values in the same language (2 texts: pcf_13, pcf_2) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:PerformanceMeasure` | carries two different rdfs:label values in the same language (2 texts: pcf_3, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:PerformanceMeasure` | carries two different skos:definition values in the same language (2 texts: pcf_3, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:PerformanceReport` | carries two different skos:definition values in the same language (3 texts: pcf_1, pcf_13, pcf_3) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ProductionEquipment` | carries two different skos:definition values in the same language (2 texts: pcf_2, pcf_4) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ProfitabilityAnalysis` | carries two different skos:definition values in the same language (2 texts: pcf_3, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ProjectPlan` | carries two different skos:definition values in the same language (2 texts: pcf_13, pcf_5) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:RawMaterial` | carries two different skos:definition values in the same language (2 texts: pcf_2, pcf_4) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:RegulatoryAuthority` | carries two different skos:definition values in the same language (5 texts: pcf_10, pcf_11, pcf_12, pcf_2, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:RegulatoryConcernRegister` | carries two different skos:definition values in the same language (2 texts: pcf_1, pcf_2) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:RegulatoryRequirement` | carries two different skos:definition values in the same language (2 texts: pcf_11, pcf_12) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:RegulatoryRequirementData` | carries two different skos:definition values in the same language (2 texts: pcf_2, pcf_8) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:RemediationPlan` | carries two different skos:definition values in the same language (2 texts: pcf_11, pcf_8) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ResearchPublication` | carries two different skos:definition values in the same language (2 texts: pcf_1, pcf_2) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ResourcePlan` | carries two different skos:definition values in the same language (2 texts: pcf_10, pcf_5) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ReturnedProduct` | carries two different skos:definition values in the same language (2 texts: pcf_4, pcf_6) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:RiskAssessment` | carries two different rdfs:label values in the same language (2 texts: pcf_11, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:RiskAssessment` | carries two different skos:definition values in the same language (2 texts: pcf_11, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:RootCauseAnalysis` | carries two different skos:definition values in the same language (4 texts: pcf_1, pcf_13, pcf_4, pcf_6) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:SalesLead` | carries two different skos:definition values in the same language (2 texts: pcf_3, pcf_6) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:SeniorManagement` | carries two different skos:definition values in the same language (2 texts: pcf_1, pcf_2) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ServiceLevelAgreement` | carries two different rdfs:label values in the same language (2 texts: pcf_6, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:ServiceLevelAgreement` | carries two different skos:definition values in the same language (3 texts: pcf_6, pcf_8, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:Stakeholder` | carries two different skos:definition values in the same language (3 texts: pcf_1, pcf_13, pcf_7) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:Supplier` | carries two different skos:definition values in the same language (4 texts: pcf_4, pcf_5, pcf_6, pcf_9) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:TechnologyAssessment` | carries two different skos:definition values in the same language (2 texts: pcf_1, pcf_8) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:TechnologyData` | carries two different skos:definition values in the same language (2 texts: pcf_1, pcf_2) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (wellformedness) | `bpot:TrainingPlan` | carries two different skos:definition values in the same language (2 texts: pcf_13, pcf_5) | *real* | Recorded in baseline (PO decision); harmonization deferred to architect |
| Validation (skos) | `bpot:PCF` (scheme) | Concept scheme has no top concept (skos:hasTopConcept or skos:topConceptOf). | *real* (BPO's catalog never declared one) | **Fixed** (PO decision): the 13 PCF categories, the scheme's only concepts with no `skos:broader`, made top concepts both ways, in `tools/port_from_bpo.py`; SKOS rung now 0. Listed in §3 |
| Validation (realist, warning ×224) | 224 classes (e.g. `bpot:ActOfForecasting` ⊑ `cco:ont00000371` + `cco:ont00000228`) | Class asserts more than one named parent. Asserted single inheritance is the realist default; ... | *false alarm* under BPO's documented convention: a second, allowlisted parent is co-asserted so BPO's offline SHACL anchors resolve (CLAUDE.md "SHACL anchor allowlists"; forecasts `626`+`853`; role enrichment `984`/`187`/`506`). With full CCO in scope many of these are now redundant, an opportunity rather than a defect | None (warnings not gated) |
| Validation (realist, warning ×220) | 220 classes with two named parents | The definition of {X} does not name its parent, "{label}". ... | *false alarm*: knock-on of the co-parent convention. The definition names one parent; the check fires for the other | None |
| Validation (realist, warning ×73) | 73 classes under BPO's own genus `bpot:ActOfIdentification`, labelled "Act of Identification (discernment sense)" | The definition of {X} does not name its parent, "Act of Identification (discernment sense)" | *unsure*, leaning *real* (minor): BPO put a disambiguator in the label (to separate it from CCO's `ont00001261` Act of Identifying), and a correct definition ("An Act of Identification in which ...") can never contain a qualified label. Either BPO moves the qualifier to a comment or `skos:altLabel`, or the template's genus check ignores a trailing `(…)` qualifier. **Corrected 04:30**: first classed as a template bug on the assumption that the label was CCO's; checked, it is BPO's | None (warning) |
| Validation (realist, warning ×5) | classes under BPO's "Act of Communication (shared anchor)" | (as above, label "Act of Communication (shared anchor)") | *real* (minor): BPO put an editorial note into an `rdfs:label` | None (warning) |
| Validation (realist, warning ×13) | `ActOfProduction` (×2), `AnalystRelationsManagementCapability`, `LenderRelationsManagementCapability`, `ApproveImplementationPlanPermission`, `ArchitectureCapability`, `CodeImplementationCapability`, `EvaluationCapability`, `PlanAuthoringCapability`, `Capability`, `Role`, `P20799`, `P20960` | The definition of {X} does not name its parent, "{label}" | *real* (minor): the definition's genus is an ancestor or a near-synonym, not the asserted parent (P20799 "An Act of Design" ⊑ Act of Formulation; P20960 "An Act of Information Processing" ⊑ Act of Analysis; capabilities "An Organization/Agent Capability" ⊑ a more specific capability) | None (warning); for the architect |
| Validation (realist, warning ×3) | `P11042`, `P11043` (filler `BoardOfDirectors`), `P19596` (filler `RegulatoryAuthority`) | Class {X} restricts cco:ont00001922 to {Y}, which is not known to fall under the property's range cco:ont00001017 | *real*, rooted upstream: the fillers are Organizations (`1180`), which in CCO 2.0 are Groups of Agents, not Agents (`1017`). BPO's notes record this gap | None (warning) |
| Validation (realist, warning ×2) | `ServiceProvider`, `SupplyChainOrganization` | Class {X} is restricted on cco:ont00001954, whose domain cco:ont00001017 it is not known to fall under | *real*, same Organization ⊄ Agent gap (`has capability` said of an Organization) | None (warning) |
| Test suite (first full run, stopped) | — | 15 h 29 min, ~52% done, stuck in a release build (§7) | *template bug* (scale) | Stopped on PO instruction; re-run without the 8 release-build tests |
| Test suite (re-run, 10-25 20:37–21:44) | `test_iri_lint.py` ×3 | `naming_convention bpot:P10530_SuggestionProgram` | *real* (the known IRI-lint finding) | Not fixed (PO decision) |
| Test suite | `test_site.py` ×4 failed + 21 errors | `Refused: bpot:bearsPermission has no skos:definition. The site publishes what the ontology asserts, with no fallback.`; 19 of the errors are pytest's own `assert not self._finalizers` after the failed fixture | *real*: BPO documents all 10 properties in `rdfs:comment`, none in `skos:definition` | **Fixed** with PO-approved definitions (§3); site tests re-run |
| Test suite | `test_ontology_checks.py::test_the_upstream_vocabulary_the_shapes_walk_is_in_scope` | passed, but its **setup took 3,056 s** (a full ladder measurement) | *template bug* (scale) | None |
| New project tests (10-26) | `tests/test_bpo_port.py`, 27 tests | first run: 26 passed, 1 failed: `ontology/sections/pcf_5.ttl` holds APQC text but its header names no framework | *real* (BPO slices 5 and 6 had no `dct:source`; no slice named the release) | Fixed: release cited on every such module (§3); 27 passed |
| Validation (annotation-profile, warning ×3,119) | every class | Class has no definition source. CCO cites the source of each definition with this annotation; ... | *real* (BPO records no per-definition source; the APQC row is in `apqcSourceText`/`pcfID`, the modelling rationale in `rdfs:comment`) | Not fixed; warnings are not gated. Mapping BPO's provenance to the profile's annotation is a modelling call for the architect |

## 5. Template files you changed

The output of `python tools/template_status.py` at the end, pasted whole:

```
  94 owned file(s); recorded f1412848cc58f36e (unreleased), now 54c93e746583595c
    changed  tools/ontology/validate.py
    added    tests/test_bpo_port.py

  this project has diverged from the template it was made from in the files above. That is allowed; it is what the next template update will have to merge.
```

For each file it lists:

| File | What you changed | Why the template did not work as it was |
|---|---|---|
| `tools/ontology/validate.py` | Added `bind_this_inline()`, called from `run()`: when pyshacl pre-binds an **IRI** focus node to `$this` in a SPARQL constraint, the IRI is also written into the query's outermost WHERE braces. The binding is kept, so projections and `{$this}` messages are unchanged; a blank-node or literal focus is untouched. No shape, baseline or threshold changed. Approved by the PO (§6, 15:02) | pyshacl passes `$this` as an rdflib `initBindings`, which rdflib joins *after* evaluating the pattern: every focus node paid for a whole-graph evaluation of `subClassOf*`/`FILTER NOT EXISTS`, making the realist rung ~O(n²). BPO-sized corpus: did not finish in 1 h 56 min (killed); realist rung alone 1,390 s on 1/13 of the corpus. Equivalence evidence: see §7 (15:45) |
| `tests/test_bpo_port.py` (**added**, not changed) | New file: the 27 tests the PO required (property kinds, derived capability mapping, Boolean `routable`, PCF release provenance, drift held to `config/annotation-drift.tsv`) | `template_status.py` reports it as `added` under the template-owned `tests/` component: a project has nowhere of its own to put tests the suite will run, so any project test reads as divergence from the template |

## 6. Questions you had to ask

| When | Question | Who answered | Time lost | Was the answer in the docs? |
|---|---|---|---|---|
| 13:17 | Where is the report form? The request says it is attached; it was not, and the template has no `research/port-report.md` | Aaron (sent the form at 13:20) | ~0 (kept going, drafted structure meanwhile) | no (process gap in the request, not the template) |
| 15:02 | The validation ladder cannot finish on BPO (realist shapes, ~O(n²) in pyshacl/rdflib). Patch the template's `validate.py`, stop the milestone, or stop the port? | Aaron: patch `validate.py` (template-owned), prove equivalence, log it in §5 | 1 h 15 min (the diagnosis, §7) | no. Nothing in the template states a size limit or how long the ladder takes |
| 10-24 16:35 | Validation: (a) scheme `bpot:PCF` has no top concept: fix? (b) 57 violations are cross-slice definition/label drift in BPO: harmonize, record in baseline, or leave the gate red? | Aaron: (a) fix mechanically; (b) record in baseline as known, with the reason | **Waiting ~11.5 h overnight** (answered by 10-25 04:05; not counted as hands-on). Hands-on cost ~10 min | no. The template has no guidance for porting an ontology that arrives with findings: the baseline starts at 0 for an empty module, and `--accept-regression` is described for regressions, not for a starting inventory |
| 10-25 21:50 | The site refuses BPO's 10 properties (no `skos:definition`): draft definitions, copy comments, or leave the site broken? | Aaron: draft for review. Then (10-26) **approved with edits**: replacement texts for all 10; the three `requires…` re-typed to annotation properties; `bearsPermission` as a policy association; `enablesProcess` narrowed to a required capability; tests for property kinds, the derived mapping, Boolean `routable`, PCF release provenance, and a comment-drift check | **Waiting ~5.5 h overnight** (not hands-on). Review itself ~15 min; implementing the conditions ~45 min | no. The template's validation ladder does not require a property definition, but its site builder does; nothing tells a porter that before the Pages build fails |
| 14:00 | Rename `P10530_SuggestionProgram` to satisfy `naming_convention`, or keep it? | Aaron: keep; classify as real, not fixed | ~5 min (worked on in parallel) | no. The template says nothing on how a project keeps a known, accepted finding open: the linter has no baseline or waiver, so CI's IRI-lint step stays red until the term is renamed |

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
| 13:31 | Dependabot | A Dependabot PR (`actions/setup-python` 7.0.0 → 7.1.0) opened 2 min after the repo was created: the template's pinned actions were already stale at copy time. Its three PR runs ended `action_required`. Left alone, not part of the port | 0 |
| 13:32 | `gh run watch` on Reasoning | Exited 1 twice while the run was still in progress (GitHub API 502s), not a template issue; polled `gh run view` instead | 2 min |
| 13:35 | `CLAUDE.md` (rendered by init) | "Nothing is pushed without the architect's say-so": the first push (needed for CI, step 5) had already happened with the PO's go-ahead for the port. README step 5 assumes a push to main; the rendered CLAUDE.md forbids one. The two need reconciling | 0 |
| 13:36 | `config/naming.yaml`, DEVELOPMENT "Writing a term" | Template decision 4 wants readable local names; BPO's own decision D7 deliberately moved from readable IRIs to `bpo:P<pcfID>` (1,823 process classes) and `PCF_<id>` (1,921 concepts). The class regex `^[A-Z][A-Za-z0-9]*$` accepts `P10002`, so nothing enforces decision 4. **Kept BPO's local names** (namespace swap only) to preserve PCF traceability; recorded here rather than asked | 5 min |
| 13:37 | `mappings/README.md`, `tools/ontology/mappings.py` | The request asks for "old IRI to new IRI"; the checker requires the subject to be a term a module here declares, so rows run new → old (`bpot:X skos:exactMatch bpo:X`). Direction inverted against the request's wording | 0 |
| 13:38 | DEVELOPMENT "Adding a file" | Clear and sufficient: four new modules declared in `config/repository-layout.yaml` (not template-owned); `tools/layout.py` ok first time. Unclear whether a ported-once module should carry `generator:`; left it off so CI never needs the BPO checkout | 3 min |
| 13:40 | `vendor_upstream.py --rebuild` | 133 seeds → 151 CCO/BFO terms, CCO extract rebuilt; no problems | 0 |
| 14:05 | `.github/workflows/checks.yml`, `iri_lint.py` | PO decided to keep `P10530_SuggestionProgram` and leave CI red. **Template defect, two parts:** (1) the IRI linter has no baseline or waiver, unlike `validate.py --gate`, so a known, accepted finding cannot be carried; (2) Checks is one fail-fast job, and IRI lint is step 9 of 16, so a red lint stops competency, mappings, generated-file currency, normalize, communications, template-status and the **whole test suite** from running in CI. One accepted finding blinds 8 checks. Worked around by running those 8 locally and recording the results here; CI evidence for them is missing. No template file changed | 5 min |
| 13:43–15:00 | `tools/ontology/validate.py` + `shapes/realist_shapes.ttl` | **Blocker. The validation ladder cannot finish on BPO.** First full run started 13:43; still running at 15:00 (one core pegged, ~200 MB), no output (stdout is buffered when redirected, so there is no progress either). Timed each shape set on core + PCF 11 only (2,616 triples, ~300 classes): wellformedness 34.5 s, **realist 1,389.5 s**, annotation-profile 0.4 s, skos 0.4 s. Cause, measured: pyshacl passes the focus node as a pre-binding, and rdflib applies pre-bindings *after* evaluating the pattern, so each focus node pays for the whole graph. "Anchored" constraint on one focus: 0.865 s pre-bound vs 0.028 s with the IRI inlined (31×); cost per focus grows with the graph, so the total is ~O(n²). The full corpus is ~20× the triples and ~10× the classes: on the order of days, beyond GitHub's 6 h job limit. **Template defect**: the realist shapes as written (per-focus `subClassOf*` + `FILTER NOT EXISTS`) do not scale past a toy ontology on pyshacl/rdflib; the template has no timing test at realistic size | 1 h 15 min |
| 15:45–15:54 | `validate.py` patch, equivalence | Ran every shape set unpatched and patched (separate processes) over (a) every negative fixture and (b) core + PCF 11, comparing the full result records (focus, shape, severity, message with substituted values). **All 8 identical** (9/25/10/10 fixture results; 0/69/158/0 on core+PCF 11). Realist on core+PCF 11: 685 s → 147 s (4.7×; the per-query gain was 31×, so constraints not led by `$this` still cost). Fixture times unchanged within noise | 10 min |
| 15:56 | `tools/licensing/disposition.py --check` | Passes, and that is a finding: the modules carry **3,757 verbatim APQC PCF passages** (`bpot:apqcSourceText`), classified with their files as MIT `project-content`. Licensing is decided per file, so third-party text inside an authored module is invisible to it. The template's promise ("licensed reference material kept out") holds for files, not for content. In BPO this is a **real** issue (APQC text redistributed under MIT with no APQC attribution); the template did not catch it. Not changed in the port; flagged for the PO | 0 |
| 15:56 | `mappings.py` / SEMAPV | 5,051 rows, 0 findings first time. SEMAPV has no justification for "same term, namespace moved"; used `semapv:UnspecifiedMatching` + `mapping_tool` + a comment. The mappings README frames sets as crosswalks to *other* vocabularies and has no guidance for a predecessor/port mapping | 5 min |
| 10-25 04:10 | `config/validation-baseline.json`, `validate.py --record` | The baseline is one **count per rung** (`authored_findings: 57`), not a list of findings. Fixing one drift and introducing an unrelated violation in the same rung passes the gate unchanged; the identity of the 57 lives only in this report. A known-findings baseline needs finding identity (focus + shape), as BPO's own Gate F does by category | 0 (noted) |
| 10-25 04:19 | `validate.py` speed | Each full ladder run costs ~35 min even patched (realist ~30 of it). Every iteration here (detail, re-record, gate) is another 35 min; the JSON report keeps only 20 sample warnings, so the warning breakdown needed a separate run | 35 min |
| 10-25 05:07–20:36 | `pytest tests/` on the ported corpus | The suite took 6 min on the empty module. On BPO, after **15 h 29 min** it had run ~156 of ~299 tests (52%) with 3 failures (names print only at the end under `-q`), then sat in `test_release.py::test_two_builds_are_byte_identical_across_hash_seeds`: one `release.build()` subprocess at 100% CPU for 5 h 22 min (15:14 → 20:36), with a second build still to come. **Stopped at 20:36 on the PO's instruction**; re-run with the seven release-build tests deselected (`test_release.py` lines 74–160, `test_vocabulary.py::test_a_release_ships_the_diff_inside_its_checksums`) | 15 h 29 min (unattended) |
| 10-25 20:36 | `tools/release.py` | **Template defect: the release pipeline cannot build BPO in useful time.** `build()` canonicalizes every artefact graph with `rdflib.compare.to_canonical_graph` (for byte-identical builds) and re-checks each of 3 serializations with `isomorphic()`. BPO has 4,381 blank-node restrictions, many structurally alike (`someValuesFrom` on a few properties), the case where rdflib's canonicalization degrades badly. One build: >5 h 22 min unfinished; the test builds twice; the Release workflow builds twice too. **Tagging a release is blocked** for an ontology of this shape. Not changed (PO decision: deselect, record) | (counted above) |
| 10-25 08:13 | `.gitattributes` / report | Git warned that `research/port-report.md` had CRLF line endings: the agent's file-write tool on Windows wrote CRLF, as the rendered CLAUDE.md warns. Normalized to LF. `.gitattributes` converts on commit anyway, so this cost nothing | 1 min |
| 10-25 21:50 | `tools/site/build_site.py` vs the shapes | **Template defect:** the site builder refuses a term with no `skos:definition` (or with two per language), a rule the validation ladder does not check for properties. The port passed the gate it was given and would have failed only at the Pages deploy. The same rule should be a shape (or the site should read the ladder) | 20 min |
| 10-25 21:50 | site term index | The site checks one module at a time, so a class whose definitions drifted across modules (51 here) publishes the first module's text and never shows the conflict. The validation ladder reports it; the public site hides it | 0 (noted) |
| 10-26 03:20 | `rdfs:comment` texts | Kept verbatim, PO decision: comments still name old CURIEs ("DERIVED from bpo:enablesProcess", "bpo:PCF_<pcfID>"). Provenance text is not rewritten; a reader sees the old prefix. Known port limitation | 0 |
| 10-26 03:24 | drift beyond the gate | Comments are checked by nothing in the template: 53 terms carry differing `rdfs:comment`s (`designatesProcessType` has 7). Added `config/annotation-drift.tsv` (266 variants, 110 term/property pairs: 53 comment, 51 definition, 6 label) and a test that holds the modules to it exactly, by identity, unlike the count-only validation baseline | 15 min |
| 10-26 03:26 | `tests/` (declared `template: owned`) | The PO's tests went into `tests/test_bpo_port.py`, the only place the suite runs. The directory is template-owned, and `template_status.py` lists the file as `added` (§5): a project's own tests have no declared home. Site tests re-run 03:33–03:44: **38 passed** (11 min) | 0 |
| 13:31 | `.githooks/` | README table promises the IRI linter "in a git hook", but `core.hooksPath` is unset after cloning and the README never says to run `git config core.hooksPath .githooks`. The hook is inactive by default | 0 (noted) |

## 8. Overall

- **Did you finish within the timebox?** Yes, for the port: complete, mapped, reasoned, validated against a recorded baseline and published 1 day 15 h after starting (timebox 3 working days; target 2 days). Not for "everything green": Checks stays red at IRI lint by the PO's decision to keep `bpot:P10530_SuggestionProgram`, and **releases cannot be built** (`tools/release.py` does not finish on this corpus). First green CI took 26 min against a 2 h target.
- **Would you start your next ontology from this template?** **With changes.** Setup was fast and clear (init, layout contract, vendoring, mappings, reasoning all worked first time, and the README was enough for setup). But the checks were built and timed on toy ontologies. Three of them (the realist shapes, the test suite, the release build) do not complete at BPO's size without a change, and one needed a template-file patch just to finish. A template that cannot validate or release a 3,000-class ontology is not yet ready to bet new work on.
- **The three changes to the template that would have saved the most time:**
  1. **Make the checks scale, and test that they do.** Inline the focus node in SPARQL constraints (the patch in §5, or an upstream pyshacl/rdflib fix); replace `to_canonical_graph` in `release.py` with a canonicalization that copes with thousands of similar restrictions; add a size test (thousands of classes and restrictions) to the template's own suite with a time budget. This cost ~3 h hands-on and ~20 h of machine time.
  2. **Let a project carry known findings everywhere, by identity.** The validation baseline is a count per rung; IRI lint has no baseline at all; the site refuses outright. A port arrives with findings. One mechanism (a list of findings, each with focus, check and reason) honoured by every check would have avoided the red Checks job, the fail-fast masking of 8 steps, and two questions to the PO.
  3. **One contract for what a term must carry.** The site requires a `skos:definition` on every authored term and one value per language; the ladder does not check either for properties. Put the site's rules in the shapes (and document them), so a port fails at the gate, not at deploy. Also say where a project's own tests go (`tests/` is template-owned) and how to map a predecessor ontology in SSSOM (no `semapv` justification fits a namespace move).
- **Anything the template made easier than you expected:** `init_project.py` (one clean run, ~1 min); the layout contract (four modules declared, right first time); vendoring by reference (133 seeds to a 151-term extract with no hand work); the SSSOM checker (5,051 rows, 0 findings first time); the IRI linter (one true finding across 5,051 terms, no noise); the reasoner (ELK over the full pinned BFO + CCO, 1 min locally); the falsification fixtures, which made it possible to *prove* the `validate.py` patch changed nothing; and the validation gate's refusal to raise a count without a stated reason, which forced every accepted finding into words.
