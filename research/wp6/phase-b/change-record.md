# WP6 Phase B — change and decision record, B1 to B18

**Status: DRAFT, for the BPO architect.** Every disposition below is *proposed*. Nothing has
been changed in BPO. The trials of the back-port candidates ran in scratch copies of BPO and
were thrown away (§3).

**Governing direction:** the BPO architect's memo of 2026-10-31. The experiment tests the
template, not the reproduction of BPO. It has two objectives, kept apart:

1. **What changes:** this record.
2. **Whether the result is better:** the separate quality review, after S2.

Zero semantic drift is not the success criterion. A change counts as evidence once it is
traceable: what changed, why, what caused or detected it, and with what effect.

## 1. The experimental design

### States

| State | BPO source | Port changes | Status |
|---|---|---|---|
| **S0** | `bc64e91` | none (`--unchanged`: only namespace, headers, 3 dropped CCO restatements) | tagged `s0` (`3690d2a`), immutable |
| **S1** | `bc64e91` | the PO-approved port changes of 2026-10-26 (B3, B5, B6, B12) | tagged `s1` (`c062662`) |
| **S2u** | the S2 commit | none | **proposed** |
| **S2** | the S2 commit (one BPO commit, with the approved BPO-side corrections) | the approved port changes | to be built |

**S2u is the unchanged-source comparison the memo asks for.** With four states, each effect
has its own comparison:

| Comparison | Holds fixed | Isolates |
|---|---|---|
| S0 → S1 | BPO source | the template process (the port changes, and what prompted them) |
| S0 → S2u | the port (unchanged) | BPO's own corrections |
| S2u → S2 | BPO source (corrected) | the template process on the corrected source |
| S0 → S2 | — | both together: the overall result |

If a back-port candidate (B3, B5, B6, B12) is adopted in BPO, it appears in S2u too. Its
*origin* stays recorded here: the mechanism column says it came from the template process,
not from an independent BPO correction.

This adds a state to the protocol as amended by A1 to A8. The Template Team should be told
(a proposed amendment A9) before S2 is measured.

### What is measured, for every state

| Measure | Tool | Says |
|---|---|---|
| Statements | `tools/lossless_check.py` | every BPO statement accounted for, and every addition |
| Findings, by identity | `tools/wp6_measure.py`, `tools/wp6_classify.py` | which defects each check reports, each in a class |
| Entailed class hierarchy | `tools/wp6_entailments.py` (ELK, pinned ROBOT) | every entailed superclass of every class, and which are asserted; separates asserted-axiom changes from entailment changes |
| Annotation drift | `config/annotation-drift.tsv`, `tools/wp6_b1.py` | each variant, its module, and the BPO commit that introduced it |
| BPO's own gates on a BPO-side change | `tools/wp6_backport_trial.py` | Gates A–D ×13, corpus ELK + Gate F, C1–C7, matchability, consistency audit |
| Reproducibility | `tools/wp6_manifest.py` | content and instrument commits, template revision, every Python distribution, Java, ROBOT sha256, upstream artifact digests, sha256 of every check, shape and config file |

`research/wp6/measure/s0/` and `s1/` now hold `manifest.tsv` and `entailments.tsv` beside the
Phase A findings.

### The S2 commit

**Not yet selectable.** It is the BPO commit that carries the corrections approved from this
record. It will be `685f1f2` or later (BPO's answer of 2026-10-30: S2 carries APQC's notice).

## 2. What is already measured

- **S0 and S1 entail the same class hierarchy.** 3,119 classes, 19,112 entailed superclass
  pairs, of which 3,343 are asserted, in both states. The 574 findings S1 removes are
  therefore all annotation-level, or punned-individual, changes. No class's place in the
  hierarchy moved.
- **The B13 candidate is asserted-only.** Removing the 216 redundant parents leaves the 19,112
  entailed pairs unchanged, with 3,127 asserted. It removes exactly 361 findings (216 K06 and
  145 K03) and adds none.
- **Every one of the 266 drift variants is traced** to the BPO commit that introduced it
  (`b1-origins.tsv`), and each of the 110 drifted term/property pairs is classified
  (`b1-terms.tsv`).

## 3. The back-port trials in BPO

Each candidate was applied alone to a scratch worktree of BPO at `685f1f2` and BPO's own
gates were run (`trials/<candidate>.tsv`, full output in `trials/<candidate>.log.txt`).

| Gate (BPO's own) | baseline | B3 | B5 | B6 | B12 | B13 |
|---|---|---|---|---|---|---|
| Gates A–D, 13 slices | 13 pass | 13 pass | 13 pass | 13 pass | 13 pass | **13 fail at Gate C** (SHACL, 376 violations); A, B, D pass |
| corpus ELK (13 slices + ext + catalog + capability layer + CCO) | consistent, 0 unsat | same | same | same | same | same |
| Gate F (RefIntegrity, FR-18 baseline) | at baseline (39/0/0/0) | same | same | same | same | **fails: capability-as-process 30, expected 39** |
| C1–C7 (`validate_caps.py`) | 0 violations | 0 | 0 | **0** | 0 | 0 |
| matchability | 62 routable, 391 gaps over 453 processes | same | same | same | same | same |
| consistency audit, co-parent issues | 11 | 11 | 11 | 11 | 11 | **146** |

**Reading:**

- **B3, B5, B6 and B12 are safe to back-port.** Every BPO gate holds, and **B6 does not
  disturb C5–C7**. Those shapes target the objects of the `requires*` triples with SPARQL
  over `rdfs:subClassOf*`, which does not depend on the property's OWL type.
- **B13 cannot be back-ported as it stands.** The 216 parents are what BPO's offline Gate C
  and its consistency audit check for. Removing them breaks Gate C in every slice, while
  ELK is unaffected.
- **B13 also exposes a weakness in BPO's Gate F.** Its capability-as-process rule reads only
  *directly asserted* Organization Capability (568) parents. For 9 of the 39, 568 was the
  redundant co-parent, so without it Gate F reports them as resolved, though all 9 are still
  entailed under 568. The template's scheme rule, which follows `rdfs:subClassOf`
  transitively, still finds all 39 (measured on the B13 candidate). A change with no effect
  on entailment can thus move a check that reads asserted axioms only.
- BPO's CLAUDE.md quotes matchability as 60 routable and 385 gaps over 445; at `685f1f2` it
  is 62 / 391 / 453.

Trial harness notes: the scratch worktree's shell scripts were converted to LF (a Windows
checkout gives them CRLF, which bash refuses), and `corpus_check.sh` was run with Git for
Windows' bash, since a bare `bash` can resolve to WSL's. The corpus results are in
`trials/<candidate>.corpus.tsv`; the first run of that gate, in the full trial files, failed
for these harness reasons alone.

## 4. The record

Columns, as the memo asks: **original** (S0, i.e. BPO `bc64e91`), **result** (S1, or the
candidate), **nature** of the difference, **mechanism** (what caused it, what detected it),
**evidence**, **proposed disposition**, **rationale**.

"Nature" uses five values:

- **none**;
- **annotation:** text only, with no OWL meaning;
- **asserted:** asserted axioms change and the entailed hierarchy does not;
- **entailed:** the entailed hierarchy changes;
- **semantic:** the intended meaning changes, whether or not OWL sees it.

A difference can be more than one of these.

### B1. The same term reads differently in different modules (drift)

| | |
|---|---|
| Original | 110 term/property pairs, 266 variants: 51 definitions and 6 labels (57 wellformedness violations, K09/K10), and 53 comments (K08) |
| Result | S1: unchanged; it is still the same text |
| Nature | annotation, and for some terms semantic (below) |
| Mechanism (cause) | **BPO's authoring process.** 213 of the 266 variants date from 2026-06-02, when each slice was written separately; independent per-slice agents minted the same readable IRIs (BPO `ff28025` says so). `ff28025` then harmonized the clashing *parents* (Budget/BusinessStrategy → 965, PerformanceMeasure → 853, Supplier → 1180) but never the *texts*. 26 variants exist only after v0.4.1's prefix rename (`dda9fa5`), but no drift was *created* by it: no two variants differ only by `ex:`/`bpo:` |
| Mechanism (detection) | **The template.** Its wellformedness shapes (one definition and one label per language) and v0.1.0's annotation profile (comments). BPO validates each slice alone, so its architecture cannot see cross-slice drift; the template's merged-corpus validation can |
| Evidence | `b1-origins.tsv` (each variant's introducing commit); `b1-terms.tsv` (each pair's kind and proposed resolution) |

**What the drift is**, from reading every definition and label:

| Kind | Definitions | Labels | What it means | Proposed resolution |
|---|---:|---:|---|---|
| wording | 10 | 1 | same meaning, different words | one canonical text; no semantic or OWL change |
| narrowed | 34 | 4 | one shared kind, each slice defining it in its own context (Customer has 7 variants) | one general definition; slice scope to comments, or a subclass where a slice needs the narrower kind (per term) |
| homonym | 2 | 1 | two different kinds under one IRI: **PerformanceMeasure** (a Directive measure *specification* in s3, a Descriptive measured value in s9), **CustomerProfile** (a customer segment in s1, one customer's record in s6) | split: one new IRI, the slice that means the other kind re-pointed. Changes asserted axioms |
| genus | 2 | — | a variant's genus disagrees with the asserted parent: **Supplier** (s5, s6, s9 "An Agent" against parent Organization 1180, and Organization ⊄ Agent in CCO 2.0); **RawMaterial** (s2 "Material Entity", less specific than the asserted Portion of Material 457; not contradictory). PerformanceMeasure's s3 variant is also a genus contradiction | correct the text to the parent, BPO's own rule |
| registry-copy | 2 | — | a slice's inlined copy of a registry genus differs from `apqc-ext.ttl`, D9's single source of truth: ActOfForecasting (s10), ActOfReporting (s13) | the registry text, after checking whether the slice's wording should flow back |
| synonym classes | 1 | — | **SeniorManagement**'s two definitions name two different role classes, SeniorManagerRole (s1) and SeniorManagementRole (s2): two IRIs for what reads as one role | merge, or state the difference. Merging changes asserted axioms |

The 53 comments: 34 are per-slice notes on a shared term's local use, 6 are registry copies,
3 are properties re-declared with their own note in each slice, **7 are deliberate review
addenda** (a second comment in the *same* slice, e.g. LetterOfCredit's "FALSE-FRIEND note"),
and **3 were created by the port**, which merged three BPO files into one module.

| | |
|---|---|
| Proposed disposition | Resolve the 57 definition/label findings in BPO, term by term, from `b1-terms.tsv`: wording and narrowed → one text; genus → correct the text; registry-copy → the registry; homonym and synonym → a modelling decision each (3 terms). For comments: keep per-slice notes where they say something module-specific, and resolve the 6 registry copies. The 7 addenda are not drift (see §5) |
| Rationale | One IRI has one meaning; a reader of one slice must not get a different class from a reader of another. The memo's distinction holds here. Wording and narrowing (44 of 57) change no meaning that OWL sees, and resolving them changes none. The 3 homonym/synonym terms change meaning *and* asserted axioms, so they need entailment evidence when resolved. The 4 genus terms change meaning, not OWL |

### B2. APQC text redistributed without APQC's notice

| | |
|---|---|
| Original | 3,757 `apqcSourceText` literals (1,836 classes), under MIT, with no APQC notice |
| Result | **Closed in BPO** (`2e55edd`, ADR-003 at `b3b7ff3`). Port `main` carries NOTICE.md and the site-footer notice (`7674579`); the ontology carries `dcterms:rights` from S2 on |
| Nature | none (licensing metadata) |
| Mechanism | Detected by the BPO evaluation (manual). The template's licensing check passed it: per-file licences cannot see quoted text (T9). v0.1.0 detects only *declared* third-party text. The site footer cannot carry a third-party attribution (P-A8) |
| Proposed disposition | Closed (architect's decision, ADR-003). S2: port tool carries `dct:rights`; declare `apqcSourceText`, `pcfID`, `hierarchyID` in `config/third-party-text.yaml` with BPO's values |
| Rationale | BPO's answer, `BPO-BPOT-2026-10-30-phase-b-licensing-answer` |

### B3. The PCF release named on every module with APQC text

| | |
|---|---|
| Original | BPO names release 7.4 only on the catalog; 13 of 15 modules have a `dct:source`; slices 5 and 6 have none |
| Result | S1: `dcterms:source "APQC Process Classification Framework (Cross-Industry) v7.4"` on all 14 port modules with APQC text |
| Nature | annotation (header metadata); no entailment |
| Mechanism | **Detected by the port team's own provenance test** (`tests/project/`), written during the port; not by a template check. v0.1.0's T23 check reads it only for declared third-party text. Changed by the port tool, PO decision 2026-10-26 |
| Evidence | trial B3 (§3) |
| Proposed disposition | **Back-port** to BPO |
| Rationale | Each module carrying APQC text should name the release it came from; this does not depend on the template |

### B4. `P10530_SuggestionProgram`

| | |
|---|---|
| Original and result | One non-PCF class (BPO's compound-row de-conflation of P10530) with a PCF-style IRI and an underscore. IRI lint violation (K16), at S0 and S1 |
| Nature | none yet; a rename is an IRI change, recorded in SSSOM |
| Mechanism | Detected by the template's IRI linter; accepted by BPO's Gate F |
| Proposed disposition | Rename to a readable non-PCF IRI (e.g. `SuggestionProgramManagement`), with a replacement row. Or keep it as a recorded exception |
| Rationale | The `P<id>` form says "a PCF row", and this class is not one. BPO's D7 rule (G6) holds either way |

### B5. The ten BPO properties have no definition

| | |
|---|---|
| Original | 10 properties with `rdfs:comment`, no `skos:definition` (K14) |
| Result | S1: the PO's definitions (2026-10-26), comments kept |
| Nature | annotation, **and semantic for three of them**: the definitions decide what `requires*` (B6), `bearsPermission` (B7) and `enablesProcess` (B8) mean. `enablesProcess` is now "a necessary condition", which turns its 356 pairs into requirement claims with no OWL change |
| Mechanism | Detected by the template's site build (refuses an undefined term), then by v0.1.0's wellformedness shape |
| Evidence | trial B5 (§3) |
| Proposed disposition | **Back-port**, after B6, B7 and B8 are decided, since three of the ten texts depend on them |
| Rationale | A property without a definition cannot be reviewed. The definitions must follow the decisions, not settle them silently |

### B6. `requiresCapability`, `requiresRole`, `requiresPermission` are object properties used between classes

| | |
|---|---|
| Original | `owl:ObjectProperty`, asserted only class-to-class (563 assertions; K02). OWL 2 DL reads this as punning: the classes are also individuals, related to each other, and nothing follows for their instances. BPO chose object properties deliberately, with ranges enforced by SHACL C5–C7 rather than `rdfs:range` |
| Result | S1: `owl:AnnotationProperty` |
| Nature | asserted (property type); **no entailment change** (S0 and S1 entail the same 19,112 pairs). Semantic only in that S1 stops suggesting an OWL meaning the axioms never had |
| Mechanism | Detected by PO review during the port (2026-10-26), then automatically by v0.1.0's placement shape (K02, 563 findings at S0) |
| Evidence | trial B6 (§3); S0/S1 entailment identity |
| Options | **(a)** annotation property: honest about the semantics, no OWL meaning, SHACL still checks the targets. **(b)** keep the object property and accept punning: legal OWL 2 DL, but it says nothing about instances. **(c)** class-level restrictions, e.g. `P ⊑ ∃ has_participant.(Agent ⊓ ∃ has_capability.C)`: real OWL meaning, which ELK would reason with, and new entailments, which would need checking against CCO 2.0's `has capability` domain (Agent: see B11) |
| Proposed disposition | **(a), back-port.** The trial shows C1–C7, matchability and every BPO gate unchanged. Record (c) as the route to an OWL requirement semantics; B8 must be settled first |
| Rationale | (b) asserts something nobody means. (c) is the realist reading, but a necessity claim over 356 pairs that B8 says are not all necessities |

### B7. `bearsPermission`

| | |
|---|---|
| Original | an annotation property whose label says a role *bears* a permission. In BFO, *bears* is the relation of a bearer to its dependent continuants. CCO's Action Permission (`ont00000751`) ⊑ Process Regulation (`1324`) ⊑ `965` (labelled "Prescriptive Information Content Entity" in CCO 2.0) ⊑ ICE: a generically dependent continuant, which a role cannot bear (verified in the pinned CCO) |
| Result | S1: the definition is corrected (a policy association); the label is unchanged |
| Nature | semantic (definition); none in OWL (annotation property, no axioms use it) |
| Mechanism | Human review (the BPO evaluation); no check can find it (G4) |
| Proposed disposition | Relabel (`permissionApplicableToRole`), with a deprecation and an SSSOM row, and back-port the definition |
| Rationale | The label asserts a BFO relation that cannot hold |

### B8. `enablesProcess` is used to derive a requirement

| | |
|---|---|
| Original | 356 `enablesProcess` pairs (the evaluation's 361 was wrong). **197** come from slice axioms `Capability ⊑ ∃ realized_in.Process`; **159** from the judgment table `capabilities/capability_scope.json`. `requiresCapability` is exactly their inverse, so every pair becomes "process P requires capability C" |
| Result | S1: the pairs are unchanged, but the PO's B5 definition now says "necessary condition": the requirement reading made explicit |
| Nature | semantic, with no OWL change |
| Mechanism | Human review (evaluation); undetected by any check. **Two steps are in question.** (1) `C ⊑ ∃ realized_in.P` says every instance of C *is* realized in some P, which is strong for a realizable entity that may never be realized. (2) The inversion turns "C is realized in P" into "P needs C", a necessity the axiom does not state |
| Proposed disposition | **Audit the 356 pairs** by source. The 159 judgment-table pairs: confirm per capability that each process *needs* it. The 197 axiom-derived pairs: decide whether the derivation stands. Split "can enable" from "requires" where it does not. Decide (1) separately, as a modelling question for the slices |
| Rationale | `requiresCapability` drives dispatch. A false requirement makes a process unroutable for no reason. How many of the 385 matchability gaps (of 445) it accounts for is not yet measured |

### B9. Definitions whose genus is not the asserted parent

| | |
|---|---|
| Original | 233 findings at S0 under v0.1.0 (the evaluation counted 13 under the narrower check of `2455bcc`): **145 K03** (the parent named in the definition is a redundant co-parent), **77 K04** (the genus is more general than the asserted parent), **11 K05** (the genus is an ancestor or another class: P20799 "an act of design…" ⊑ Act of Formulation; the FNSR markers) |
| Result | S1: unchanged. The B13 candidate removes all 145 K03 (measured) |
| Nature | annotation (the definition's genus); none in OWL |
| Mechanism | Detected by the template's realist genus check. **Gap:** the check passes a class if *any* of its definitions names the parent, so a contradicting variant hides behind an agreeing one (Supplier, PerformanceMeasure: B1). New finding P-B1 |
| Proposed disposition | Resolve B13 first (145 disappear). Then the 88: align the genus with the parent (the 77 K04 include "a role that…" under Occupation Role and "a planned act…" under Act of Communication; not yet reviewed one by one), or re-parent the 11 K05 where the text is right |
| Rationale | Genus–differentia is BPO's own convention (GOLDEN PRINCIPLE): the definition and the parent must agree |

### B10. Editorial qualifiers in labels

| | |
|---|---|
| Original | 18 labels ending in a parenthetical: **9 BPO notes** (K12: "(shared anchor)", "(discernment sense)", "(capability)" ×2, "(asset)", "(product)", "(permission)", "(deployed artifact)", and "Request for Proposal (RFP/RFQ)"); **9 APQC element names** (K17, false alarm: "Process accounts payable (AP)") |
| Result | S1: unchanged |
| Nature | annotation |
| Mechanism | Detected by the template's realist label check; it cannot tell a source's own name from a note (K17) |
| Proposed disposition | Move the 9 notes to `skos:altLabel` or the comment; keep the APQC names as they are |
| Rationale | A label names the kind; a note about it belongs elsewhere. APQC's names are the source's, and stay verbatim |

### B11. Organizations where CCO requires an Agent

| | |
|---|---|
| Original and result | 5 findings (K13): `has recipient` (`ont00001922`, range Agent) restricted to BoardOfDirectors (P11042, P11043) and RegulatoryAuthority (P19596); `has capability` (`ont00001954`, domain Agent) on ServiceProvider and SupplyChainOrganization |
| Nature | none; a decision record |
| Mechanism | Detected by the template's realist domain/range check; known and documented in BPO, never tested |
| Evidence | **CCO 2.0 is inconsistent with itself here** (verified in the pinned CCO): `has capability` has domain Agent (`1017`) and range Agent Capability (`1379`); CCO's own Organization Capability (`568`) ⊑ `1379`; Organization (`1180`) ⊑ Group of Agents (`300`), not ⊑ Agent. So CCO cannot let an Organization have an Organization Capability without inferring it to be an Agent |
| Proposed disposition | Record BPO's pattern as a decision: organizations are kept as organizations, and the 5 are accepted as **upstream** (K13 is so classified). Check CCO v2.2 for a change before S2. If a fix is wanted, the alternative is to restrict to a member agent of the organization |
| Rationale | Forcing Organization ⊑ Agent would contradict CCO; restating the relation on member agents changes BPO's meaning |

### B12. The PCF concept scheme has no top concept

| | |
|---|---|
| Original | `bpot:PCF` names no top concept (K15) |
| Result | S1: the 13 category concepts as top concepts (26 triples) |
| Nature | annotation (SKOS); no OWL entailment |
| Mechanism | Detected by the template's SKOS shapes; changed by the port tool, PO decision 2026-10-25 |
| Evidence | trial B12 (§3). BPO's catalog is generated (`src/apqc_transform`), so the back-port belongs in the generator, not the file |
| Proposed disposition | **Back-port** in the catalog generator |
| Rationale | A SKOS consumer needs an entry point; the template found what BPO's checks did not |

### B13. Redundant co-asserted parents

| | |
|---|---|
| Original | 224 classes with more than one named parent. **216** have one redundant parent each (K06): an ancestor of their other parent in the pinned CCO. **8** have two parents that are both needed (K07, 16 parent axioms) |
| Result | candidate: the 216 redundant parent axioms removed |
| Nature | **asserted only**: the entailed hierarchy is unchanged (19,112 pairs; asserted 3,343 → 3,127) |
| Mechanism | Caused by BPO's architecture: each slice co-asserts an allowlisted parent so that Gate C passes offline without CCO. Detected by the template's realist shape, which validates with CCO in scope |
| Evidence | `b13-parents.tsv`: one row per asserted parent of every multi-parent class (448), with status, the path that makes it redundant, and the module. **Trial B13 (§3): in BPO, Gate C fails in all 13 slices (376 violations), the consistency audit rises from 11 to 146 issues, and Gate F falsely reports 9 capability-as-process findings as resolved. ELK, C1–C7 and matchability are unaffected** |
| The 8 (K07, "unsure") | 7 delivery-fleet roles (Approver, Architect, Developer, Evaluator, MarketAnalyst, Planner, Strategist) under the `FNSR Role` marker **and** Occupation or Authority Role. **IT Infrastructure Component** under IT Asset and Information Processing Artifact |
| Proposed disposition | **Keep the 216 in BPO** for now, and accept K06 (and the 145 K03 that follow) as a **project–template architecture difference**: BPO validates each slice offline against allowlisted anchors; the template validates the merged corpus with CCO. Removing them is a BPO architecture decision: Gate C would have to validate with the CCO closure, the consistency audit change, and Gate F follow `subClassOf` transitively. Separately, **fix Gate F's asserted-only reading** whatever is decided. For the 8: the marker is a grouping, not a genus. Proposed: drop the `FNSR Role` parent and carry fleet membership as an annotation. IT Infrastructure Component needs the architect's call |
| Rationale | The memo's distinction exactly: an asserted change with no entailed change. The question is which architecture the parents serve, not whether the ontology says something different |

### B14. No class names a definition source

| | |
|---|---|
| Original and result | 3,119 warnings (K01): CCO's definition-source annotation (`ont00001754`) is on no class |
| Nature | annotation (provenance) |
| Mechanism | Detected by the template's annotation profile (a CCO convention BPO never adopted) |
| Evidence | 1,831 classes carry `pcfID`, 1,836 carry `apqcSourceText`: BPO *has* provenance for the PCF-derived classes, in its own properties |
| Options | **(a)** add `ont00001754` mechanically: "APQC PCF 7.4, element <pcfID>" for the 1,831, and BPO's authorship for the rest. **(b)** configure the profile to accept `pcfID`. **(c)** switch the rule off by recorded decision |
| Proposed disposition | **(a)** for the PCF-derived classes, mechanically, and decide what "source" means for BPO-authored definitions |
| Rationale | The provenance exists; the template asks only that it be stated in CCO's form. Note that a definition *paraphrases* the row; the source says where to check it |

### B15. 39 capabilities with process IRIs

| | |
|---|---|
| Original and result | 39 (K11), BPO's tracked backlog (Gate F, FR-18) |
| Mechanism | Detected by BPO's Gate F; reproduced exactly by the template's scheme rule configured in Phase A (T12) |
| Proposed disposition | Not a Phase B item. Stays BPO's backlog |
| Rationale | Already tracked; the template's contribution is that it can now detect it too |

### B16. Comments cite `bpo:` CURIEs

| | |
|---|---|
| Original and result | 1,224 comments in the port cite `bpo:` terms, which are `bpot:` here |
| Mechanism | Caused by the port's namespace move (prose is not rewritten); found by manual review |
| Proposed disposition | **BPO: no change** (BPO's answer: `bpo:` is BPO's prefix). **Port:** keep as provenance, since the port is a test bed, and note it in NOTICE/README. Rewriting 1,224 comments is noise for this experiment |
| Rationale | BPO's answer makes this the port's decision |

### B17. Three local re-statements of CCO axioms

| | |
|---|---|
| Original | `371 ⊑ 228`, `402 ⊑ 228`, `626 ⊑ 853` asserted locally in BPO (the "1b bridge" blocks) |
| Result | S0 and S1: dropped by the port; each is asserted verbatim in the pinned CCO |
| Nature | asserted (statements about upstream terms); no entailment change |
| Mechanism | The port's mechanics (CCO is in scope here) |
| Proposed disposition | Keep in BPO (its offline Gate C needs them); keep dropped in the port |
| Rationale | The same architecture difference as B13 |

### B18. Header metadata not carried

| | |
|---|---|
| Original | BPO's header titles, `owl:versionInfo "0.4.1"`, and design-note comments |
| Result | S0, S1: one header per port module citing its BPO header IRI and `dct:source`; titles, version and notes not carried |
| Nature | annotation (header) |
| Mechanism | The port tool's header replacement; found by manual review |
| Proposed disposition | Carry `owl:versionInfo` (as the BPO source version) and the titles. Drop design notes that are no longer true in the port ("self-contained: … inlined") |
| Rationale | A version and title are provenance; a note that describes BPO's architecture is false in the port |

## 5. Corrections to the Phase A record found while doing this

| What | Correction |
|---|---|
| K08's reason ("inlined copies of a shared term have drifted") | True for 43 of the 53. **7 are deliberate review addenda**: two comments in one slice, BPO practice, legal RDF. **3 were created by the port**, which merged three BPO files into one module. Proposed: the 7 reclassified **false alarm** (the one-comment rule against a legitimate practice), the 3 kept **real** but owned by the port. Under A6 this is a new, dated register change with this reason, and needs the architect's approval |
| B8's count | 356 `enablesProcess` pairs, not 361 |
| B13 in the memo ("145 potentially redundant parents") | 216 redundant parent axioms on 216 classes. The 145 are K03 genus findings that follow from them. The 8 uncertain are K07 |
| `965`'s label | CCO 2.0 labels it "Prescriptive Information Content Entity". BPO's docs and this record's earlier text say "Directive"; the IRI is the same |

## 6. Detection: what the framework found, and what it did not

| Found by | Items |
|---|---|
| template checks, automatically | B1 (definitions, labels, comments), B5, B6 (v0.1.0), B9, B10, B11, B12, B13, B14, B4 (IRI lint), B15 (once configured) |
| the port team's own tests | B3 |
| human review | B2, B6 (first), B7, B8, B16, B17, B18 |
| **nothing** | B8's inversion and its `realized_in` premise; **homonyms** and **synonym classes** (the check reports drift, not that two kinds share an IRI or one kind has two); **genus contradictions hidden behind an agreeing definition** (P-B1); B7's misuse of *bears* |

A weakness in **BPO's own** checks, found by the experiment: Gate F's capability-as-process
rule reads asserted parents only, so an entailment-neutral change (B13) moved its count from
39 to 30 (§3).

New template finding: **P-B1.** The genus check evaluates "some definition names the
parent", so it passes a class whose other definition contradicts it.

## 7. Decisions needed from the BPO architect

1. **The design:** adopt S2u, and propose A9 to the Template Team.
2. **Gate F:** follow `rdfs:subClassOf` transitively in its capability-as-process rule (B13 trial). This is a BPO fix found by the experiment, independent of B13's outcome.
3. **B1:** approve the per-term resolutions in `b1-terms.tsv`. Decide the 3 homonym/synonym
   terms (PerformanceMeasure, CustomerProfile, SeniorManagement), and the comment policy.
4. **Back-ports B3, B5, B6, B12:** adopt or not, on the trial evidence. B5 after B6, B7, B8.
5. **B6:** option (a), (b) or (c).
6. **B7:** the relabel.
7. **B8:** the audit, and whether the `realized_in` derivation stands.
8. **B9, B10, B14:** approve the proposed handling.
9. **B11:** record the pattern as a decision.
10. **B13:** remove or keep the 216 (trial), and decide the 8.
11. **B4, B16, B18:** as proposed, or otherwise.
12. **§5:** approve the K08 reclassification of 7 (and the reason correction for 3).

Once these are decided and made in BPO, the S2 commit can be named. S2u and S2 are then
ported and measured with the same instrument, and the quality review follows separately.