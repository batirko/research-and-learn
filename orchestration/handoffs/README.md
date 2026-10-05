# Handoffs

A handoff is the file a worker leaves when it finishes. Every worker writes one, and the orchestrator writes one at the end of each session. This folder is empty until the build starts.

## Names

`{date}-{kind}-{scope}.md`, in lowercase. The kinds are `topic`, `review`, `facts`, `fix`, `context`, `portal`, `integration`, `helper` and `orchestrator`. The scope is a topic ID, a cluster or a run.

- `2026-10-06-topic-p02.md`
- `2026-10-06-facts-run-02.md`
- `2026-10-06-orchestrator.md`

When a second handoff would take the same name, add a number: `2026-10-06-orchestrator-2.md`.

## What a worker's handoff holds

- What exists now, and what's left.
- What the worker couldn't verify.
- Starting questions it replaced, and why.
- Glossary terms it proposes, each with the topic that's its home.
- New facts about the case, with provenance tags.
- Errors it found in a source, for the worker pack.
- Changes it proposes to the topic map, the standards, the context notes or the open questions, each with its reason.
- Any conflict between documents, and which one it followed.
- Questions only the owner can answer.
- The tokens it thinks it used, and whether it reached its budget.

Leave out a heading with nothing under it. A short handoff that says what exists is better than a long one that retells the work.

## What the orchestrator's handoff holds

- Where the build stands.
- What each run measured: tokens, and tokens per topic against the projection.
- What it decided while the owner was away, with the decision log's entries.
- The questions waiting for the owner.
- What the next session does first.

## How handoffs are used

The orchestrator reads every handoff, updates the shared files and carries the questions to the owner. This folder, the board and the decision log are enough for a new orchestrator to pick up the build.

Don't change a handoff once it's written. A correction goes in a new one.
