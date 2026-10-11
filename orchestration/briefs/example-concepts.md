<!-- Example. A filled concepts brief for the engine's test guide, a first season keeping bees, in engine/tests/fixture/. Its run, dates and findings are invented. Copy the shape, and write your own content. -->

# Brief: concepts, record uses, B01, P01 and M01

## Goal

Read B01, P01 and M01 against the merged list of concepts, and record where each concept is used.

The concept map shows Sam where each idea is explained and where it comes back. Every topic page ends with the same data for that page. So a use that is only a passing mention sends Sam to a section that doesn't help.

The work is done when every topic in your scope has a verdict for every concept on the list: a use at one section with a how line, or no use.

## What counts

`docs/method.md`, "Key concepts", has the rules. In short:

- **A use** is a topic where the concept does work in the argument. A passing mention doesn't count, nor the everyday sense of a word, nor a mention only in materials, exercises or a private block.
- **The case's own nouns** count as a use only where a topic says something about them: Hillside, its teaching apiary and Sam's two hives.
- **The text is public.** The mentor's advice stays out of every how line, even restated.

Give each use the one section that uses the concept most, and one sentence on what the topic does with it. A topic never uses its own concept.

"Brood" appears in almost every paragraph of P01. Count it once, at the section that reads a frame. "Inspection" in M01 is the subject of its first section, so it's a use; in B01 it's only mentioned.

## Model and budget

You run on Opus. Your budget is about 60,000 tokens.

## Read before you start

1. `AGENTS.md`
2. The run picture: `orchestration/briefs/run-06/picture.md`.
3. `docs/method.md`, "Key concepts", and `engine/format.md`, "The concept file".
4. `context/glossary.md` and the topic map's home table in `curriculum/topic-map.md`.
5. The merged list, `research/concepts-merged.md`.
6. B01, P01 and M01.

## Fixed

- Find each section's anchor in a build of your own: `python3 engine/build.py --out /tmp/concepts-run-06`. Don't build into `site/`.
- Don't edit the topics, the glossary or `content/concepts.json`. Propose changes to them in your handoff.
- Don't run git.

## What you own

- `research/concept-uses-run-06.md`
- `orchestration/handoffs/2026-10-14-concepts-run-06.md`

## Hand back

The research file and the handoff. Finish with a short summary for someone who wasn't watching:

- the uses per topic, and the ones you judged too weak to count;
- any concept whose home looks wrong, or that two topics both explain;
- the tokens you think you used.
