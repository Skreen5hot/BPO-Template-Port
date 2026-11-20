---
id: BPOT-EXAMPLE-2026-11-20-template-test-assumes-gitattributes
from: BPOT
to: EXAMPLE
date: 2026-11-20
type: finding
subject: "test_against_names_what_both_sides_changed fails in a project that has changed .gitattributes, as communications protocol 1.1 asks"
in_reply_to: null
refs:
  - repo: Skreen5hot/Ontology-Template
    commit: cb4d874a0c6bb022b076ec7f714b4ae04d01db62
    path: tests/test_template.py
    sha256: ac08843769046972bb7ed4fcc40f80dd9c487ff295280bf4fe6a74721ec8a19b
  - repo: Skreen5hot/BPO-Template-Port
    commit: 6b25a6d165fd551e47ba3e214135943b65ff714a
    path: .gitattributes
    sha256: 11dfc733b50a14bb1705acb8176c33f7c7e9180adb8e19290ddcc5d919cd74f2
author: Claude (agent), drafted at the direction of Aaron Damiano, the BPO architect and PO, under the architect's standing approval to send messages
requires_act: false
---

A small template defect, found while merging the port's WP6 branch into its `main`. It
needs nothing from you beyond a fix when you next touch the test.

## The defect

`test_against_names_what_both_sides_changed` (first reference, line 211) builds its
fixture from the template's manifest:

```python
names = sorted(record["files"])
both, theirs_only = names[0], names[1]
```

It then assumes the project has not changed `theirs_only`, which is the second
template-owned file in sort order. In the template that file is `.gitattributes`. A
project that adds `communications/** -text` to `.gitattributes`, as communications
protocol 1.1 Rule 7 asks of every record, has changed it. The update report then rightly
names both files under `both`, and the test's assertion `report["both"] == [both]` fails.

## In the port

The port added that line when it adopted protocol 1.1 (second reference). The test is the
only failure in the port's Checks suite on its `main` after the WP6 merge. We have not
edited it, because it is template-owned.

## A suggestion

Choose `both` and `theirs_only` from files the project has not changed. For example,
filter `names` against `status.measure()` before picking them, and skip if fewer than two
remain. The test then holds in any project, which is where template-owned tests run.

Nothing is expected of you beyond the fix.
