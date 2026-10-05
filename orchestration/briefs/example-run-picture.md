<!-- Example. A filled run picture for the engine's test guide, a first season keeping bees, in engine/tests/fixture/. The run, its dates, its workers and its findings are invented. Copy the shape, and write your own run's content. -->

# The run around you: run 2, 2026-10-06

Every brief in this run points at this file. It's part of your brief, so read it in full.

## Where the build stands

The pilot is done, and Sam accepted it on 5 October 2026. Three topics are live: B01 How a colony works, P01 Inspecting a hive, and M01 Hive monitors: scales, sensors and apps. This run writes the two high topics, B02 The beekeeping year and P02 Swarm control. A facts check then reads both, and a fix worker applies its findings. Next to them, a context worker checks the association's public pages, and a portal worker builds the apiary sheet Sam asked for. `orchestration/handoffs/2026-10-05-orchestrator.md` has the pilot's account.

## The workers in this run

All workers share one workspace folder, with no worktrees. Nobody but the orchestrator runs git or the build (`python3 engine/build.py`).

| Worker | Model | Writes these files, and nothing else |
| --- | --- | --- |
| Topic worker, B02 | Opus | `content/base/b02-the-beekeeping-year/`, `research/b02-the-beekeeping-year.md`, handoff `orchestration/handoffs/2026-10-06-topic-b02.md` |
| Topic worker, P02 | Opus | `content/practical/p02-swarm-control/`, `research/p02-swarm-control.md`, handoff `orchestration/handoffs/2026-10-06-topic-p02.md` |
| Context worker | Opus | `context/association.md`, new files in `context/sources/`, handoff `orchestration/handoffs/2026-10-06-context-association.md` |
| Portal worker | Opus | The files under `engine/` its brief names, handoff `orchestration/handoffs/2026-10-06-portal-apiary-sheet.md` |
| Later: facts check | Sonnet | `reviews/facts-2026-10-06-b02-p02.md`, handoff `orchestration/handoffs/2026-10-06-facts-run-02.md` |
| Later: fix worker | Opus | The topic folders and dossiers its brief names, handoff `orchestration/handoffs/2026-10-06-fix-run-02.md` |

A file the table doesn't give you is read-only for you. That covers `content/`, `research/`, `context/`, `curriculum/`, `docs/`, `engine/`, `tools/`, `guide.toml` and `orchestration/`, apart from your own files. If a shared file needs a change, propose it in your handoff.

Other workers' drafts might appear in the folder while you work. Don't rely on them until their handoff.

## How this run's topics meet the others

- **B02 is the home of the season:** when a colony grows, swarms, stores and shrinks, and what the beekeeper does in each stretch. B01 holds the brood clock, how long each kind of bee takes to emerge. Link to B01 for the numbers.
- **P02 is the home of swarm control:** the signs before a swarm, and the methods that suit a beekeeper with two hives. P01 holds reading a frame. B01 holds why a colony raises a new queen. B02 says when in the year swarms come, and P02 says what to do about them.
- M01 lists a vendor's claim that sound monitors hear a colony preparing to swarm, as not verified. P02 can link to M01, and doesn't need to settle that claim.
- The glossary's words are fixed: "inspection", "sealed brood", "forager" and "queen". Its "Don't use" column lists the words they replace.

Link to any topic with `[[ID]]`, written or not. To see what live topics already promise about yours, search `content/` for `[[B02]]` or `[[P02]]`.

## Critical materials

This guide allows three (`materials.critical_in_guide`), one per cluster.

- C1 has 1, and B01 used it. B02 proposes none.
- C2 has 1, unused. P02 can propose one.

## Sizes

This guide's bands are smaller than the defaults, because it's a test guide. B02 is S, 150 to 700 words: aim near 425. P02 is M, 700 to 1,200 words: aim near 950. No XL. A high topic reaches depth level 2.

## What earlier checks caught

The pilot's reviews found these. Check for them before you hand off.

- **The mentor's advice in public text.** A pilot topic said in public text what the mentor does with a weak colony. The mentor call is private, so what the mentor said goes in a private block, with its tag. The public text says what a beekeeper can do.
- **A hedge dropped.** The mentor said "I'd usually", and a draft wrote "always". Keep each speaker's own hedge.
- **A guess about Sam's apiary.** "Your colonies will swarm in May" guesses about the case. Cite the handbook's months for the association's apiary, or write the month as unknown.

## The environment

- The web works. The orchestrator fetched a national beekeeping body's advice page on swarm control before starting this run.
- No exercise in this guide needs software. An exercise happens at the hive, so write its steps, and don't claim you ran it.
- Scratch files go in a folder named after your worker, in the session's scratch directory. Not in the workspace.
- If the permission system blocks the format check or the lint, don't retry. Say so in your handoff, and the orchestrator runs them.
- A usage limit can stop you at any time. Write to disk as you go.
- If you pass your budget, stop, and hand off what you have with what's left.
