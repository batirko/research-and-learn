# Brief: review worker, {scope}

## Goal

Review {these finished topics | the whole guide}, independently:

- **{ID} {Title}:** `content/{tier}/{id}-{slug}/`

You didn't write them. That's the point. Read each topic as the reader will, then test it against the standards.

The review is done when each topic has a review file with a verdict and its findings, ranked most serious first.

## Model and budget

You run on {the strongest model}. Your budget is about {tokens} tokens. {Lean mode: You can't start subagents, so open links yourself.}

Before you start, fetch one page a topic cites. If the fetch fails, stop and say so in your handoff.

## Read before you start

1. `AGENTS.md`
2. The run picture: `{orchestration/briefs/run-NN/picture.md}`.
3. `orchestration/worker-pack.md`, then the standards in `docs/standards/` where a check needs them.
4. `engine/format.md`, as far as you need it to read the markup.
5. Each topic's entry in `curriculum/topic-map.md`.
6. `context/README.md`, `context/glossary.md`, and the context notes these topics cite.

Read a topic before you read its dossier. Your first impression as a reader is evidence. The dossier would anchor you on the writer's reasoning.

## What a review covers

{For a review of topics, keep this list. For the whole guide at integration, replace it with the guide-wide checks in the playbook's "Integration" section.}

- **As a reader:** can someone new to the subject follow it? Where did you get lost, skim or want more?
- **Against the map:** does it answer its starting questions, or say why it replaced one?
- **Against the topic standard:** the parts, the section ranks, the depth and the size.
- **Facts about the case:** every one tagged and supported by the context notes or the sources, private ones in private blocks, nothing guessed. A reviewed topic gets no separate facts check, so check every claim, not a sample. Search a source for the cited line instead of reading it whole.
- **Private facts in other words:** search the public text, the block titles and the visual titles. No script catches a private fact restated in other words.
- **Sources:** open a sample of links yourself. Does each say what the topic claims? Open every critical material, and judge whether it earns its rank.
- **Visuals:** read the job statement, look at the visual, then read the section without it.
- **Writing:** `docs/standards/writing.md`, the glossary, and the patterns the `no-ai-slop` skill names.

How you go about it is your call.

## The review file

**Write it as you go.** Create it early with the verdict "in progress". Add each finding when you have it, so a stop loses nothing.

- A verdict: ready, ready after small fixes, or needs rework.
- Findings, most serious first. Each says where, what's wrong, and what would fix it.
- What you checked and what you didn't, so nobody assumes a check that never ran.

## What you own

- `reviews/{id}-{slug}.md` for each topic. {At integration: `reviews/integration-{date}.md`.}
- `orchestration/handoffs/{date}-review-{scope}.md`.

Don't edit the topics. A fix worker applies your findings. Don't run git or the build.

## Hand back

The review files and the handoff. Finish with a short summary for someone who wasn't watching:

- which topics are ready, and which aren't;
- the one or two findings that matter most;
- the tokens you think you used.
