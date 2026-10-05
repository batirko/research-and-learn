# AGENTS.md

The operating guide for every agent in this workspace: the orchestrator, every worker, and any session the owner opens. Read it first.

## What this workspace is

It builds a guide to a subject that its reader must understand by a date. The guide is a local HTML portal of ranked topics in tiers. Each topic explains its subject from the ground up, then offers a few ranked materials for depth. `docs/method.md` has the method on one page, and `docs/concept.md` has the whole design.

## Where to start

Find the first line that fits, and follow it.

1. **`docs/request.md` still reads "Status: template, not filled yet."** The workspace has no guide yet. Run the set-up skill (`.claude/skills/set-up/`). It interviews the owner and writes the settings.
2. **The request is filled, and `curriculum/topic-map.md` still reads "Status: template, not filled yet."** Run the scaffold skill (`.claude/skills/scaffold/`). It researches the case and proposes the topic map.
3. **The topic map exists.** You are the orchestrator unless a brief says otherwise. Read `orchestration/playbook.md`, then `orchestration/board.md`. No worker starts before the owner has answered the kickoff.
4. **You have a brief.** You are a worker. Your brief names your goal, your reading and the files you own. End by writing a handoff in `orchestration/handoffs/`.

## Hard rules

1. **No invented facts.** Every outside claim has a source you opened in this session. Every fact about the case carries a provenance tag. An unknown is written as an open question, never as a guess. `context/README.md` lists the tags.
2. **Evidence and interpretation stay apart.** The context notes are a first reading made before anyone knew the case well. When your research contradicts them, the evidence wins, and you say so in your handoff.
3. **Private stays private.** A fact from a private source sits in a private block. What is on `context/never-publish.md` never enters a topic, and the build fails if it reaches the portal.
4. **Sources are frozen.** Nobody edits a file in `context/sources/`. A correction goes into the worker pack, so every later worker sees it.
5. **One word per concept, one home per concept.** `context/glossary.md` holds the words. The topic map names the topic that explains each shared concept; the others link to it.
6. **Write only the files your brief names.** Propose changes to shared files in your handoff.
7. **Only the orchestrator runs git.** Workers share one folder, and a git command in one can capture or wipe another's files.
8. **`engine/` and `tools/` hold no guide content.** An owner upgrades by copying them from a newer release, so anything written there would be lost.

## When documents disagree

The higher one wins. Say in your handoff that you found a conflict.

1. `docs/request.md`: the owner's own words.
2. `docs/decisions.md`: decisions the owner has confirmed.
3. `docs/standards/`, with the values in `guide.toml`.
4. `curriculum/topic-map.md`
5. `orchestration/worker-pack.md`
6. Your brief.

## Document map

| File | Read it when |
| --- | --- |
| `docs/method.md` | You need the method: tiers, ranks, a topic's parts, depth, visuals, evidence, privacy, words |
| `docs/request.md` | You need the owner's request, the goal, the date, or the assumptions still to confirm |
| `docs/decisions.md` | You are about to reopen something that looks settled |
| `docs/standards/topic-page.md` | You write or review a topic |
| `docs/standards/sources.md` | You pick, check or rank a source or a material |
| `docs/standards/visuals.md` | You consider a diagram |
| `docs/standards/writing.md` | You write a sentence the reader will see |
| `docs/standards/portal.md` | You touch the portal or share it |
| `engine/format.md` | You write a topic file |
| `guide.toml` | You need a number: a size band, a limit, a quota total. The standards name the setting |
| `context/` | You need a fact about the reader, the goal or the case. Start at `context/README.md` |
| `curriculum/topic-map.md` | You need what a topic sets out to answer, its rank and size, or a concept's home |
| `orchestration/worker-pack.md` | You are a worker: it condenses the request, the reader and the standards |
| `orchestration/playbook.md` | You are the orchestrator |
| `orchestration/board.md` | You need the status of a topic |

## Commands

The engine needs Python 3.11 or later. If `python3` is older, call `python3.11`.

| To | Run |
| --- | --- |
| Check a topic you wrote | `python3 engine/topic.py content/<tier>/<id>-<slug>` |
| Lint it | `python3 tools/lint.py content/<tier>/<id>-<slug>` |
| Build the portal and run the checks (orchestrator only) | `python3 engine/build.py` |
| Build a copy to share, without the private blocks | `python3 engine/build.py --share` |
| Scan that copy before it goes to anyone | `python3 tools/scan.py files site-share/ --terms <the owner's list>` |

`engine/README.md` explains the build and its eight checks.

## Writing

Write in the Google developer documentation style: one idea per sentence, active voice, present tense, and exact words for certainty. `docs/standards/writing.md` has the guide's rules. Before you hand off any prose, run the slop pass in `.claude/skills/no-ai-slop/` in detect mode, and fix what it finds.

## Subagents

Set the model on every spawn; a subagent otherwise inherits its parent's. Use the smallest model that can do the job: a smaller model to find sources, check links and check facts, the strongest to write, review and design. `orchestration/playbook.md` has the table.

## Working with the owner

- The owner may run several sessions and come back cold. Lead with what the guide now does, or with the decision you need.
- Recommend one path, with its reasoning. Don't list the options you would not take.
- Ask only when a wrong guess would waste a worker's run. Otherwise decide as a careful colleague would, and log it in `docs/decisions.md`.

## This repository

If you are working on research-and-learn itself rather than on a guide: no file from a real guide ever enters this repository. A lesson from a real guide comes back only as a general rule, re-authored, with no fact about its case. The git hooks in `.githooks/` scan every commit and push for private terms and secrets; turn them on with `git config core.hooksPath .githooks`.
