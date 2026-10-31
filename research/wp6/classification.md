# WP6 Phase A — classification of the S0 findings

**Status: APPROVED.** The BPO architect approved every class, K01 to K17, as proposed, on
2026-10-30 (amendment A5). The "Proposed" column below is the approved classification. It is
fixed before S2 is measured (A6). Any later change is a new, dated entry here, with its reason.

The register entries in `config/findings-register.yaml` are written from this table by
`tools/wp6_register.py`: one per S1 finding, with its class's classification, reason and owner.

## How the findings are classified

There is one entry per finding: `research/wp6/measure/s0/classes.tsv` holds all 4,323, by the
findings register's identity (check, where, focus, rule, message digest, severity).
`tools/wp6_classify.py` assigns each finding to exactly one class. It refuses to finish if a
finding falls into no class or into two.

Four shapes are split into classes by a mechanical test against the pinned CCO 2.0. The test
is stated with each class below.

The classifications used:

- **real:** a defect in BPO, as BPO is written.
- **false alarm:** the check works as written, but this finding is not a defect in BPO.
- **template bug:** the check itself is wrong.
- **upstream:** the defect is in a pinned upstream (CCO), not in BPO.

S1 is classified by the same tool. **Every S1 finding is an S0 finding** (S1 adds none), so
S1 needs no classes of its own.

## The classes

| Class | Finding | S0 | S1 | Proposed | Owner | Reason | B-ref |
|---|---|---:|---:|---|---|---|---|
| K01 | Class has no definition source (annotation profile, warning) | 3,119 | 3,119 | **real** (low) | BPO architect | No BPO class cites where its definition comes from. 1,823 of these definitions paraphrase an APQC row, and a reviewer cannot check a paraphrase without its source. The profile is the project's to configure: switching the rule off would be a decision recorded as such, not a reclassification | B14 |
| K02 | A class is related to a class by an object property (realist, violation) | 563 | 0 | **real** | BPO (fixed in S1 by the PO, 2026-10-26) | `requiresCapability` and `requiresRole` are asserted between classes. OWL reads both sides as individuals and entails nothing about the classes. S1 re-types the three `requires*` properties as annotation properties | B6 |
| K03 | Definition does not name a parent, where that parent is a redundant co-parent (realist, warning) | 145 | 145 | **real** (consequence of K06) | BPO architect | The parent the shape expected is already entailed through the other asserted parent (e.g. Act of Advocacy ⊑ Planned Act, beside Social Act ⊑ Planned Act). Removing the K06 parent removes the finding. Counted separately because the register counts findings, not causes | B9, B13 |
| K04 | Definition does not name a parent, on a class with another named parent (realist, warning) | 77 | 77 | **real** (low) | BPO architect | The definition names a more general genus than the asserted parent: "a role that…" under Occupation Role, "a planned act in which…" under Act of Communication | B9 |
| K05 | Definition does not name its only parent (realist, warning) | 11 | 11 | **real** (low) | BPO architect | The genus named is an ancestor or another class: "an organization capability…" under Stakeholder Relationship Management Capability; P20799 "an act of design…" under Act of Formulation; the FNSR markers, whose definitions name no parent | B9 |
| K06 | More than one named parent, all but one redundant (realist, warning) | 216 | 216 | **real** (low) | BPO architect | Every parent but one is already an ancestor of another asserted parent in the pinned CCO. These are BPO's co-asserted allowlist parents, which keep each slice valid offline. They are redundant once CCO is in scope, as it is here | B13 |
| K07 | More than one named parent, genuinely (realist, warning) | 8 | 8 | **unsure** | BPO architect | 7 delivery-fleet roles sit under the `FNSR Role` marker and also under Occupation or Authority Role. Using a marker as a genus is the "defined class written as a primitive one" the shape warns of. The 8th, IT Infrastructure Component (IT Asset + Information Processing Artifact), may be a genuine dual nature | B13 |
| K08 | Two different comments in one language, from different modules (annotation profile, warning) | 43 | 43 | **real** | BPO architect | Inlined copies of a shared term carry different notes across modules (`config/annotation-drift.tsv`). *Amended 2026-10-31: was 53; 10 moved to K18 and K19* | B1 |
| K09 | Two different definitions in one language (wellformedness, violation) | 51 | 51 | **real** (high) | BPO architect | The same IRI reads differently depending on which module is loaded | B1 |
| K10 | Two different labels in one language (wellformedness, violation) | 6 | 6 | **real** (high) | BPO architect | As K09, for labels | B1 |
| K11 | A `P<number>` class under Organization Capability (naming: scheme rule, warning) | 39 | 39 | **real** | BPO | BPO's own tracked backlog (Gate F, FR-18 baseline 39): capabilities wearing process-type IRIs. Reproduced exactly by the configured scheme rule | B15 |
| K12 | Label ends in a parenthetical qualifier, BPO's own label (realist, warning) | 9 | 9 | **real** (low) | BPO architect | 8 are editorial notes written into names: "(shared anchor)", "(discernment sense)", "(capability)" ×2, "(asset)", "(product)", "(permission)", "(deployed artifact)". The 9th, "Request for Proposal (RFP/RFQ)", glosses an acronym; it is kept in the class rather than split by hand | B10 |
| K13 | An Organization where CCO requires an Agent: range of `has recipient` (3), domain of `has capability` (2) (realist, warning) | 5 | 5 | **upstream** (CCO `ont00001180` Organization) | BPO architect | In CCO 2.0, Organization is a Group of Agents (an Object Aggregate), not an Agent. BPO's placements are right about organizations, and CCO's signatures exclude them | B11 |
| K14 | Property has no `skos:definition` (wellformedness, violation) | 10 | 0 | **real** | BPO (fixed in S1 by the PO, 2026-10-26) | All 10 BPO properties carried a comment and no definition | B5 |
| K15 | Concept scheme has no top concept (SKOS, violation) | 1 | 0 | **real** | BPO (fixed in S1 by the PO, answered by 2026-10-25) | The PCF scheme names no top concept, so a SKOS consumer has no entry point | B12 |
| K16 | `P10530_SuggestionProgram` breaks the class naming convention (IRI lint) | 1 | 1 | **real** | BPO architect | A non-PCF class with a PCF-style IRI and an underscore. The PO kept it on 2026-10-26; it is real and not fixed | B4 |
| K17 | Label ends in a parenthetical, and the label is the PCF row's own name verbatim (realist, warning) | 9 | 9 | **false alarm** | BPO architect | e.g. "Process accounts payable (AP)". This is APQC's name for the element, reproduced as the PCF scheme gives it. The check cannot tell a source's own name from an editorial note. Test: a `P<id>` class whose label equals `PCF_<id>`'s `skos:prefLabel` | B10 |
| K18 | Two different comments in one language, both in one BPO module (annotation profile, warning) | 7 | 7 | **false alarm** | BPO architect | A second comment added in review (a caution or false-friend note) in the same slice: BPO practice and legal RDF; the one-comment rule meets a legitimate practice. *Added 2026-10-31 (A6), the BPO architect's decision* | B1 |
| K19 | Two different comments in one language, both in `bpot.ttl`, from different BPO files (annotation profile, warning) | 3 | 3 | **real** | the port (BPOT) | The port merged BPO's registry and capability files into one module, so a registry note and an inlined-copy note now sit on one term. Created by the port, not by BPO. *Added 2026-10-31 (A6), the BPO architect's decision* | B1 |
| | **Total** | **4,323** | **3,749** | | | | |

Totals for S0, as approved on 2026-10-30: **real 4,301** (145 of them consequential on K06),
**upstream 5**, **false alarm 9**, **unsure 8**, **template bug 0**.

Totals for S0 after the dated change of 2026-10-31 (below): **real 4,294**, **upstream 5**,
**false alarm 16**, **unsure 8**, **template bug 0**.

## Known defects no check finds (detection gaps)

These are recorded so the S2 verdict does not read "no finding" as "no defect".

| Gap | In | Why no check finds it | B-ref |
|---|---|---|---|
| G1 | S0: 14 of the 15 modules holding APQC text do not name the PCF release | v0.1.0 checks the source and release of third-party text only when it is declared in `config/third-party-text.yaml`. BPO has declared none: declaring it is the B2 decision, pending Legal | B3 |
| G2 | S0, S1: APQC text redistributed under MIT with no APQC notice | Same as G1. Detection only (T9), pending Legal | B2 |
| G3 | S1: three SSSOM rows say "ported unchanged" for the `requires*` properties the port re-typed | No check compares a mapping row's justification with the change made. Our defect, found while producing S0 | — |
| G4 | S0, S1: `bearsPermission` and `enablesProcess` semantics | Needs review; no tool can catch it | B7, B8 |
| G5 | S0, S1: comments cite the old `bpo:` CURIEs | Prose | B16 |
| G6 | S0, S1: BPO's second D7 rule (a non-capability class with a `pcfID` is named `P<pcfID>`) | A scheme rule cannot compare a local name with a literal. At S0 and S1 the count is 0, measured outside the instrument | B15 |

## Changes to the classification (A6: new, dated, with reasons)

### 2026-10-31 — K08 split into K08, K18 and K19

**Decided by:** the BPO architect, in the Phase B decisions of 2026-10-31 (§10 there).

**Why:** the reason given for K08, "inlined copies of a shared term have drifted", was wrong
for 10 of its 53 findings. This was found while tracing every drift variant to its BPO commit
(`research/wp6/phase-b/b1-origins.tsv`):

- **7** have both comment variants in one BPO slice. A second comment was added in review, a
  caution or false-friend note: LetterOfCredit, MaterialSafetyDataSheet, RealProperty,
  RegulatoryRequirementsStatement, BusinessResiliencyCapability, ChannelManagementCapability,
  P17497. **Now K18, false alarm.**
- **3** have both variants in `bpot.ttl`, which the port made by merging three BPO files:
  ActOfDevelopment, ActOfFormulation, ActOfVerification. **Now K19, real, owned by the port.**

**How:** `tools/wp6_classify.py` assigns them mechanically, from each term's comment modules in
the state's `config/annotation-drift.tsv`. The register is rewritten from this table by
`tools/wp6_register.py`, and only these 10 entries change.

**Effect:** S0 real 4,301 → 4,294, false alarm 9 → 16. The approved table of 2026-10-30 is
kept above, with the amendment marked in it.

### 2026-10-31 — figures corrected in the Phase B record, not in this classification

- **B13** is 216 redundant parent axioms on 216 classes (K06). The 145 K03 genus warnings
  follow from them, and the 8 K07 are separate. K03 stays **real** and is documented as an
  *accepted architecture exception*: BPO keeps the parents (decision of 2026-10-31). It is not
  counted as resolved.
- **B8** has 356 pairs, not 361.
- **`ont00000965`** is labelled "Prescriptive Information Content Entity" in CCO 2.0.
