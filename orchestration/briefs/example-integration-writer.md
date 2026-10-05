<!-- Example. A filled integration-writer brief for the engine's test guide, a first season keeping bees, in engine/tests/fixture/. Its run and dates are invented: it assumes run 2 put all five topics live. Copy the shape, and write your own content. -->

# Brief: integration writer, run 3

## Goal

Write the text that ties the guide together, in one voice: the three tier maps, the home page text and the open-questions page. All five topics are live. Sam reads the home page first, and takes the open-questions page to the association's first meeting of the season.

The work is done when each file meets its part below, passes the writing rules and the lint, and the format check reads it.

## The files

- **The tier maps.** `content/base/intro.md` is a first draft from after the pilot: revise it against B01 and B02, at about its current length. Practical and Modern have no map yet: write `content/practical/intro.md` and `content/modern/intro.md`. Each map says how its topics fit together. The Modern map also says which Base and Practical topics M01 updates.
- **The home page text,** `content/home.md`. It exists. Revise it to say what the guide is, how the ranks work, how to read it, and what the private blocks are. The build adds the reading order, the tiers and the totals below your text, so frame them and don't repeat the numbers. Aim for about 250 words.
- **The open-questions page,** `content/questions.md`. It exists, with OQ-01 and OQ-02. Add OQ-03 on the swarm collection list, and keep every ID.
- **For each question,** say why it matters to Sam and which topics depend on it. Say who can settle it: the seller, the secretary or the mentor. Group the questions so Sam can take them to the right person.

## Fixed

- `docs/standards/writing.md` and the glossary's words. Speak to Sam as "you".
- No new facts about the apiary or the association. Every fact comes from a topic or a context note, with its tag.
- What the mentor said sits in a private block. A block's title is public text. On the open-questions page, the line that opens a question is public too: it shows in every link to the question.
- The markup in `engine/format.md`, "Pages without parts". If you need more, say so in your handoff, and use only the markup that exists.

## Model and budget

You run on the strongest model. Your budget is about 150,000 tokens.

## Read before you start

1. `AGENTS.md`
2. The run picture: `orchestration/briefs/run-03/picture.md`.
3. `orchestration/worker-pack.md`, and `engine/format.md` ("Pages without parts" and private blocks).
4. `docs/request.md`: Sam's own words on the goal and the tiers.
5. `curriculum/topic-map.md`, `context/open-questions.md` and `context/glossary.md`.
6. Each topic's header and short version. Read further where a page needs it.

## What you own

- `content/base/intro.md`, `content/practical/intro.md`, `content/modern/intro.md`
- `content/home.md` and `content/questions.md`
- `orchestration/handoffs/2026-10-07-integration-pages.md`

Write nowhere else. Don't run git or the build. Run the format check on each page, such as `python3 engine/topic.py content/questions.md`.

## Hand back

The pages and the handoff. Finish with a short summary for someone who wasn't watching:

- what each page now does;
- how you grouped the questions, and why;
- the tokens you think you used.
