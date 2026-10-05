<!-- Example. A filled review brief for the engine's test guide, a first season keeping bees, in engine/tests/fixture/. It reviews one pilot topic, in run 1. Its dates and details are invented. Copy the shape, and write your own content. -->

# Brief: review worker, P01

## Goal

Review one finished pilot topic, independently:

- **P01 Inspecting a hive:** `content/practical/p01-inspecting-a-hive/`

You didn't write it. That's the point. Read it as Sam will, then test it against the standards.

This is a pilot review. Sam reads the pilot to set the depth, the length and the visuals for every later topic. So say where a standard itself looks wrong, as well as where the topic misses one.

The review is done when the review file has a verdict and its findings, ranked most serious first.

## Model and budget

You run on Opus. Your budget is about 150,000 tokens. This build runs in the lean mode, so you can't start subagents. Open links yourself.

Before you start, fetch one page P01 cites. If the fetch fails, stop and say so in your handoff.

## Read before you start

1. `AGENTS.md`
2. The run picture: `orchestration/briefs/run-01/picture.md`.
3. `orchestration/worker-pack.md`, then the standards in `docs/standards/` where a check needs them.
4. `engine/format.md`, as far as you need it to read the markup.
5. P01's entry in `curriculum/topic-map.md`.
6. `context/README.md`, `context/glossary.md` and `context/association.md`.

Read the topic before you read its dossier. Your first impression as a reader is evidence. The dossier would anchor you on the writer's reasoning.

## What a review covers

- **As a reader:** can someone who has never opened a hive follow it? Where did you get lost, skim or want more?
- **Against the map:** does it answer the map's three starting questions, or say why it replaced one?
- **Against the topic standard:** the parts, the section ranks, depth level 3 on the critical sections, and the size.
- **Facts about the case:** P01 cites the association's handbook and the mentor call. Check every tagged claim, not a sample. Search the sources for each cited line instead of reading them whole.
- **Private facts in other words:** the mentor call is private. Search the public text, the block titles and the visual titles for what the mentor said.
- **Sources:** open a sample of links. Does each say what the topic claims?
- **The exercise:** P01's "Try it" material sends Sam to a frame. Check that it asks for nothing a first-season beekeeper wouldn't have, and that its rank says what doing it pays.
- **Writing:** `docs/standards/writing.md`, the glossary, and the patterns the `no-ai-slop` skill names.

How you go about it is your call.

## The review file

**Write it as you go.** Create it early with the verdict "in progress". Add each finding when you have it, so a stop loses nothing.

- A verdict: ready, ready after small fixes, or needs rework.
- Findings, most serious first. Each says where, what's wrong, and what would fix it.
- What you checked and what you didn't, so nobody assumes a check that never ran.

## What you own

- `reviews/p01-inspecting-a-hive.md`
- `orchestration/handoffs/2026-10-05-review-p01.md`

Don't edit the topic. A fix worker applies your findings. Don't run git or the build.

## Hand back

The review file and the handoff. Finish with a short summary for someone who wasn't watching:

- whether P01 is ready;
- the one or two findings that matter most;
- what you'd change in a standard;
- the tokens you think you used.
