# Standard: sources and materials

How to find, check, rank and cite what lies outside the guide. A **material** is an outside thing the reader might read, watch, hear or do. A **source** is anything a topic rests on.

Here, "you" is the worker who picks or checks a source. The limits are settings in `[materials]` in `guide.toml`, given here with their defaults.

## Two uses of a source

1. **Evidence** for a claim in the explanation. It sits inline, as a link next to the claim.
2. **A material** in the topic's list. It is worth the reader's time in itself.

The same page can be both. Everything below covers both uses, and the ranking rules cover materials only.

## Check before you cite

1. **Open every link in the session that cites it.** A link from memory, from a search snippet or from an earlier document doesn't count until you've opened it.
2. **Check four things:** the page exists, it says what you claim, who wrote it, and when.
3. **Record the date you checked it,** in the material's `checked` field and in the dossier.
4. **Quote the sentence the claim rests on,** in the dossier. Then a reviewer who can't reach the web can still check the claim.
5. **If a page is gone,** look for an archived copy. If there is none, drop the source and the claim that rested on it.

If you can't reach the web at all, stop and say so in your handoff. A topic written from memory fails rule 1 on every link.

The seeds in the topic map are leads. Nobody has checked them.

## Prefer first-hand sources

In this order:

1. **The origin:** the paper, the specification, the book by the person who coined the idea, the account by the people who did the work.
2. **A practitioner's account with numbers:** what a named person or group did and measured.
3. **A good explainer:** a clear teaching piece by someone with standing in the field.
4. **Vendor content:** allowed when it's the best explanation there is. Mark it with `vendor: yes`.

Don't use content farms, unattributed listicles or machine-written summaries.

## Numbers

- A number needs a primary source, a unit and a date.
- When the only source is a vendor or a single practitioner, say so, and tell the reader to trust the shape and not the figure.
- When no credible number exists, say that, so the reader doesn't go looking for one.

## Ranking a material

Ask five questions.

1. **Does it serve the goal?** A famous piece on a neighbouring subject ranks below a plain piece on this one.
2. **Is it first-hand?**
3. **What does it add?** If the explanation already carries its content, the material ranks lower, however good it is.
4. **Is it worth the time?** A three-hour video needs a stronger case than a ten-minute article.
5. **Is it current?** In a tier whose facts age fast, a material older than `materials.max_age_months` (18) needs a stated reason.

Then give it a rank. The right-hand column restates `ranks.*.material` from the settings.

| Rank | It means | The reader will |
| --- | --- | --- |
| Critical | The reader needs the original, and the guide can't stand in for it | Read or watch the named part in full |
| High | A skim clearly pays: it adds proof, depth or a second voice on something the goal depends on | Skim it, 10 to 15 minutes |
| Medium | A skim pays a little: useful, and the reader would lose little without it | Skim it faster, about 5 minutes |
| Context | For reference or completeness | Open it when needed |

## Critical materials are picked with care

- **Per topic:** at most `materials.critical_per_topic` (1), or `materials.critical_per_critical_topic` (2) in a topic that is itself critical.
- **Per cluster:** each cluster has a quota in the topic map. The quotas add up to `materials.critical_in_guide` (30). Stay inside yours.
- **Justify each one.** In `what you get`, write what the original gives that the explanation can't. That might be the full argument, the data, a worked example, or the author's voice on a contested point.
- **Name the part.** A book is critical only by chapter.
- **Name what you passed over,** in `passed over`: the obvious alternative and why this one won.
- **Prefer short.** Between two good candidates, the shorter one is critical and the longer one is high.

A topic with no critical material is normal. But writers judge one cluster at a time and pick too few. So integration compares the strongest high materials across the whole guide, and promotes the ones the reader needs in the original.

## How many

At least one material per topic, and at most `materials.per_topic` (5). The orchestrator can lower the ceiling from the reader's hours.

Every material has a rank, context ones included. Keep context materials to the few the reader might open. A long list is a failure of selection.

## Exercises

A hands-on task is a material of type `exercise`. An exercise:

- runs with free tools, when `materials.exercises_free` is true, as it is by default;
- states its time, its steps in outline, and what the reader learns by doing it;
- uses no private data and nothing the reader can't get on their own.

An exercise's rank says what doing it pays, and its time says what it costs. A high exercise is worth doing however long it takes. Run the exercise yourself before you list it, or say in "Not verified" which steps you couldn't run.

## Quoting

Summarise in your own words. Quote only when the exact wording matters, and keep a quote short. Don't reproduce long passages, figures or tables from a source.

## Sources about the case

- **The sources folder,** `context/sources/`, holds the documents the owner gave, frozen. Cite one with its tag, `[source: name]` or `[private: name]`. `context/sources/README.md` lists them and their tag names.
- **A public page about the case** carries a `[public]` tag with its link. Pages about the case can change or vanish, so record what the page said, and when, in your dossier.
- **When a frozen source is wrong,** don't edit it. Say so in your handoff, with the evidence. The orchestrator adds the correction to the worker pack's list of known errors and to the decision log, so every later worker sees it.

## Where candidates are recorded

Each topic has a dossier in `research/`. Record every candidate there with a verdict: kept, with its rank, or dropped, with the reason. The next session then knows what was already considered. `research/README.md` has the shape.

## The material entry

`engine/format.md`, section "Materials", lists every field and which ones are required. The material types are `materials.types` in the settings.

## How a reviewer checks

1. Open every material, and a sample of the inline evidence. Check the four things in "Check before you cite".
2. Check the limits: the count per topic, the critical count per topic, and the cluster's quota in the topic map.
3. For each critical material, read `what you get` and `passed over`. If the explanation already gives what the material claims to give, it isn't critical.
4. In a tier whose facts age fast, check each material's date against `materials.max_age_months`.
5. For an exercise, check that the steps run with what the reader has, or that "Not verified" names the steps that weren't run.
