# WP6 — final quality evaluation of the ontology template on BPO

2026-11-04. Written after the four-state comparison (`four-state-comparison.md`), as A9 §7
requires: first what changed and why, then whether it is better. It answers the BPO
architect's five questions of 2026-11-03. Unresolved items are recommendations, not a new
correction cycle.

**Scope of the claim.** One ontology (BPO, 3,122 classes), one template release (v0.1.0),
one port. Semantic change is neither good nor bad by default. Each judgment below cites its
evidence.

## 1. Did the template detect meaningful defects?

**Yes, most of the defects found.** Of the 18 change items B1–B18:

- **Template checks found 11**, automatically: B1, B4, B5, B6 (v0.1.0), B9, B10, B11, B12,
  B13, B14, B15.
- **The port team's own test found 1:** B3.
- **Human review found 7:** B2, B6 (first), B7, B8, B16, B17, B18. B6 was found both ways,
  so it counts in two rows.

Of the template's findings:

| Defect | Size at S0 | Why it mattered |
|---|---|---|
| One IRI, different definitions or labels depending on the module loaded (K09, K10) | 51 + 6 violations | The same term meant different things to different consumers (B1). It also exposed the PerformanceMeasure homonym and the CustomerProfile split |
| `requires*` asserted between classes as object properties (K02) | 563 violations | OWL reads both sides as individuals (punning). The "requirement" said nothing a reasoner could use (B6) |
| Definitions whose genus is not the asserted parent (K04, K05) | 88 | 20 + 7 resolved after one-by-one review (B9), incl. P20799 re-anchored and `ActOfCommunication` retired as a duplicate of CCO 402 |
| No definition source (K01) | 3,119 | B14: 1,831 APQC-derived definitions now cite APQC and BPO's authorship of the wording |
| Concept scheme without a top concept, properties without definitions | 1 + 10 | B12, B5 |

It also detected **the one regression a correction introduced**. BPO's B1 deprecation of
`SeniorManagementRole` removed its definition and parent (K20, K21). BPO's own gates passed
it, so the template caught a defect the source project's validation missed.

**False alarms are few.** 16 at S0 (K17 9, K18 7), all from the label and comment checks.

## 2. Did it support correct improvements?

**Partly. It located defects well, but the corrections were human work, and the template
cannot judge them semantically.**

- **Clean, mechanical support.** The re-typing (B6), definitions on properties (B5), top
  concepts (B12), release provenance (B3) and definition sources (B14) went from finding to
  fix with no semantic risk. They removed 574 findings at S1 and are now in BPO's source.
- **Pointing at the right place.** For B1 and B9 the template pointed at the right terms.
  Deciding what to do needed the architect's referent-level review: PerformanceMeasure was
  a homonym, split into two classes; SeniorManagement roles were the same role, merged;
  CustomerProfile was split three ways; RegulatorRole became a subclass. P-B1 records why
  a check cannot make these decisions.
- **One check pushes against a sound convention.** K03 rose by 16 and K06 by 6. Where BPO
  made a definition name its specific parent, the class still co-asserts the broader
  allowlist parent (`568`, `228`, `BFO_0000040`), which BPO's offline SHACL needs. The
  genus check then reports the broader parent as unnamed. This is the accepted
  architecture exception (B13), and the count reflects that, not new defects.
- **Unclear improvements: none.** Every change to the entailed hierarchy (50 pairs lost, 47
  gained) traces to a recorded decision (comparison §4b).

## 3. Did it reduce errors?

**Measured by the template's own checks, yes, sharply. Measured by meaning, the largest
reduction came from outside them.**

| | S0 | S1 | S2 |
|---|---:|---:|---:|
| Violations | 632 | 58 | **2** |
| Warnings | 3,691 | 3,691 | 1,827 |
| Drift variants (term/property pairs) | 266 (110) | 266 (110) | 111 (45) |

- **The two violations left** are the `SeniorManagementRole` regression.
- **The 1,827 warnings** are mostly:
  - BPO-authored definitions without a source (K01, 1,291), whose authorship recording is
    open;
  - the accepted co-parent exceptions (K03 160, K06 218).
- **The most consequential defect was B8.** 356 capability–process pairs were read as
  necessary requirements, and 197 axioms said every capability *is* realized. No template
  check found it, and it moved no entailed pair. Its correction changed dispatch from
  64 routable over 453 processes to 30 over 197; the two are not comparable as rates.
  Counting only template findings would miss the largest gain in meaning.

## 4. Did it improve traceability and reproducibility?

**Yes, and this is where the template contributed most beyond its checks.**

- **Every state is reproducible and checked.** Each is tagged with its content commit; the
  port tool rebuilds S0 and S1 byte for byte from BPO `bc64e91`. The lossless check
  accounts for every source statement:
  - S0: 49,336 = 49,336;
  - S2u: 50,664 = 50,664.

  Each `manifest.tsv` records the commits, every Python distribution, Java, ROBOT's
  sha256, and the upstream digests.
- **Findings by identity** make states comparable finding by finding (1,800 persisting,
  2,523 resolved, 29 new), not just by count.
- **Digest pinning found a defect no version check would** (E-B1). BPO declared CCO
  2024-11-06 while vendoring a later file, and CCO's development branch kept the old
  version IRI on relabelled content. BPO now checks the file's digest.
- **Provenance in the content.** APQC's notice is carried and declared (B2). Each module
  names the BPO module, version and commit it came from (B18). Retired IRIs have a
  migration record, and in BPO a migrations page.

**Two reproducibility weaknesses, found in this run:**

- **P-B2 (template): an unevaluated rung looks like a set of findings.** When the vendored
  extract lacked a newly named CCO term, v0.1.0 marked the annotation-profile rung NOT
  EVALUABLE but exited 1, as it does for findings. The first S2 measurement therefore
  reported 1,336 fewer warnings (493 findings, not 1,829), with no error (comparison §7). `vendor_upstream` did
  report the cause, as a separate check. Recommendation: a run with any rung not evaluable
  should fail distinctly, and a comparison tool should refuse states whose evaluable rungs
  differ.
- **G-B1 (port): the environment.** The port's own `.venv` predates the pins, and the suite
  fails 39 tests outside the Phase A environment. The manifests record the environment,
  but the repository does not rebuild it. Recommendation: refresh `.venv` from
  `requirements-dev.txt` and state in `docs/DEVELOPMENT.md` that measurements use it.

## 5. What did it miss?

| Defect | Found by | What a template could do |
|---|---|---|
| **B8**: relations whose names or definitions claim more than their axioms (`enablesProcess` read as necessity; "is realized in" definitions) | human review | Third detection requirement (A9 message). Flag candidates such as a relation inverted by generation, or modal language in definitions. A person decides |
| **`ITServiceSolution`**: a material artifact defined to include software | human (referent review) | none mechanical; needs referent review |
| **P12721**: a parent (Cargo Transportation) narrower than the class | human (CCO-pin evidence work) | candidate: definition differentia wider than the parent's definition. Hard |
| **PerformanceMeasure homonym, SeniorManagement duplicate** | template's drift check pointed at them; the decisions were human | first and second detection requirements; P-B1 |
| **APQC text without its notice (B2)** | human (BPO evaluation, T9) | v0.1.0 checks declared third-party text only. Now declared here and holding |
| **Genus check passes a class whose other definition contradicts its parent (P-B1)** | human | fix in the template after WP6 (accepted, decision 23) |

## 6. Verdict

The template is **effective as a detector and as a reproducibility frame, and not a
substitute for referent-level review**.

- **Detection.** It found most of BPO's defects by count and most of the structural ones by
  kind. It caught the one regression Phase B introduced.
- **Reproducibility.** It made every state rebuildable and comparable.
- **Misses.** It missed the defects that matter most for meaning: over-claiming relations,
  misclassified referents and homonyms. All of them needed the architect's judgment, which
  A9's design kept separate and visible.
- **No effect on the corrected source (S2u → S2).** The template's process effect reached
  BPO through four back-ports and through BPO's corrections of what it detected.

## 7. Recommendations (for the next cycle; none blocks this result)

**BPO**

1. Restore `SeniorManagementRole`'s definition and its `BFO_0000023` parent beside
   `owl:deprecated` (K20/K21). It is the only regression.
2. Decide how BPO-authored definitions record their authorship (K01, 1,291).
3. Assess the 37-class capability-as-process backlog, with its 111 realized-in
   restrictions and 20 definitions.
4. Take the R5/R6 act-versus-capability methodology question as its own ADR.
5. Decide whether the co-asserted allowlist parents (K03/K06) stay, or BPO's SHACL merges
   the CCO closure instead.

**Template**

6. P-B2: a rung that is not evaluable fails distinctly, and is not counted as findings.
7. P-B1 (accepted): evaluate each definition alone, and the parent's label in genus
   position.
8. The three detection requirements: possible homonyms, duplicate classes, over-claiming
   relations. Candidates for a person, not automatic verdicts.
9. The deprecation policy as a check: a deprecated class keeps its definition and parent.
   v0.1.0 found the regression through the general definition and placement rules; a
   specific check would name the cause.

**Port**

10. G-B1: rebuild `.venv` from the pins.
11. `wp6_measure.py`: refuse a state on which any rung is not evaluable.
