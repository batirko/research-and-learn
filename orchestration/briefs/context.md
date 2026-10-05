# Brief: context worker, {scope}

## Goal

Check and extend what is known about the case: {the scope of this visit}.

{Examples of a scope:

- check every link in one context note;
- record what a body in the case published after a date;
- find out what a name in the sources refers to;
- settle an open question that a public page can answer.}

## Why

The topics about the case rest on the context notes. The scaffold wrote them as a first reading, and some of it is tagged `[inference]` or `[unverified]`. A wrong fact here spreads into every topic that cites it. {Which topics wait for this visit, and why now.}

## Model and budget

You run on {the strongest model}. Your budget is about {tokens} tokens.

Before you start, fetch one page in scope. If the fetch fails, stop and say so in your handoff.

## Read before you start

1. `AGENTS.md`
2. The run picture: `{orchestration/briefs/run-NN/picture.md}`.
3. `context/README.md`: the provenance tags, and how a note keeps evidence apart from interpretation.
4. The context notes in scope.
5. `context/open-questions.md` and `context/never-publish.md`.
6. {The sources to search.}

## Fixed

- {Public sources only. | The private sources named here, and public ones.} Nothing behind a login the owner doesn't have.
- Every fact gets a provenance tag, and a public fact gets its link.
- Open the page. A search snippet doesn't confirm anything.
- Sources are frozen. To keep what a page says today, add a new dated file to `context/sources/`, and its row to the list in `context/sources/README.md`. Never change an old file.
- Record what a source says. Label what you make of it, apart.
- When the evidence contradicts a note, the evidence wins. Correct the note, and say so in your handoff.
- When the people who own the case give several explanations for one thing, record all of them.

## Yours to decide

Where to look, and in what order.

## What you own

- {The context notes assigned.}
- New files named `context/sources/{name}-{date}.md`, and their rows in `context/sources/README.md`.
- `orchestration/handoffs/{date}-context-{scope}.md`.

Propose new open questions and glossary terms in your handoff. The orchestrator owns both files. Don't run git or the build.

## Hand back

The updated notes, with the date of each change, and the handoff. The handoff says what changed, and which topics it affects. It also says what stayed unknown. A public source can't answer most questions about a case, and saying so is a result.

Finish with a short summary for someone who wasn't watching:

- what changed;
- what stayed unknown;
- the tokens you think you used.
