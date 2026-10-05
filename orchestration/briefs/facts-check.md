# Brief: facts check, {run or scope}

## Goal

Check every claim about the case in {these topics | these pages}: {IDs or paths}.

{When none of them gets an independent review: This check is the only one their facts get.} A wrong fact about the case costs the reader in the case. That's why this check exists.

{When a topic is still being written: check the others first, and write their findings. Don't open that topic's folder until the orchestrator says it's finished.}

The check is done when every tagged claim, and every untagged sentence that states something about the case, has a verdict. The findings are ranked, most serious first, ready for a fix worker.

## What to check

- **Every provenance tag.** Does the source say it, where the tag says, with that strength? Search the source at the cited words instead of reading it whole. A speaker's hedge that went missing is a finding.
- **Untagged statements about the case.** Each needs a tag, or an open question's ID.
- **Private facts outside private blocks,** including a private fact restated in other words. Block titles and visual titles count as public text.
- **The never-publish list.** Nothing on it appears anywhere.
- **The known errors** in the worker pack.
- **Open-question IDs.** Each one cited exists, and asks what the sentence says it asks.
- **Public pages about the case,** tagged `[public]`. Open them.

Don't judge the writing, the general claims or the materials. That isn't this check.

{Anything about one topic that needs extra care, and why.}

## Model and budget

You run on {a smaller model}. Your budget is about {tokens} tokens: about 50,000 per topic.

Before you start, fetch one public page a topic cites. If the fetch fails, say so, and compare public claims with the writer's dossier instead.

## Read before you start

1. `AGENTS.md`
2. The run picture: `{orchestration/briefs/run-NN/picture.md}`.
3. `orchestration/worker-pack.md`: the tags, the hard rules and the known errors.
4. {The last facts check's file in `reviews/`, if one exists. Copy its form.}
5. `context/README.md`, `context/open-questions.md`, `context/never-publish.md`, and the context notes as you need them.
6. The sources in `context/sources/`, by search.
7. The topics, and their writers' handoffs. Each handoff names what its writer couldn't verify.

## Fixed

- Write each finding into the file as you go, so a stop loses nothing.
- Don't edit the topics. Don't run git or the build.

## What you own

- `reviews/facts-{date}-{ids}.md`
- `orchestration/handoffs/{date}-facts-{scope}.md`

## Hand back

The review file and the handoff. Finish with a short summary for someone who wasn't watching:

- the claims checked, and the findings, per topic;
- the most serious findings;
- anything in a context note that the evidence contradicts;
- the tokens you think you used.
