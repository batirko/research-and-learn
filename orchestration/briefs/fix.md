# Brief: fix worker, {scope}

## Goal

Apply the findings in {`reviews/...`} to {these topics}: {IDs and folders}.

The fix is done when every finding is applied, or settled with a reason in your handoff. The format check and the lint give 0 errors on every topic you touched, and each stays inside its size band.

## What to apply

{All the findings in the file, or a list. Name any finding the orchestrator settled differently, and what's not yours: a re-rank, a change to the map, a decision for the owner.}

{A topic near the ceiling of its band: name it. Every edit to it is word-neutral, so cut before you add.}

## Fixed

- Every quote you change matches its source, with the speaker's own hedges.
- Private stays private. A block's title and a visual's title are public text.
- A finding that needs a new source: open it yourself, and cite it.
- Run the `no-ai-slop` skill on every paragraph you rewrite.
- Add a short note to each touched topic's dossier: "Fix after {the check}".

## Model and budget

You run on {the strongest model}. Your budget is about {tokens} tokens.

## Read before you start

1. `AGENTS.md`
2. The run picture: `{orchestration/briefs/run-NN/picture.md}`.
3. `orchestration/worker-pack.md`
4. The findings, and the handoff of the worker that wrote them.
5. Each topic, and its dossier.

## What you own

- The topic folders above, and their dossiers in `research/`.
- `orchestration/handoffs/{date}-fix-{scope}.md`.

Write nowhere else. Don't run git or the build. Run the format check and the lint on the topics you touched.

## Hand back

The handoff. Finish with a short summary for someone who wasn't watching:

- the findings applied, per topic;
- any you settled differently, and why;
- the words in each topic after the fix;
- the tokens you think you used.
