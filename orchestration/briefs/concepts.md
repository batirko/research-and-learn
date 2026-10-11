# Brief: concepts, {propose | record uses}, {scope}

## Goal

{Propose: Propose the key concepts of these topics: {IDs}.}
{Record uses: Read these topics against the merged list of concepts, and record where each concept is used: {IDs}.}

The concept map shows the reader where each idea is explained and where it comes back. Every topic page ends with the same data for that page. So a concept that misses its home, or a use that is only a passing mention, misleads the reader on every page it touches.

{Propose: The work is done when each topic has its concepts, within `limits.concepts_per_topic` ({1 to 8}), and each concept has a name, a home section, a rank and a definition.}
{Record uses: The work is done when every topic in your scope has a verdict for every concept on the list: a use at one section with a how line, or no use.}

## What counts

`docs/method.md`, "Key concepts", has the rules. In short:

- **A key concept** is an idea the reader's goal needs and that travels across the guide.
- **Its home** is the topic that explains it. Where the glossary or the topic map's home table names a home, that's the home.
- **A use** is a topic where the concept does work in the argument. A passing mention doesn't count, nor the everyday sense of a word, nor a mention only in materials, exercises or a private block.
- **The case's own nouns** count as a use only where a topic says something about them: {the case's nouns, from `case.terms` and the glossary}.
- **The text is public.** No fact about the case and nothing from a private source goes in a name, a definition or a how line.

{Propose: Seed your list from the glossary's homes and the topic map's home table, then read each topic. Prefer ideas the reader needs over ideas that are easy to name. Two names for one idea are one concept: use the glossary's word.}
{Record uses: Give each use the one section that uses the concept most, and one sentence on what the topic does with it. A topic never uses its own concept.}

{Anything about one topic or concept that needs extra care, and why.}

## Model and budget

You run on {the strongest model}. Your budget is about {tokens} tokens.

## Read before you start

1. `AGENTS.md`
2. The run picture: `{orchestration/briefs/run-NN/picture.md}`.
3. `docs/method.md`, "Key concepts", and `engine/format.md`, "The concept file".
4. `context/glossary.md` and the topic map's home table in `curriculum/topic-map.md`.
5. {Record uses: the merged list, `{research/concepts-merged.md}`.}
6. The topics in your scope.

## Fixed

- Find each section's anchor in a build of your own: `python3 engine/build.py --out {a folder of your own}`. Don't build into `site/`.
- Don't edit the topics, the glossary or `content/concepts.json`. Propose changes to them in your handoff.
- Don't run git.

## What you own

- `research/{concepts-proposed-<scope> | concept-uses-<scope>}.md`
- `orchestration/handoffs/{date}-concepts-{scope}.md`

## Hand back

The research file and the handoff. Finish with a short summary for someone who wasn't watching:

- {Propose: the concepts per topic, and the ones you weighed and left out;}
- {Record uses: the uses per topic, and the ones you judged too weak to count;}
- any concept whose home looks wrong, or that two topics both explain;
- the tokens you think you used.
