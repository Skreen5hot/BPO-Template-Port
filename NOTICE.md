# Notice: APQC Process Classification Framework® content

This repository is a port of the Business Process Ontology (BPO,
`Skreen5hot/BusinessProcessOntology`) onto an ontology template, run as a test of that
template. Like BPO, it contains two kinds of material, under different terms.

| Material | Terms |
|---|---|
| This repository's own work: the port tooling, the template's code, tests and documentation, the research records, and BPO's own ontology design and BFO/CCO modelling as ported | MIT, see [`LICENSE`](LICENSE) |
| Material derived from the **APQC Process Classification Framework® (PCF), Cross-Industry, version 7.4**: element IDs, hierarchy IDs, element names and element descriptions | APQC's licence, whose notice is reproduced below. **The MIT licence does not cover this material.** |
| The vendored BFO and CCO extracts | Their own licences, see [`vendor/NOTICE.md`](vendor/NOTICE.md) |

## Where the PCF material is

- `ontology/catalog.ttl`: every PCF element's ID, hierarchy ID, name and description.
- `ontology/sections/pcf_*.ttl`: PCF element IDs, hierarchy IDs, names (in labels) and
  descriptions (`bpot:apqcSourceText`).
- `ontology/wiring.ttl`, `mappings/bpo.sssom.tsv` and `config/annotation-drift.tsv`: PCF
  element IDs inside IRIs, and labels that are PCF element names.
- The project website, whose pages show the same terms. It carries this notice in the
  footer of every page.
- PCF element IDs also appear inside IRIs throughout (`bpot:P<id>`, `bpot:PCF_<id>`), and the
  records under `research/` and `tests/` quote terms by IRI and label.

All of it is taken from BPO, which carries the same notice (BPO's `NOTICE.md` and
`docs/adr/ADR-003-pcf-licensing-posture.md`, at `b3b7ff3`). Nothing here is fetched from
APQC. From the evaluation state S2 on, each ported module carries the notice in its
`dcterms:rights` annotation too. The states S0 and S1 were ported before BPO carried it, and
are kept as they were measured.

## APQC's notice

The notice below is copied verbatim from BPO's `NOTICE.md`, which copies it from the
Copyright and attribution sheet of the PCF 7.4 workbook. APQC's licence requires a copy of
it in every copy of the PCF and in every derivative work.

> ©2024 APQC. ALL RIGHTS RESERVED. This Process Classification Framework® (“PCF”) is the
> copyrighted intellectual property of APQC. APQC encourages the wide distribution,
> discussion, and use of the PCF for classifying and defining organizational processes.
> Accordingly, APQC hereby grants you a perpetual, worldwide, royalty-free license to use,
> copy, publish, modify, and create derivative works of the PCF, provided that all copies of
> the PCF and any derivative works contain a copy of this notice.

## Also

- **No endorsement.** Neither this port nor the Business Process Ontology is produced,
  reviewed or endorsed by APQC.
- **Trademarks.** Process Classification Framework® and PCF are APQC's marks. They are used
  here only to identify the source.
- **Redistributing.** If you copy or adapt any file listed above, keep this notice with it.
