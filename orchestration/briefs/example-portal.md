<!-- Example. A filled portal brief for the engine's test guide, a first season keeping bees, in engine/tests/fixture/. It belongs to the run in example-run-picture.md. The request and the setting it names are invented. Copy the shape, and write your own content. -->

# Brief: portal worker, the apiary sheet

## Goal

At the pilot review, Sam said: "I want one sheet I can take to the hive." Build a page that gathers the "What to check first" list from every written topic's case part. Group the lists by tier, and fit them on as few printed sheets as you can.

The work is done when three things hold. A build into your own folder passes all eight checks. The page works from disk with the network off. It holds in both themes, at phone width and in print.

## Why

Sam reads the guide at a desk and works at the hive with gloves on. Each topic ends its case part with what to check first, and today those lists sit on three pages, and on five once B02 and P02 land. One printed sheet puts them where Sam needs them.

## Model and budget

You run on the strongest model. Your budget is about 200,000 tokens. Set the model on any subagent you start.

## Read before you start

1. `AGENTS.md`
2. The run picture: `orchestration/briefs/run-02/picture.md`.
3. `docs/standards/portal.md`: what the portal must do. `engine/design.md`, "Print", for how a page prints.
4. `engine/format.md`: the case part's three blocks, and their headings in `guide.toml`.
5. `guide.toml`, and the engine's code under `engine/`.
6. The live topics B01, P01 and M01, which each have a case part.

## Fixed

- The portal opens from disk and works with the network off. Nothing loads from the network.
- Python 3.11 or later, standard library only. Plain JavaScript, with no libraries.
- The page's title and its link text come from `guide.toml`, with a comment, because another guide names its case part differently. A guide whose `case.part` is `""` builds no such page.
- The eight checks keep passing, and check 3 covers the new page's links. Don't weaken a check to pass it.
- Private stays private. A private block on the sheet stays closed, follows the print rule in `engine/design.md`, "Print", and stays out of search.
- Every live topic still builds, and the topic file format doesn't change.
- An upgrade replaces `engine/`. List every file you change, and why, so the change can be made again.

## Yours to decide

How the page is built, where it's linked from, and its print layout, within the portal standard.

## What you own

- The files under `engine/` the page needs.
- `orchestration/handoffs/2026-10-06-portal-apiary-sheet.md`.

Don't edit `content/`. If a topic breaks the build, report it. Build with `python3 engine/build.py --out` and a folder in your scratch directory, never into `site/`. Don't run git.

## Hand back

The changed engine and the handoff. The handoff lists the files you changed and why, the setting you added, how you tested the page, and any change you propose to `docs/standards/portal.md`.

Finish with a short summary for someone who wasn't watching:

- what the portal does now;
- what you need decided;
- the tokens you think you used.
