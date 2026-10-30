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
