# Communications

The record of what this repository has said to, and heard from, the teams it depends on
or that depend on it.

This record follows the communications protocol, version 1.1:
Skreen5hot/communications, PROTOCOL.md at 05068d800506bae6bbf66f6cb11d4eccc6adb312, sha256
fb3a06309eb5ecd5920a7737789df524000e5447f86c008ec16fee6203d9d74d.

That file is the protocol: what a message is, the rules, team codes, and how messages are
announced on the board (the Discussions of `Skreen5hot/communications`). It is not
repeated here. Until 2026-11-05 this record followed the template's copy of it (this
file, as the template shipped it). Every message recorded under that copy satisfies 1.1.

```text
communications/
  README.md                 this file
  <team>/README.md          who the team is and where its repository lives
  <team>/incoming/          messages received, copied verbatim with their source
  <team>/outgoing/          messages sent
```

## Teams

This repository's code is **BPOT**. It corresponds with:

- **The Ontology Template team**, code `OT`, in folder `example/`. This record already
  called it `EXAMPLE`, an alias `correspondents.yaml` lists, and keeps doing so (protocol
  § Codes).
- **BPO**, the Business Process Ontology, in folder `bpo/`.

The codes are in `correspondents` in `config/project.yaml`.

## This record's own rules

These add to the protocol and do not change it.

1. **The checker.** `python tools/communications.py` checks every message and lists the
   threads still open; `tests/test_communications.py` runs the same checks on every push.
   It is the template's v0.1.0 tool, kept unchanged while WP6 holds the template fixed
   (A7). It counts commits by path and does not follow renames, as protocol 1.1 Rule 1
   asks. That is sound only while no message moves, so none is moved until the tool
   follows renames.
2. **Decisions** (protocol Rule 4) are recorded in `docs/decisions/`, citing the message
   by id.
3. **Line endings.** `.gitattributes` keeps this folder byte for byte
   (`communications/** -text`, protocol Rule 7).
4. **Sending.** Messages are committed to `main` and pushed, then announced with the
   communications repository's `tools/alert.py` (protocol § Alerts). An agent working
   here checks for waiting messages when its session starts, from a clone of that
   repository: `python tools/inbox.py --code BPOT --record <this repository>/communications`.
5. **Adding a team.** Create `communications/<team>/README.md` naming the team and its
   repository, and add the team's code to `correspondents` in `config/project.yaml`. The
   checker refuses a message folder for a team it does not know.
