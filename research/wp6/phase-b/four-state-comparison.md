# WP6 Phase B — the four-state comparison (A9)

2026-11-04. What changed between S0, S1, S2u and S2, and why. This states what changed,
not whether it is better: that judgment is in `quality-evaluation.md` (A9 §7).

**A9** is a protocol amendment, submitted by the BPO architect and accepted by the Template
Team on 2026-10-31 (template decision 24). It adds the state **S2u**, the corrected BPO
source through the unchanged port, so that BPO's corrections can be separated from the
template's effect. Its three clarifications apply throughout this record:

1. the template instrument stays v0.1.0;
2. the template-prompted changes BPO adopted count with the template's effect;
3. the kept `dct:rights` notice is a declared change to the port's mechanics.

## 1. The states

| State | BPO source | Port mode | Tag | Content commit |
|---|---|---|---|---|
| S0 | `bc64e91` | `--unchanged` | `s0` | `3690d2a` |
| S1 | `bc64e91` | the four PO-approved changes of 2026-10-26 | `s1` | `c062662` |
| S2u | `2b86c91` | `--unchanged --carry-headers` | `s2u` | `7d7cfa5` |
| S2 | `2b86c91` | `--carry-headers`; the four changes made only where the source lacks them | `s2` | `fdcf000` |

- **The S2 source.** BPO `2b86c91800336044f7ca4e5c21459245fe54a8ee` is 39 commits on
  `685f1f2`, accepted by the BPO architect on 2026-11-04 (`change-record.md` §10).
- **Measured** with v0.1.0 (template `a754332`), Python 3.12.10 and the S0/S1 manifest's
  distributions, ROBOT 1.9.11 with ELK, CCO `v2.0-2024-11-06` (`510dad7`) and BFO
  `044490f`. Each state's `manifest.tsv` records all of it.

### Declared changes to the port's mechanics and dependencies (A9 §5)

They apply to S2u and S2 alike, so S2u → S2 holds them fixed. S0 → S2u carries them besides
BPO's corrections, and they are separated here.

| Change | Port commit | Touches | Effect on the measures |
|---|---|---|---|
| The four changes made only where the source lacks them | `785d9b2` | port tool | On `bc64e91` the tool rebuilds S0 and S1 byte for byte. On `2b86c91` it makes none of them (§2) |
| `--carry-headers`: BPO's `dct:rights` (B2), and BPO's titles, version and commit as a `dct:source` literal (B18) | `785d9b2` | module headers only | Outside the lossless check. Headers: S0 → S2u, 11 statements removed and 45 added |
| The mapping set names the BPO commit read, not a fixed `bc64e91` | `785d9b2` | SSSOM header | none |
| APQC's PCF text declared as third-party (B2): `apqcSourceText`, `pcfID`, `hierarchyID` | `9c7fc33` | `config/third-party-text.yaml` | Holds S2u/S2 to the declaration. Gives no finding: each module with these values carries the source, release and notice |
| CCO extract re-vendored from the same pins: + `ont00000870`; − `ont00000117`, `ont00000595`, which the corrected content no longer names | `4bf822e` | `vendor/` | Necessary. Without it v0.1.0 did not evaluate the annotation-profile rung (first run `d446e52`, superseded by `838120e`) |

S0 and S1 keep their Phase A measurements. Each was made with the extract that matched its
own content.

## 2. S2u → S2: the template's effect on the corrected source

**None. S2 is byte for byte S2u:** the ontology, mapping set, drift inventory and corpus
digest are identical (`s2` is an empty commit on `s2u`). The findings are identical by
identity (1,829), and so are the entailments (19,109 pairs).

**Why.** BPO adopted all four port changes the template process prompted (B3 `0fa372e`,
B5 `af7f65f`, B6 `8245f8b`, B12 `873404b`). With each already in the source, the port has
nothing left to make.

**This is not the template's whole effect.** Under clarification 2:

- its process effect is **S0 → S1** (§3);
- plus **the four back-ports**' share of S0 → S2u;
- plus **the BPO corrections of defects that template checks detected** (§6), whose
  correction was BPO's.

## 3. S0 → S1: the template process on the original source (Phase A, unchanged)

- **Statements:** 3 removed, 39 added. These are the 3 re-typed properties, 10 property
  definitions and 26 top-concept links, exactly the four changes.
- **Headers:** 13 release citations added.
- **Entailed hierarchy:** identical (19,112).
- **Findings:** 4,323 → 3,749. 574 removed, none new: K02 563, K14 10, K15 1.

## 4. S0 → S2u: BPO's corrections, through the unchanged port

### 4a. Asserted statements (outside the headers)

Lossless check, S2u against its source: 50,664 = 50,664, none missing, none extra.
Against S0, 989 statements are removed and 2,317 added.

| Statement kind | Removed | Added | Cause (BPO commits) |
|---|---:|---:|---|
| `ont00001754` definition source | 0 | 1,831 | B14 `001b327`: one per APQC-derived class |
| `requiresCapability` (class-level annotation) | 358 | 0 | B8 `6b95ce5`: none of the pairs is a shown necessity. The three kept delivery requirements are in `bpot.ttl`, unchanged |
| `rdfs:subClassOf` restriction | 220 | 16 | 199 realized-in (`BFO_0000054`): B8 step 1 `8fe1246` (197) and Decision A `da2e573` (2). Then 4 participant restrictions on `ITServiceSolution` users (`6d2b1fa`), the `PerformanceMeasureSpecification` repointing (`d80496f`) and the CustomerProfile split (`9e48392`) |
| `rdfs:subClassOf` named parent | 28 | 24 | See 4b |
| `skos:definition` | 213 | 153 | B1 `5dff7de`/`448cc2c` (51 reconciliations, so one per term); B9 `103405b`; B8 `702641c` (57 "can be realized"); B5 (properties) |
| `skos:scopeNote` | 0 | 90 | 85 are B1's replaced module-specific definitions, each kept as "As used in section N before WP6 B1"; 3 are the B10 qualifiers moved out of labels (`02991d9`); 2 are the `enablesProcess` and `requiresCapability` interpretations (`1686f4e`, `7165716`) |
| `rdfs:comment` | 129 | 131 | dated correction notes on the changed classes |
| `rdfs:label` | 16 | 15 | B1, B10 `02991d9` (editorial qualifiers) |
| `owl:deprecated`, `dct:isReplacedBy` | 0 | 3 + 3 | `bearsPermission` (B7), `SeniorManagementRole` (B1), `ActOfCommunication` |
| `enablesProcess` | 13 | 0 | B8 |
| `inGrouping` | 0 | 7 | B13 K07 `5484bed` |
| `permissionApplicableToRole` / `bearsPermission` | 0 / 1 | 1 / 0 | B7 `afe86cc` |
| `rdf:type`, `hasTopConcept`, `topConceptOf` | 5 / 0 / 0 | 10 / 13 / 13 | B6, B12; new classes (`SupplierSolicitation`, `PerformanceMeasureSpecification`, …) |

### 4b. Entailed class hierarchy (ELK, indirect pairs included)

**19,112 → 19,109 pairs.** 50 are lost and 47 gained, and 14 pairs are entailed in both
states but asserted in only one. Every change traces to a decision:

| Change | Pairs | Cause |
|---|---|---|
| P11035, P11036: capabilities → acts (`ActOfRelationshipManagement`, Social Act `1327`) | −14 / +14 | Decision A `da2e573` |
| `ITServiceSolution`: Information Processing Artifact → Infrastructure System (`870`) | −2 / +1 | `6d2b1fa` |
| P12721: Act of Cargo Transportation (`595`) → `ActOfTransportation` | −1 / +1 | `027be8a`, `0e2791b` |
| P20645, P20838, P20860, P20899, P20926: `ActOfCommunication` → CCO `402` (+ `228` asserted) | −5 | `ff87b3b` |
| P20799: `ActOfFormulation` → `ActOfDesign` | −1 / +1 | B9 `103405b` |
| 7 delivery roles leave the `Role` marker | −7 | B13 K07 `5484bed` (membership by `inGrouping`) |
| `Facility` retired for CCO Facility | −6 | B10 `fb42d66` (IRI not kept; recorded in BPO `docs/migrations.tsv`) |
| `ITInfrastructureComponent` ⊑ `117` removed | −1 | B13 `df04151` |
| `P10530_SuggestionProgram` → `SuggestionProgramManagement` | −6 / +6 | B4 `4da56d7` |
| `SeniorManagementRole` loses its chain | −6 | B1 `d117716` (see §5) |
| RFP: Descriptive (`853`) → Directive (`965`); RFP and RFQ under `SupplierSolicitation` | −1 / +8 | B10 `84ba743` |
| `RegulatorRole` ⊑ `RegulatoryAuthorityRole` | +1 | `04ef72d` |
| New classes: `PerformanceMeasureSpecification`, `CustomerDataSpecification`, `CustomerSegmentProfile` | +15 | `d80496f`, `9e48392` |

**Equal hierarchies are not semantic equivalence**, and the converse holds too. The largest
semantic change in Phase B moved no entailed pair: B8 removed 197 axioms saying every
capability *is* realized in some process, and 358 requirement links that dispatch read as
necessities. The named-class hierarchy is blind to both.

### 4c. Annotation text

| | S0 | S2u |
|---|---:|---:|
| Drift inventory: variants (term/property pairs) | 266 (110) | 111 (45) |
| Two definitions in one language (K09) | 51 | 0 |
| Two labels in one language (K10) | 6 | 0 |
| Two comments, across modules (K08 / K18 / K19) | 43 / 7 / 3 | 35 / 7 / 3 |

The remaining comment variants are, by B1's decision, module-specific notes that were kept.

### 4d. Intended interpretation of relations

- **`requiresCapability`**: generated as the inverse of `enablesProcess` and read as "the
  agent must bear it". It is now asserted only where a necessity is shown: the three
  delivery acts, under the architect's interpretation of 2026-11-03 (bearer = performer;
  evidence before assignment).
- **`enablesProcess`**: relabelled "can be realized in process", a possible realization.
- **`bearsPermission` → `permissionApplicableToRole`**: an annotation-level association
  between kinds, not BFO's bearer relation.
- **57 capability definitions** say "can be realized in". The text no longer claims a
  necessity that no axiom carries.
- **`requires*`**: annotation properties (B6). They were object properties asserted between
  classes, which OWL reads as punning.

### 4e. Validation and operational behaviour

| Measure | S0 | S1 | S2u = S2 |
|---|---:|---:|---:|
| Template findings, by identity | 4,323 | 3,749 | 1,829 |
| … of which violations | 632 | 58 | **2** |
| Reasoner | consistent | consistent | consistent |
| Entailed pairs | 19,112 | 19,112 | 19,109 |
| Site build and check; release build | pass | pass | pass |
| BPO Gate F capability-as-process (K11) | 39 | 39 | 37 |
| BPO dispatch (12-agent demo fleet): processes with requirements / routable / gaps | 453 / 64 / 389 | — | 197 / 30 / 167 |

**The dispatch figures are not comparable as rates.** The 256 processes that carried only an
unshown capability requirement are *not assessed* by requirement-based dispatch (BPO
architect, 2026-11-03, §4D). The earlier 64 counted assignments justified by requirements
nobody had shown to be necessary. None of the 197 processes that kept requirements lost
routability.

## 5. Findings, class by class (S0 → S2u, by identity)

| Class | S0 | S1 | S2u | Persist | Resolved | New | What moved |
|---|---:|---:|---:|---:|---:|---:|---|
| K01 no definition source | 3,119 | 3,119 | 1,291 | 1,286 | 1,833 | 5 | B14 gave the 1,831 APQC-derived classes a source (2 others left the corpus). BPO-authored definitions are left without one, since their authorship is open. The 5 new are new BPO-authored classes |
| K02 class-to-class object property | 563 | 0 | 0 | 0 | 563 | 0 | B6 (S1 by the port; in S2u by BPO) |
| K03 genus is a redundant co-parent | 145 | 145 | 160 | 144 | 1 | 16 | **Rises.** Definitions now name the specific parent (B9; the 5 slice 8 acts; capability definitions under their capability genus). The co-asserted allowlist parent (`568`, `228`, `BFO_0000040`) is left unnamed. An accepted architecture exception (B13) |
| K04 / K05 genus not named | 77 / 11 | 77 / 11 | 57 / 4 | 57 / 4 | 20 / 7 | 0 | B9 (88 reviewed one by one) |
| K06 redundant extra parent | 216 | 216 | 218 | 212 | 4 | 6 | Kept by decision (B13). +6 from the same co-assertion pattern |
| K07 genuine extra parent | 8 | 8 | 0 | 0 | 8 | 0 | B13 K07 (7 roles); `ITInfrastructureComponent` |
| K08 / K18 / K19 comment drift | 43 / 7 / 3 | same | 35 / 7 / 3 | 35 / 7 / 3 | 8 / 0 / 0 | 0 | B1 (comments kept where module-specific) |
| K09 / K10 definition / label drift | 51 / 6 | same | 0 / 0 | 0 | 57 | 0 | B1 |
| K11 P-class under Organization Capability | 39 | 39 | 37 | 37 | 2 | 0 | Decision A |
| K12 / K17 parenthetical label | 9 / 9 | same | 1 / 9 | 1 / 9 | 8 / 0 | 0 | B10. The 1 left is the deprecated `ActOfCommunication`'s "(shared anchor)"; K17 is APQC's own names (false alarm) |
| K13 Organization where CCO wants an Agent | 5 | 5 | 5 | 5 | 0 | 0 | B11: documented, upstream |
| K14 / K15 / K16 | 10 / 1 / 1 | 0 / 0 / 1 | 0 | 0 | 12 | 0 | B5, B12, B4 |
| **K20** class without definition | 0 | 0 | 1 | — | — | 1 | **Regression.** See below |
| **K21** class reaches no BFO category | 0 | 0 | 1 | — | — | 1 | **Regression.** See below |
| **Total** | **4,323** | **3,749** | **1,829** | 1,800 | 2,523 | 29 | |

**K20 and K21** are proposed classes, pending the BPO architect under A6
(`classification.md`, 2026-11-04). Both findings are on `bpot:SeniorManagementRole`. BPO's
B1 consolidation (`d117716`) deprecated the class and removed its definition and parent.
The template's deprecation policy keeps both, and BPO's later deprecation of
`ActOfCommunication` (`ff87b3b`) did keep them. BPO's gates do not check deprecated classes
for either. **This is the only regression from S0 to S2.** It was introduced by a Phase B
correction and detected by the template. The correction scope is closed, so it is
recorded as a recommendation.

## 6. Where each change came from (A9 §6)

| Origin | Items |
|---|---|
| **Template process: port changes, back-ported to BPO** (count with the template's effect, clarification 2) | B3 (found by the port team's own provenance test), B5, B6, B12 |
| **Detected by template checks, corrected by BPO** | B1 (definitions, labels, comments; incl. PerformanceMeasure, CustomerProfile, RegulatorRole), B4 (IRI lint), B9 (incl. `ActOfCommunication`), B10 (incl. RFP/RFQ, Facility), B11, B13 (incl. K07), B14 (annotation profile) |
| **Detected by BPO's own gates, corrected by BPO** | Decision A (Gate F's capability-as-process rule, which the template's configured scheme rule reproduces exactly as K11) |
| **Detected by human review** | B2 (licensing), B7, **B8** (the 356 pairs, 197 axioms, 57 definitions, delivery requirements), B16, B17, B18, `ITServiceSolution`, P12721 (found in the CCO-pin evidence work, E-B1) |
| **Detected by the experiment's comparison, not a check** | E-B1, the CCO pin defect (template digest pinning made it visible) |
| **Introduced by a correction, detected by the template** | K20/K21, `SeniorManagementRole` |

## 7. Measurement incidents in this run

- **The first S2u/S2 measurement was invalid** (`d446e52`). The port's CCO extract lacked
  the newly named `ont00000870`, and v0.1.0 reported the annotation-profile rung NOT
  EVALUABLE. The instrument then measured that state on three of four rungs without failing.
  K01 read 3,119 → 0 and K08/K18/K19 53 → 0. Found by checking K01's fall against the
  1,831 definition sources actually added. The extract was re-vendored from the same pins
  (`4bf822e`) and both states re-measured (`838120e`). Template finding, in
  `quality-evaluation.md`.
- **The test environment.** The suite run in the system Python or in the port's own
  `.venv` fails 39 tests (no `pyoxigraph`, no `markdown`; the `.venv` predates the Phase A
  pins). All measurements here ran in the Phase A environment, whose distributions equal
  the S0/S1 manifests.
- **Classifier.** `wp6_classify.py` put every placement-shape finding in K02. Narrowed to
  the message, with S0 and S1 reclassified byte for byte (proposed with K20/K21).
