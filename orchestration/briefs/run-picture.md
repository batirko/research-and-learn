# The run around you: {run name}, {date}

Every brief in this run points at this file. It's part of your brief, so read it in full.

## Where the build stands

{The phase. Which topics are live, by ID. What this run writes or checks. The path of the last orchestrator handoff.}

## The workers in this run

All workers share one workspace folder, with no worktrees. Nobody but the orchestrator runs git or the build (`python3 engine/build.py`).

| Worker | Model | Writes these files, and nothing else |
| --- | --- | --- |
| {Topic worker, P02} | {model} | {`content/practical/p02-.../`, `research/p02-....md`, its handoff} |
| {Later: facts check} | {model} | {`reviews/facts-run-02.md`, its handoff} |

A file the table doesn't give you is read-only for you. That covers `content/`, `research/`, `context/`, `curriculum/`, `docs/`, `engine/`, `tools/`, `guide.toml` and `orchestration/`, apart from your own files. If a shared file needs a change, propose it in your handoff.

Other workers' drafts might appear in the folder while you work. Don't rely on them until their handoff.

## How this run's topics meet the others

{For each topic in the run: the concepts it's the home of, and the neighbouring topics that hold the concepts next to it. Which live topics it builds on. The map's homes table decides who explains what.}

Link to any topic with `[[ID]]`, written or not. To see what live topics already promise about yours, search `content/` for `[[YOUR-ID]]`.

## Critical materials

{Each cluster this run touches: its quota, what's used, and what's left for this run's topics. Two workers in one cluster share what's left, so say who can propose what.}

## Sizes

{The band of each topic in this run, from `[sizes]` in `guide.toml`, and the word count to aim at: the middle of the band. Any XL granted, and why. The depth each rank reaches.}

## Tiers whose facts age fast

{Keep this section when a topic in the run sits in a tier with `fast = true`, and delete it otherwise.}

- Date each claim about a tool to the month.
- Give the topic a `check again` date.
- Prefer materials newer than `materials.max_age_months` (18). An older one needs a stated reason.

## What earlier checks caught

{The patterns the last checks found, written as rules to follow before you hand off. Delete this section on the first run.}

## The environment

- {Web access: which page the orchestrator fetched to confirm it, and which sites block scripted fetches.}
- {Tools installed for exercises. Don't install new software yourself; write the exercise, mark the steps you couldn't run, and say so.}
- {Where scratch files go: a folder of your own, named after your worker.}
- If the permission system blocks the format check or the lint, don't retry. Say so in your handoff, and the orchestrator runs them.
- A usage limit can stop you at any time. Write to disk as you go.
- If you pass your budget, stop, and hand off what you have with what's left.
