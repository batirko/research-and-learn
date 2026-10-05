---
name: scaffold
description: Researches the case and proposes the guide's topic map, after the set-up interview. Use when docs/request.md is filled but curriculum/topic-map.md still says it's a template, or when the owner asks to "scaffold the guide", "propose the topics" or "plan the guide". Writes the context notes, the open questions, a first glossary, the topic map and the board, then puts the kickoff questions to the owner.
---

# Scaffold

You research the case, write what is known and unknown about it, and propose a topic map that fits the owner's hours. You don't write topics. The session that runs the scaffold usually goes on as the orchestrator, so `orchestration/playbook.md` is worth reading now.

## What you produce

- **Case notes** in `context/`: what is known about the case, with evidence kept apart from interpretation. A guide with no case has none.
- `context/open-questions.md`, `context/glossary.md` and the research's additions to `context/reader.md`.
- `curriculum/topic-map.md`: the proposed map.
- `orchestration/board.md`: one row per topic, and the cost projection.
- Changes to `guide.toml` and new assumptions in `docs/request.md`, where the sizing needs them.
- The kickoff questions, put to the owner.

Fill each file as its own instructions say. This skill says what goes in, and the file says its shape.

## Before you start

1. If `docs/request.md` still says it's a template, run the set-up skill first.
2. Read `docs/request.md`, `context/reader.md`, `guide.toml`, `docs/method.md` and `context/README.md`.
3. Read `engine/format.md`, "The topic map": the parts of the map the build reads. Read the playbook's "Kickoff" section.
4. Fetch one public page about the subject. If the fetch fails, stop and tell the owner. Without the web, the scaffold writes from memory.

## Fixed

- **Sources are frozen.** Nobody edits a file in `context/sources/`. To keep what a public page says today, save it there as a new dated file, and add its row to the list in `context/sources/README.md`.
- **You open every source you cite.** A link from memory or a search snippet doesn't count.
- **Every fact about the case carries a provenance tag.** The tags are in `context/README.md`.
- **Evidence and interpretation stay apart.** Your reading of the case is a first reading, made before anyone knew the case well. It goes under its own heading.
- **Don't guess about the case.** An unknown becomes an open question.
- **When the people who own the case give several explanations for one thing,** record all of them, and pick none.
- **Nothing on the never-publish list goes into a note.** A source can hold something that must never publish. Add a term for it to `context/never-publish.md`, as that file says.

## Research the case

- Read every source in `context/sources/` once, in full. You're the first reader. Later workers search the sources instead.
- Then read the public pages about the case: its organisations, places, rules and dates.
- Write one case note per question about the case, as `context/README.md` says: its name, its shape, and a row in that file's table.
- Write what each person in the case does and expects, with tags. Leave out personal details the reader doesn't need.
- Add to `context/reader.md` what the research finds the case will ask of the reader, with tags.

You can start a helper on a smaller model to find candidate pages. Set its model. Open what you cite yourself.

## Research the subject

Research the subject as far as the map needs, and leave the depth to the topic workers. Find what the goal needs:

- what people learn first;
- the standard texts and courses;
- the practices, and how people tell they worked;
- what today's tools change;
- where practitioners disagree.

The sources you find become seeds in the map. A seed is a lead nobody has verified yet.

## Open questions and the glossary

- **An open question** is an unknown about the case, with an ID such as OQ-03. Give each one its likely answers, what would settle it, and who can. Write them as `context/open-questions.md` says. A question about the subject in general isn't one: a topic answers it from sources.
- **The first glossary** holds one word per concept. Start with the case's own terms. Add the subject's terms where the field uses several words for one thing. Put the words each one replaces in "Don't use". Once the map names homes, give each term its home topic.

## Propose the topic map

Fill `curriculum/topic-map.md` as its instructions say. When it's filled, change its status line from "template, not filled yet" to "proposed by the scaffold on" and today's date, as its instructions say.

### The topics

- Start from the goal in `docs/request.md`. Each topic earns its place by an ability the goal names, and its "Why" says which, with evidence. Evidence about the case comes first.
- Place each topic in a tier by the owner's definitions.
- Rank it. A critical topic is one the reader can't reach the goal without. We recommend that critical topics stay near a third of the guide.
- Size it S, M or L by how much it has to explain. Propose no XL: the orchestrator grants an XL in a brief. A topic too big for XL is two topics.
- Give it starting questions, written before research, and seeds.
- Guess whether a visual would pass `docs/standards/visuals.md`, and name its job. The topic worker decides.
- A topic in a tier with `updates = true` names the topics it updates. A topic in a tier with `fast = true` carries the marker for facts that age fast.

### Size the map to the hours

1. Take the reading hours from `docs/request.md`.
2. **Text time:** each topic at the middle of its band, divided by `sizes.words_per_minute` (220). With the default bands, that's about 5 minutes for S, 9 for M and 14 for L.
3. **Material time, at the limits:**
   - The critical materials: `materials.critical_in_guide` (30) for the guide. Until writers pick them, assume a length for each, and list it as an assumption.
   - The other materials: the rest of `materials.per_topic` (5) in each topic. Count half of them as high and half as medium, at the minutes `[ranks]` gives each (15 and 5). Leave context ones out. List the split as an assumption too.
4. **Fit:** we recommend that text and materials together fill no more than about two thirds of the reading hours. The reader also rereads, takes notes and works through the open questions.
5. **When it doesn't fit,** lower `materials.per_topic`, then `materials.critical_in_guide`. Then cut or shrink medium topics, then high ones. Don't cut a critical topic to fit. Tell the owner instead.
6. **The first wave must fit early.** The reader reads the critical topics, and the high topics they depend on, while the rest is built.

Write every changed setting to `guide.toml`, and add each one to the assumptions in `docs/request.md`. Put the sums in the map, next to its shape table.

### Clusters and quotas

A **cluster** is a few topics that one worker can research together, because they share sources. Its **quota** is the number of critical materials its topics can propose.

- The quotas add up to `materials.critical_in_guide`.
- A quota can't pass what its topics allow: `materials.critical_per_critical_topic` (2) for each critical topic, and `materials.critical_per_topic` (1) for each other topic.
- When the caps can't reach the total, lower `materials.critical_in_guide`, and list the change as an assumption.
- Give the larger quotas to the clusters where the reader will work from an original.

### One home per shared concept

When several topics touch a concept, name the one that explains it in full: the concept's home. The others link to it, and add only what's theirs. Workers can't see each other's drafts, so the map's homes are what keep two topics from explaining one concept twice.

### The reading order

Number the steps, critical topics first, each after the topics it needs. The first wave is the critical topics, plus the high topics they depend on.

### The pilot

Recommend one topic per tier, and give each the `pilot` marker. Between them, the pilot topics test what would cost most to get wrong across the whole guide:

- the topic that rests most on the case, to test provenance, private blocks and the case part;
- a critical topic that reaches depth 3, to test depth and length;
- a topic in a tier whose facts age fast, to test dates;
- a topic with a likely visual, to test the visual standard.

Say in the map what each pilot topic tests. Pilot topics are written before their prerequisites exist, so each must stand alone.

## Fill the board and the settings

- `orchestration/board.md`: one row per topic in "Topics", every status `planned`, pilot topics marked in Notes. Fill the projection under "Cost", as the playbook's "Kickoff" section works it out.
- `guide.toml`: add the case's names to `case.terms`, the names topics will capitalise to `lint.proper_nouns`, and abbreviations to `lint.abbreviations`.

## Check

Run `python3 engine/build.py`. The build gives each planned topic a page from its map entry, so the owner can browse the proposal in `site/index.html`. Fix every error in the map, the glossary and the open questions.

## End with the kickoff

Tell the owner what the guide would be, in a few lines:

- the topics, by tier and by rank;
- the hours of text, and the hours of materials at the limits, against their reading hours;
- the pilot topics, and what each tests.

Say they can open `site/index.html` to see the map as a portal.

Then put the kickoff questions, as the playbook's "Kickoff" section defines them:

1. The assumptions in `docs/request.md`. "I accept them all" is an answer.
2. The map: its shape, its titles and its reading time. The owner can change any of it now, or at the pilot review.
3. The pilot topics.
4. How the build runs: the mode, the projected tokens, and whether the session can work without permission prompts. The orchestrator commits to git at every quiet point, unless the owner says otherwise.

The orchestrator records the answers in `docs/decisions.md`. No worker starts before the owner has answered.
