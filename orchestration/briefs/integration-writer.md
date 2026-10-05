# Brief: integration writer, {scope}

## Goal

Write the text that ties the guide together, in one voice: {the first drafts of the tier maps | the finished tier maps, the home page text and the open-questions page}.

The work is done when each file meets its part below, passes the writing rules and the lint, and the format check reads it.

## The files

- **The tier maps,** `content/{tier}/intro.md`, one per tier. Each is a short mental map of how its tier's topics fit together. It gives a reader who starts with critical topics a frame.
  - {After the pilot:} write a first draft from the map and the live topics.
  - {At integration:} revise the drafts against the written topics, at about their current length.
- **The home page text,** `content/home.md`. What the guide is, how the ranks work, how to read it, and what the private blocks are. The build adds the reading order, the tiers and the totals below your text. Frame them, and don't repeat the numbers. {Aim for about n words.}
- **The open-questions page,** `content/questions.md`. The open questions in `context/open-questions.md`, made into a page the reader takes into the case. Each question in the reader's terms, why it matters, the topics that depend on it, and who can settle it. Group them so the reader can plan. Keep every ID, because topics link to them.

{Delete the files this visit doesn't write.}

## Fixed

- `docs/standards/writing.md` and the glossary's words. Speak to the reader as "you".
- No new facts about the case. Every fact comes from a topic or a context note, with its tag.
- A private fact sits in a private block, and a block's title is public text. On the open-questions page, the line that opens a question is public too: it shows in every link to the question.
- The markup in `engine/format.md`, "Pages without parts". If you need more, say so in your handoff, and use only the markup that exists.

## Model and budget

You run on {the strongest model}. Your budget is about {tokens} tokens.

## Read before you start

1. `AGENTS.md`
2. The run picture: `{orchestration/briefs/run-NN/picture.md}`.
3. `orchestration/worker-pack.md`, and `engine/format.md` ("Pages without parts" and private blocks).
4. `docs/request.md`: the owner's own words on the goal, the tiers and the ranks.
5. `curriculum/topic-map.md`, `context/open-questions.md` and `context/glossary.md`.
6. Each topic's header and short version. Read further where a page needs it.

## What you own

- The files above.
- `orchestration/handoffs/{date}-integration-{scope}.md`.

Write nowhere else. Don't run git or the build. Run the format check on each page, such as `python3 engine/topic.py content/questions.md`.

## Hand back

The pages and the handoff. Finish with a short summary for someone who wasn't watching:

- what each page now does;
- what you chose, and why;
- the tokens you think you used.
