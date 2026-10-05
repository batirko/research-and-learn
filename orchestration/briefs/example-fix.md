<!-- Example. A filled fix brief for the engine's test guide, a first season keeping bees, in engine/tests/fixture/. It belongs to the run in example-run-picture.md. Its findings, word counts and the open question it names are invented. Copy the shape, and write your own content. -->

# Brief: fix worker, run 2

## Goal

Apply the findings in `reviews/facts-2026-10-06-b02-p02.md` to two topics:

- B02 The beekeeping year: `content/base/b02-the-beekeeping-year/`
- P02 Swarm control: `content/practical/p02-swarm-control/`

The fix is done when every finding is applied, or settled with a reason in your handoff. The format check and the lint give 0 errors on both topics, and each stays inside its size band.

## What to apply

All seven findings, with two exceptions.

- **Finding 4 is settled differently.** It asks P02 to cite the handbook for the association's swarm collection list. The orchestrator searched the handbook, and it names no list. So P02 says the list is unknown, and cites OQ-03, which the orchestrator added: "Does the association keep a swarm collection list?"
- **Finding 6 isn't yours.** It proposes raising B02 to critical. A change of rank goes to Sam, so the orchestrator holds it.

P02 is at 1,180 words, near its ceiling of 1,200. Every edit to it is word-neutral, so cut before you add.

## Fixed

- Every quote you change matches its source, with the speaker's own hedges.
- Private stays private. A block's title and a visual's title are public text.
- A finding that needs a new source: open it yourself, and cite it.
- Run the `no-ai-slop` skill on every paragraph you rewrite.
- Add a short note to each topic's dossier: "Fix after the run 2 facts check".

## Model and budget

You run on Opus. Your budget is about 100,000 tokens.

## Read before you start

1. `AGENTS.md`
2. The run picture: `orchestration/briefs/run-02/picture.md`.
3. `orchestration/worker-pack.md`
4. `reviews/facts-2026-10-06-b02-p02.md`, and `orchestration/handoffs/2026-10-06-facts-run-02.md`.
5. Both topics, and their dossiers.

## What you own

- `content/base/b02-the-beekeeping-year/` and `research/b02-the-beekeeping-year.md`
- `content/practical/p02-swarm-control/` and `research/p02-swarm-control.md`
- `orchestration/handoffs/2026-10-06-fix-run-02.md`

Write nowhere else. Don't run git or the build. Run the format check and the lint on both topics.

## Hand back

The handoff. Finish with a short summary for someone who wasn't watching:

- the findings applied, per topic;
- any you settled differently, and why;
- the words in each topic after the fix;
- the tokens you think you used.
