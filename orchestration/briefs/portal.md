# Brief: portal worker, {scope}

## Goal

{The change, in the owner's words where they gave them, and what the portal does after it.}

The work is done when three things hold. A build into your own folder passes all eight checks. The change works from disk with the network off. It holds in both themes, at phone width and in print.

## Why

{What the owner said at the pilot or while reading, and what it lets them do.}

## Model and budget

You run on {the strongest model}. Your budget is about {tokens} tokens. Set the model on any subagent you start.

## Read before you start

1. `AGENTS.md`
2. The run picture: `{orchestration/briefs/run-NN/picture.md}`.
3. `docs/standards/portal.md`: what the portal must do.
4. `engine/format.md`: the topic file format, a contract with every topic.
5. `guide.toml`, and the engine's code under `engine/`.
6. {The pilot topics, or the pages the change touches.}

## Fixed

- The portal opens from disk and works with the network off. Nothing loads from the network.
- Python 3.11 or later, standard library only. Plain JavaScript, with no libraries.
- A value that changes from one guide to another lives in `guide.toml`, with a comment.
- The eight checks keep passing. Don't weaken a check to pass it.
- Private stays private: blocks closed, and out of search.
- Every live topic still builds. A change to the format goes through the orchestrator first.
- An upgrade replaces `engine/`. List every file you change, and why, so the change can be made again.

## Yours to decide

How the change is built, within the portal standard: structure, type and layout.

## What you own

- {The files under `engine/` the change needs.}
- `orchestration/handoffs/{date}-portal-{scope}.md`.

Don't edit `content/`. If a topic breaks the build, report it. Build with `python3 engine/build.py --out {your scratch folder}`, never into `site/`. Don't run git.

## Hand back

The changed engine and the handoff. The handoff lists the files you changed and why, how you tested the change, and any change you propose to `docs/standards/portal.md` or `engine/format.md`.

Finish with a short summary for someone who wasn't watching:

- what the portal does now;
- what you need decided;
- the tokens you think you used.
