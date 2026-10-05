<!-- Example. A filled facts-check brief for the engine's test guide, a first season keeping bees, in engine/tests/fixture/. It belongs to the run in example-run-picture.md. Its run, dates and findings are invented. Copy the shape, and write your own content. -->

# Brief: facts check, run 2

## Goal

Check every claim about the case in two new topics: B02 The beekeeping year and P02 Swarm control. Neither gets an independent review, so this check is the only one their facts get. A wrong month or a wrong rule of the association could cost Sam a colony, or a place at the teaching apiary. That's why this check exists.

**P02 is still being written when you start.** Check B02 first, and write its findings. Don't open P02's folder until the orchestrator says it's finished. If you finish B02 before then, write your handoff for B02, say P02 is pending, and stop. The orchestrator resumes you for P02.

The check is done when every tagged claim, and every untagged sentence that states something about Sam's apiary or the association, has a verdict. The findings are ranked, most serious first, ready for a fix worker.

## What to check

- **Every provenance tag.** Does the source say it, on the page or at the time the tag gives, with that strength? Search the handbook and the mentor call at the cited words instead of reading them whole. A speaker's hedge that went missing is a finding.
- **Untagged statements about the case.** Each needs a tag, or an open question's ID.
- **Private facts outside private blocks,** including the mentor's advice restated in other words. Block titles and visual titles count as public text.
- **The never-publish list.** Nothing on it appears anywhere.
- **The known errors** in the worker pack, including the handbook's two development times for a queen.
- **Open-question IDs.** Each one cited exists, and asks what the sentence says it asks.

Don't judge the writing, the general claims about bees, or the materials. That isn't this check.

B02 rests on the handbook's calendar: check every month it gives for the association's apiary. P02 will likely quote the mentor on queen cells: each quote sits in a private block, word for word, with the hedge.

## Model and budget

You run on a smaller model. Your budget is about 100,000 tokens, about 50,000 per topic.

Before you start, fetch one public page a topic cites. If the fetch fails, say so, and compare public claims with the writer's dossier instead.

## Read before you start

1. `AGENTS.md`
2. The run picture: `orchestration/briefs/run-02/picture.md`.
3. `orchestration/worker-pack.md`: the tags, the hard rules and the known errors.
4. `reviews/facts-2026-10-05-context-notes.md`: the facts check of the context notes before the pilot. Copy its form.
5. `context/README.md`, `context/open-questions.md`, `context/never-publish.md` and `context/association.md`.
6. The handbook and the mentor call in `context/sources/`, by search.
7. `content/base/b02-the-beekeeping-year/` and `content/practical/p02-swarm-control/`, and their writers' handoffs.

## Fixed

- Write each finding into the file as you go, so a stop loses nothing.
- Don't edit the topics. Don't run git or the build.

## What you own

- `reviews/facts-2026-10-06-b02-p02.md`
- `orchestration/handoffs/2026-10-06-facts-run-02.md`

## Hand back

The review file and the handoff. Finish with a short summary for someone who wasn't watching:

- the claims checked, and the findings, per topic;
- the most serious findings;
- anything in a context note that the evidence contradicts;
- the tokens you think you used.
