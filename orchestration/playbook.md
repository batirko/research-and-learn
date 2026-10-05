# The orchestrator's playbook

This page is for the session that coordinates the build. It says what each phase needs, who does what, and how workers stay out of each other's way. It gives you the goal and the limits. How you run each step is your call.

## Your job

You're the **orchestrator**: the session that turns a scaffolded workspace into a finished guide. You don't write topics. You:

- start workers, each with a brief, and read their handoffs;
- keep the shared files true: the board, the topic map, the glossary, the open questions, the worker pack and the decision log;
- run the build and git;
- bring the owner in when a decision is theirs, and not otherwise.

A **worker** is a subagent or a session that does one job. A **brief** is its instructions. A **handoff** is the file it leaves when it finishes. A **run** is a set of workers you start together. They share one **run picture**: a file that every brief in the run points at.

## Before you start

Two skills come first: `.claude/skills/set-up/` and `.claude/skills/scaffold/`. Check that both have run:

- `guide.toml` names the guide, the reader and the tiers.
- `docs/request.md` holds the owner's request and its assumptions.
- `curriculum/topic-map.md` holds a proposed map, and `orchestration/board.md` lists its topics.

If one is missing, run the skill that writes it. Then start at the kickoff.

## The phases

| Phase | What happens | What the owner does |
| --- | --- | --- |
| Set-up | The set-up skill interviews the owner and writes the settings | Answers, and drops sources into `context/sources/` |
| Scaffold | The scaffold skill writes the context notes and proposes the topic map | Nothing |
| Kickoff | You put the kickoff questions and record the answers | Confirms or changes |
| Pilot | One topic per tier, written, checked and built | Reads them, and answers six questions |
| Waves | Critical topics, then high, then medium, built as each finishes | Starts reading. Can stop the build |
| Integration | Tier maps, the home page, the open-questions page, and checks across the guide | Nothing |
| Reading | Fixes go out in batches | Reads, marks and notes |

The owner is needed at three points: the set-up, the kickoff and the pilot. Bring any other question only when a wrong guess would waste a worker's run.

## The two modes

| | Lean, the default | Full |
| --- | --- | --- |
| Workers | Subagents of your session | Separate sessions. The owner starts each one with its brief, unless your harness can |
| A topic worker's research | Its own. A subagent can't start subagents | It can start one helper on a smaller model |
| Independent review | The pilot topics, and the topics that rest most on facts about the case | Every topic |
| Facts check | Every other topic that rests on the case, a batch at a time | Not needed. Each review checks its topic's facts |
| Every topic | The writer's done-list, the format check and the lint | The same |
| Tokens per topic, to reach the portal | About 320,000 to 400,000, or 480,000 to 650,000 with a review | About 480,000 to 650,000 |

The token figures were measured on the 45-topic guide this workspace was extracted from, as the agent tool reported them. At that rate, 15 topics cost about 5 to 6 million tokens in the lean mode, before the scaffold and integration.

**Why the lean mode checks where it does.** A check of first-reading context notes found 17 wrong or overstated claims among 176. A wrong fact about the case costs the reader in the case. A loose sentence of background costs little. So checking effort goes where a wrong fact costs most. In a guide without a case, that means the claims a reader acts on: a dose, a deadline, a rule.

**A reviewed topic gets no separate facts check.** Its reviewer checks every claim about the case in it, not a sample.

**In either mode, an unattended session stops at the first permission prompt.** A usage limit can stop every running worker at once. So you commit at every quiet point, workers write to disk as they go, and you say at kickoff whether your session can work alone.

## Kickoff

The scaffold ends by putting the kickoff questions to the owner. Record the answers they give. Ask again only what's still open.

The kickoff questions:

1. **The assumptions.** The table in `docs/request.md`, including every default the set-up took. "I accept them all" is an answer.
2. **The map.** The shape (topics by tier and rank), the titles, and the reading time against the owner's hours. The owner can change any of it, or leave the map for the pilot review.
3. **The pilot.** The recommended topics, one per tier.
4. **How the build runs.** The mode. The projected token cost, and whether it fits the owner's plan. Whether your session can work without permission prompts. Say that you commit at every quiet point, unless the owner says otherwise.

Record the answers in `docs/decisions.md`, in the owner's own words where they gave them, as its instructions say. Mark each assumption in `docs/request.md` confirmed or changed. Put the projection on the board. No worker starts before the kickoff is answered.

To project the cost, count the topics that get a review and those that don't. Multiply each count by its figure in the modes table.

## The pilot

**The pilot comes before the fan-out.** The owner's preferences on depth, length and visuals show up only when they see a page. Writers fill a size band to its ceiling, and owners cut the bands once they read the result. A change is cheap now and costly after thirty topics.

Build one topic per tier end to end, and a portal that shows them. The map recommends which. Pilot topics are written before their prerequisites exist, so they stand alone and gain their links later.

One workable order:

1. If the guide has a case, a facts check reads the context notes against the sources. The scaffold wrote them as a first reading, and a first reading overstates.
2. One topic worker per pilot topic, all at once.
3. One review worker per pilot topic, in both modes.
4. A fix worker applies each review.
5. You build the portal and run the eight checks.
6. **Stop.** The owner reads the pilot topics in the portal.

Ask the owner about six things: the depth, the length, the ranks, the materials, each visual, and the design. Then change what their answers change:

- the size bands (`[sizes]`) and the material limits (`[materials]`) in `guide.toml`;
- the standards and the worker pack;
- the map: ranks, sizes, titles and homes;
- the design: `portal.accent_hue` and the other `[portal]` settings, or a portal worker for what the settings can't do.

Log each change in the decision log. When the owner says the length is right, briefs still say "aim at the middle". The top of a band is a ceiling, not a target.

Right after the pilot, an integration writer drafts each tier's map, `content/<tier>/intro.md`. The owner reads critical topics for days before the last topic exists, and the maps give those topics a frame. Integration revises them.

## The waves

Critical topics come first, with the high topics they depend on. The map's reading order lists them. Then high topics, then medium ones, by cluster.

- A wave takes several runs. Start at most five workers in a run.
- Give a topic worker the topics of one cluster. When they won't fit one worker's budget, give it one topic.
- A topic moves through `writing`, `check`, `fix` and `live`. A topic that rests on nothing about the case and has no review goes live once its format check and lint pass.
- Rebuild the portal as each topic goes live. A finished topic is worth nothing to the reader until they can open it.
- When the critical topics are live, tell the owner. They can start reading, and they can stop the build when they have enough.

## Integration

Integration ties the guide together and checks it as a whole.

| Work | Who |
| --- | --- |
| Finish the tier maps. Write the home page text (`content/home.md`) and the open-questions page (`content/questions.md`) | One integration writer, so the pages read as one voice |
| Check links against the map's homes. Check the glossary: banned words in topics, words it doesn't know, rows without a home. Compare ranks across the guide, and count materials per topic. Sort the lint's warnings into real ones and false ones | A review worker whose scope is the whole guide. A helper on a smaller model can run the counts first |
| Compare the strongest materials across the guide, and promote the ones writers held back | The same review worker, or you |
| Check every fact about the case on the new pages | A facts check |
| Apply the findings to topics | A fix worker |
| Finish the glossary: a home for every row, and the terms the handoffs proposed | You, or one worker you give the glossary to for that task |
| Build, and run the eight checks | You |

**Why the materials pass exists.** Writers judge critical materials one cluster at a time, and they pick too few. Each holds a slot for a sibling topic, and the sibling does the same. One pass across the guide finds the originals the reader will work from.

## Reading

The owner reads, marks and notes in the portal. Their marks and notes stay in their browser. Keep a short list of the fixes they ask for, and send them out in batches. A fix to a finished topic goes to a fix worker, with a brief that names the topic's files.

Before the owner shares the portal, build a copy without the private blocks, `python3 engine/build.py --share`, and run the private-term scan on it: `python3 tools/scan.py files site-share/ --terms <list>`. The term list lives outside the workspace.

## The checks

| Check | What it does | Who runs it |
| --- | --- | --- |
| The done-list | "Done means" in `docs/standards/topic-page.md` | The topic worker, before its handoff |
| The format check | `python3 engine/topic.py <topic folder>`: can the build read the file? | The topic worker, then you |
| The lint | `python3 tools/lint.py <paths>`: the writing rules, the material limits, the tags and the glossary | The topic worker, then you |
| The facts check | Every tagged claim against its source | A facts check. Lean mode: topics, a batch at a time. Both modes: the context notes before the pilot, and the integration pages |
| The independent review | A reader who didn't write the topic, then the standards | A review worker. Lean: the pilot and the topics that rest most on the case. Full: every topic |
| The build | `python3 engine/build.py`: the portal, the eight checks and the never-publish guard | You, each time a topic goes live |

A topic that fails a check goes to a fix worker with the findings.

## Kinds of worker

| Worker | Does | Model | Template |
| --- | --- | --- | --- |
| Topic worker | Researches and writes the topics of one cluster, or one topic | The strongest | `briefs/topic.md` |
| Review worker | Reads finished topics as the reader would, then checks them against the standards | The strongest | `briefs/review.md` |
| Facts check | Compares every tagged claim with its source | A smaller model | `briefs/facts-check.md` |
| Fix worker | Applies a check's findings to topics | The strongest | `briefs/fix.md` |
| Context worker | Checks and extends the context notes | The strongest | `briefs/context.md` |
| Portal worker | Changes the portal's design or the engine | The strongest | `briefs/portal.md` |
| Integration writer | Writes the tier maps, the home page text and the open-questions page | The strongest | `briefs/integration-writer.md` |
| Helper | Finds candidate sources, checks links, runs the lint and counts | A smaller model | None. Its brief is a goal, its files, its model and its budget |

A worker is a subagent in the lean mode and a session in the full mode. The templates serve both.

## Who edits what

Workers share one folder, with no worktrees. That works only when no two workers write the same file.

| Path | Who writes it |
| --- | --- |
| `orchestration/board.md`, `docs/decisions.md`, `docs/request.md`, `curriculum/topic-map.md`, `context/glossary.md`, `context/open-questions.md`, `context/never-publish.md`, `orchestration/worker-pack.md`, `docs/standards/`, `guide.toml`, `orchestration/briefs/` | You. You can give one of them to one worker for one task, and the brief says so |
| Other notes in `context/` | You, or a context worker you assign |
| `context/sources/`, `reference/` | Nobody changes a file there. A context worker can add a new dated file, and its row in `context/sources/README.md` |
| `research/<id>-<slug>.md`, `content/<tier>/<id>-<slug>/` | The topic worker that has the topic, then the fix worker a brief names |
| `reviews/` | The review worker or the facts check that writes the file |
| `content/<tier>/intro.md`, `content/home.md`, `content/questions.md` | The integration writer |
| `engine/`, `tools/` | A portal worker |
| `site/` | The build, which only you run |
| `orchestration/handoffs/<file>` | The worker that writes it |

A worker that needs a change in a file it doesn't own proposes the change in its handoff.

Workers don't run the build. It writes `site/`, and two builds at once collide. A portal worker tests with `--out` and a folder of its own.

An upgrade replaces `engine/` and `tools/` with a newer release. So log every change a portal worker makes there, with its reason, and it can be made again after an upgrade.

## Git

**Only you run git.** Workers share one folder. A worker's `git add`, `git stash` or `git checkout` can capture or wipe another worker's files.

**Commit at every quiet point.** A quiet point is a moment when no worker is writing: between runs, or after a run's last handoff. A permission prompt or a usage limit can stop every worker at once, and a commit is what survives it. Write the message as what the guide now has, such as "P02 live after its facts check".

Don't push unless the owner has named a remote. `site/` stays out of git, because the build makes it.

If the workspace isn't a git repository, ask at kickoff whether to start one.

## Handoffs

Every worker ends by writing a handoff in `orchestration/handoffs/`. The README there says what a handoff holds and how it's named. A subagent also returns a summary to you, but the file is what lasts.

Read each handoff. Then:

- update the board;
- decide on the worker's proposals for shared files: glossary terms, open questions, homes, context notes. Log a change when it changes what later workers do;
- add each error a worker found in a source to the worker pack. Sources are frozen, so the correction lives there, and every later worker sees it;
- record the tokens the worker used;
- collect the questions for the owner.

At the end of each session, write your own handoff. The README in `orchestration/handoffs/` lists what it holds.

## Writing a brief

A brief gives a worker context, not a design.

- State the goal, why it matters, the limits that are fixed, and where to read more.
- Leave the approach open. A brief that lists steps caps the worker at your first idea, and a worker that reads the sources often finds a better one.
- Name the files the worker owns, and say "nowhere else".
- Put what all the run's workers share in the run picture, and point every brief at it. The template, `briefs/run-picture.md`, lists what it covers.
- Set the model and a budget. Say what to do when the budget runs out: stop, and hand off what exists.
- Tell a worker that uses the web to fetch one page it needs before it starts, and to stop if the fetch fails. A session that can't reach the web writes from memory.
- Give the size as "aim at the middle of the band", with the number. Grant an XL in the brief before writing, or not at all.
- Give a topic worker its cluster's quota of critical materials, and what's used.
- When the people who own the case name several competing explanations, the brief says to weigh all of them. A topic doesn't pick one before the evidence does.

Before you start a worker, write its brief to a file in the run's folder, such as `orchestration/briefs/run-03/topic-p02.md`. Write the run picture there too. In the lean mode, the subagent's prompt points at the file. A new orchestrator can then see what each worker was asked. `orchestration/briefs/README.md` lists the templates, with a filled example of each.

## Models

Pick the smallest model that can do the job, and set it on every spawn. A subagent inherits its parent's model otherwise.

| Work | Model |
| --- | --- |
| Writing, reviewing, fixing, context work, the portal, the integration pages | The strongest you have: Opus, in Claude Code |
| The facts check, finding candidate sources, checking links, running the lint and counts | A smaller model: Sonnet, in Claude Code |
| A model that costs more than the strongest standard one | Only after the owner agrees, and never several at once |

If usage limits bite, build fewer topics. Don't build them on a smaller model.

## The cost log

You log each run's token cost and compare it with the projection, so the plan changes before the budget runs out.

- **Start each worker with a budget in its brief.** The table below gives starting budgets. A facts check and a fix usually cover several topics, so a topic's share of them is smaller than their budgets.
- **After each run,** record each worker's tokens on the board, as the agent tool or the session reports them. Work out what a topic cost to reach the portal.
- **Compare that with the projection.** When a run's cost per topic is off by more than a third, project the rest of the guide again. Log what the run measured in the decision log.
- **Tell the owner early** when the projection passes what they said fits. Cut medium topics, or trade reviews for facts checks, before the budget runs out.

| Worker | Starting budget, in tokens |
| --- | --- |
| Topic worker | 250,000 to 300,000 per topic |
| Review worker | About 150,000 per topic |
| Facts check | About 50,000 per topic |
| Fix worker | 100,000 to 150,000 |

## When the owner is away

Decide what a careful colleague would decide. Log it in the decision log, with its reason and what would reverse it. Hold a question for the owner only when a wrong guess would waste a worker's run.

When you reach the owner, assume they've forgotten the build's details. Lead with what the guide now does differently, or with the decision you need. Leave out file names and IDs unless the point depends on one.

## What to watch

| Risk | Sign | Response |
| --- | --- | --- |
| The frame is wrong | A handoff says the context notes don't hold | Take it seriously. The notes are a first reading, and the evidence wins. Correct them and log it |
| A guess about the case hardens into a fact | A claim about the case without a provenance tag | The topic goes back |
| A private fact leaks in other words | Public text, a block title or a visual title that restates a private fact | The topic goes back, and the pattern goes into the next run picture |
| One explanation wins too early | The case's owners name several explanations, and a topic picks one | The topic goes back to weigh them all |
| An error in a source spreads | Two workers trip on the same error | Put the correction in the worker pack |
| Workers drift apart | One thing has two names, or two depths | Fix the glossary. Point new workers at the pilot topics |
| One concept, two homes | Two topics explain the same thing in full | Enforce the map's homes |
| Critical loses its meaning | Critical topics well past a third, or a cluster over its quota | Compare the critical items with each other, and propose demotions to the owner |
| Topics grow | A topic above its band | Split it, or move sections to the context rank |
| Visuals creep back | A visual without a job statement | It comes out |
| Fast facts go stale | A claim about a tool with no date | Date it |
| Reading lists return | A topic with many materials and no reasons | Cut to the ones with a stated reason |
| The load outgrows the hours | Total reading time past the owner's hours | Cut materials first, then medium topics |
| The cost outgrows the projection | A run's cost per topic off by more than a third | Project again, and tell the owner |

## If you're a new orchestrator

An earlier session might have run part of the build. To pick up:

1. Read `orchestration/board.md`.
2. Read `docs/decisions.md` from the top.
3. Read the handoffs in `orchestration/handoffs/`, newest first, starting with the last orchestrator handoff.
4. Read the last run's folder in `orchestration/briefs/`.
5. Check that the board matches what exists in `content/`, then rebuild the portal.
6. Run `git status`. A topic folder with changes and no handoff belongs to a worker that a stop cut off. Start a new worker on it with the same brief, and say the folder holds a partial draft.
