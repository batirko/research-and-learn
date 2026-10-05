<!-- Example. A filled topic brief for the engine's test guide, a first season keeping bees, in engine/tests/fixture/. It points at the run picture in example-run-picture.md for what the run shares. Its run, dates and source details are invented. Copy the shape, and write your own content. -->

# Brief: topic worker, P02

## Goal

Research and write one topic of the guide:

- **P02 Swarm control.** Practical, high, M, cluster C2. Read P01 first.

The topic is done when it meets "Done means" in `docs/standards/topic-page.md`, and the format check and the lint give 0 errors.

## Why this topic

A swarm in the first season halves the colony and its honey. Sam needs to know the signs that come before a swarm, and what a queen cell means at each stage. Sam also needs a method that suits a beekeeper with two hives. P01, live, teaches how to inspect. P02 says what a spring inspection looks for, and what to do when the signs show.

## The reader

Sam starts a first season with two hives at the association's teaching apiary in spring. Write for someone who has heard of beekeeping and hasn't kept bees. `context/reader.md` says more.

## Model and budget

You run on the strongest model. Your budget is about 250,000 tokens. This build runs in the lean mode, so you can't start subagents. Research alone.

Before you start, fetch one page you need. If the fetch fails, stop and say so in your handoff. A topic written without the web is written from memory.

## Read before you start

1. `AGENTS.md`
2. The run picture: `orchestration/briefs/run-02/picture.md`. It's part of this brief.
3. `orchestration/worker-pack.md`. Open a standard only where the pack points you to it.
4. `engine/format.md`, in full.
5. `context/glossary.md`, and the titles in `context/open-questions.md`. OQ-01, whether the colonies came with marked queens, touches this topic: a marked queen takes less time to find when the signs show.
6. `context/association.md`. Search the handbook in `context/sources/` for swarms. The mentor call is private: search it for "swarm" and "queen cell", and don't read it whole.
7. P02's entry in `curriculum/topic-map.md`, and the homes table there.
8. P01, `content/practical/p01-inspecting-a-hive/`. It's the closest live topic, so copy its form.

## Fixed

- The standards, the glossary and the format.
- You open every source you cite. A link from memory or a search snippet doesn't count.
- Every fact about Sam's apiary or the association carries a provenance tag. A guess about the case is a defect. An unknown is written as unknown, with its open question's ID.
- What the mentor said sits in a private block, with its hedges. A block's title and a visual's title are public text. Search your public text for the mentor's advice restated in other words.
- P02 is the home of swarm control. B01 holds the brood clock, and B02 holds the season. Link to both, and don't explain them again.
- Size M: aim near 950 words. No XL.
- At most five materials. At most one critical material: it uses C2's whole quota.
- The worker pack's known errors: the handbook gives a queen's development time as 15 days on one page and 16 on another. B01 settled on 16, with its source. Use B01's figure and link to it.
- The handbook says the association's early swarms last year came from a warm spring. The mentor puts them down to crowded boxes. Weigh both explanations, and don't pick one before the evidence does.

## Yours to decide

- How you research, and which sources you choose. The map lists no seeds for P02.
- The questions. The map asks what signs come before a swarm, and which method suits a beekeeper with two hives. Answer them, or replace one and say why in your handoff.
- How the explanation is built, and the ranks of its sections and materials.
- Whether a visual passes the test in `docs/standards/visuals.md`. The map guesses "maybe": the days between sealed queen cells and a swarm.

If the map is wrong about P02, say so in your handoff: its scope, its rank, or whether it's one topic or two. If what you find contradicts the context notes, the evidence wins. Say so in your handoff too.

## What you own

- `research/p02-swarm-control.md`
- `content/practical/p02-swarm-control/`
- `orchestration/handoffs/2026-10-06-topic-p02.md`

Write nowhere else. Don't run git or the build. Run the format check and the lint on your own files.

## Hand back

The topic, the dossier and the handoff. `orchestration/handoffs/README.md` lists what a handoff holds.

Finish with a short summary for someone who wasn't watching:

- what now exists;
- what you couldn't verify;
- what you need decided;
- the tokens you think you used.
