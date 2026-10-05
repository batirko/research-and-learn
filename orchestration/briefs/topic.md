# Brief: topic worker, {cluster or topic ID}

## Goal

Research and write {this topic | these topics} of the guide, critical ones first:

- **{ID} {Title}.** {Tier}, {rank}, {size}, cluster {C#}.

A topic is done when it meets "Done means" in `docs/standards/topic-page.md`, and the format check and the lint give 0 errors.

## Why {this topic | these topics}

{Two or three sentences: what the topic does for the reader's goal, and how it meets the topics other workers write. Say what the reader must be able to do with it.}

## The reader

{The reader's name, the goal and the date, in one or two sentences.} Write for someone who has heard of the subject and hasn't studied it. `context/reader.md` says more.

## Model and budget

You run on {the strongest model}. Your budget is about {tokens} tokens per topic.

{Keep one of these two lines.}

- {Lean mode:} You can't start subagents, so research alone.
- {Full mode:} You can start one helper on {a smaller model} to find candidate sources, with a budget of {tokens}. Set its model. Do the writing yourself.

Before you start, fetch one page you need. If the fetch fails, stop and say so in your handoff. A topic written without the web is written from memory.

## Read before you start

1. `AGENTS.md`
2. The run picture: `{orchestration/briefs/run-NN/picture.md}`. It's part of this brief.
3. `orchestration/worker-pack.md`. Open a standard only where the pack points you to it.
4. `engine/format.md`, in full.
5. `context/glossary.md`, and the titles in `context/open-questions.md`.
6. {The context notes these topics touch, and which sources to search.}
7. Your topics' entries in `curriculum/topic-map.md`, and its homes table.
8. {The live topic closest to yours, as a worked example of the form. Not of its length.}

## Fixed

- The standards, the glossary and the format.
- You open every source you cite. A link from memory or a search snippet doesn't count.
- Every fact about the case carries a provenance tag. A guess about the case is a defect. An unknown is written as unknown, with its open question's ID.
- A private fact sits in a private block. A block's title and a visual's title are public text. Search your public text for a private fact restated in other words.
- {Homes: the concepts your topics are the home of, and the topics that hold the ones next to them. Link to a home; don't explain its concept again.}
- Size {size}: aim at the middle of the band, about {n} words. The top of the band is a ceiling, not a target. {No XL. | XL granted, because {reason}.}
- At most `materials.per_topic` materials per topic ({n}). Critical materials: at most {n} for {these topics}, within the cluster's quota in the run picture.
- {The known errors in the sources that touch these topics, from the worker pack.}
- {When the case's owners name several competing explanations for something your topic covers: weigh all of them, and pick none before the evidence does.}

## Yours to decide

- How you research, and which sources you choose. The seeds in the map are leads that nobody has verified, and you'll find better ones.
- The questions. The map's starting questions were written before research. Answer them, or replace one and say why in your handoff.
- How each explanation is built, and the ranks of its sections and materials.
- Whether a visual passes the test in `docs/standards/visuals.md`.

If the map is wrong about a topic, say so in your handoff: its scope, its rank, or whether it is one topic or two. If what you find contradicts the context notes, the evidence wins. Say so in your handoff too.

## What you own

- `research/{id}-{slug}.md` for each topic: your dossier, with every candidate source and your verdict on it.
- `content/{tier}/{id}-{slug}/` for each topic.
- `orchestration/handoffs/{date}-topic-{scope}.md`.

Write nowhere else. Don't run git or the build. Run the format check and the lint on your own files.

## Hand back

The topics, the dossiers and the handoff. `orchestration/handoffs/README.md` lists what a handoff holds.

Finish with a short summary for someone who wasn't watching:

- what now exists;
- what you couldn't verify;
- what you need decided;
- the tokens you think you used.
