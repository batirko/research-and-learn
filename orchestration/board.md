# The board

The status of every topic, and of the work around them. The orchestrator owns this file and is the only one that edits it. Workers report status in their handoffs.

The topic map says what each topic is. When a topic is added, cut or re-ranked there, change its row here in the same step.

<!--
How to fill this template:
- The scaffold fills "Topics" from the topic map, one row per topic, every status "planned". It marks pilot topics in Notes.
- The orchestrator fills the rest at kickoff and keeps it true after every handoff.
- Replace everything in {braces}. Delete the example rows and this comment once the board is filled.
-->

## Status words

| Status | Meaning |
| --- | --- |
| planned | In the map. Nobody has started |
| writing | A topic worker has it |
| check | The writer has handed off. A review or a facts check is running |
| fix | A check found points. A fix worker has them |
| live | The checks passed, and the topic is in the portal |
| held | It waits for something outside the build. Notes say what |

## Where the build stands

{Date. The phase and the mode. How many topics are live. What runs now, and what comes next. The newest orchestrator handoff.}

## Topics

| ID | Title | Tier | Rank | Size | Cluster | Status | Worker | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {B01} | {Title from the map} | {Base} | {critical} | {S} | {C1} | planned | | {pilot} |

Notes hold what the next worker needs: words after the last fix, the check the topic got, an XL grant, a reason it's held.

## Critical materials

Each cluster's quota is in the topic map. The quotas add up to `materials.critical_in_guide` in `guide.toml`. Add a row when a worker proposes a critical material. Mark it accepted when a check agrees.

| Cluster | Quota | Topic | Material | Time | Accepted |
| --- | --- | --- | --- | --- | --- |
| {C1} | {1} | {B01} | {Title} | {45 min} | {yes, by the review} |

**Used:** {n} of {materials.critical_in_guide}, {total time}.

## Cost

Tokens as the agent tool or the session reports them. The projection comes from the kickoff. Compare each run with it, and log a run that differs by more than a third in the decision log.

**Projection at kickoff:** {topics with a review} × {tokens} + {topics without} × {tokens} = {total}, before the scaffold and integration.

| Run | Date | Workers | Tokens | Topics that went live | Tokens per topic | Against the projection |
| --- | --- | --- | --- | --- | --- | --- |
| {run-01} | {date} | {n} | {tokens} | {n} | {tokens} | {within a third / over by n%} |

## Workers

One row per worker you start: a subagent or a session.

| Date | Run | Kind | Scope | Model | Tokens | State | Handoff |
| --- | --- | --- | --- | --- | --- | --- | --- |
| {date} | {run-01} | {topic worker} | {P01} | {model} | {tokens} | {handed off} | {`2026-10-05-topic-p01.md`} |

## Other work

| Item | Status | Notes |
| --- | --- | --- |
| Kickoff | {open} | {decision log entries} |
| Mode | {lean} | |
| Facts check of the context notes | | {Only when the guide has a case} |
| Pilot review | | {The owner's answers on depth, length, ranks, materials, visuals and design} |
| Tier maps | | {Drafted after the pilot, finished at integration} |
| Home page text | | |
| Open-questions page | | |
| Guide-wide review | | {Links against homes, glossary, ranks, the critical materials pass} |
| Glossary homes | | |
