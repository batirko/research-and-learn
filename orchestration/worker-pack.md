# Worker pack

The standing reading for every worker, on one page. It condenses `docs/request.md`, `docs/method.md`, `context/reader.md` and the five standards in `docs/standards/`. Read this instead of them, and open a standard only where this pack points you to it. When this pack and a standard disagree, the standard wins: say so in your handoff.

Here, "you" is the worker. Numbers are settings in `guide.toml`, given with their defaults; the section "This guide's settings" lists any this guide changed.

> **To fill this file.** The orchestrator fills the sections under "This guide" at kickoff, from `docs/request.md`, `context/reader.md` and the context notes, and deletes each "To fill" note. It refills them after the pilot review, and keeps the whole pack in step with the standards and the decision log. Change the line below each time.

**Last brought in step:** not yet.

## This guide

### The reader

> **To fill:** the reader's first name, what they're preparing for, and by when, in two or three sentences. Then the three or four facts from `context/reader.md` that change how a topic is written. Cover what they've studied, what a bridge can use, and how they read.

### The goal

> **To fill:** the goal's abilities, as the numbered list in `context/reader.md`. Every topic's "Why it matters" ties to at least one of them.

### The case

> **To fill:** the case in three or four sentences: the situation, who is in it, and what is known and unknown. Name the context notes that hold the detail. Write "No case" when the guide has none.

### This guide's settings

> **To fill:** each value in `guide.toml` that differs from a default this pack quotes, such as the tiers, `materials.per_topic` or the size bands. Write "All defaults" when none does.

## Hard rules

1. **No invented facts.** Every outside claim has a source you opened in this session. Every fact about the case has a provenance tag. An unknown is an open question, with its ID from `context/open-questions.md`.
2. **Evidence and interpretation stay apart.** The context notes are a first reading, made before anyone knew the case well. If the evidence contradicts a reading, the evidence wins. Say so in your handoff.
3. **Private stays private.** A private tag sits inside a private block. A block's label and a visual's title are public text. Nothing on `context/never-publish.md` enters a topic.
4. **One word per concept.** `context/glossary.md` is the list. Read it before you write.
5. **Prove you can reach the web before you start.** Fetch one page you need. If the fetch fails, stop and say so in your handoff.
6. **Write only the files your brief names. Don't run git.**

## Provenance tags

| Tag | Meaning | Private |
| --- | --- | --- |
| `[public]`, `[public](https://...)` | From a public page, linked next to the claim or in the tag | No |
| `[source: name]` | From a document in `context/sources/` | No |
| `[private: name]` | From a private source. Inside a private block only | Yes |
| `[inference]` | Reasoning from other facts. Say which facts | No |
| `[unverified]` | One weak source, or a memory. Never stated as fact | No |

> **To fill:** any tag this guide adds in `[[tags]]`, and the names of the sources from `context/sources/README.md`, with whether each is private.

`context/README.md` has the rest.

## Known errors in the frozen sources

The sources in `context/sources/` are frozen: nobody edits them, even to fix an error. When a worker's handoff names one, the orchestrator adds an entry here, under a heading for its source. An entry gives the place in the source, what it says, what is true, the evidence, and the decision that recorded it, such as (D12). Before you rely on a source, read its entries.

None yet.

## A topic's parts

Every part, in order, is in `docs/standards/topic-page.md`. The points writers miss:

- **Why it matters:** 2 to 4 public sentences (`limits.why_sentences`), tied to an ability in the goal, with evidence.
- **The short version:** 5 to 8 lines (`limits.short_lines`), each a claim, not a table of contents.
- **The explanation:** from zero. Explain the mechanism, what it costs and where it breaks. Close each concept with a "For your goal" sentence. A bridge to what the reader has done is optional and comes after the explanation.
- **Ranks:** every section has one, never above the topic's. Depth follows the rank: level 3 on a critical topic's critical sections, level 2 on high topics, level 1 to 2 on medium ones.
- **One home per concept:** if the topic map names another topic as a concept's home, link to it and add only what is yours.
- **The case part:** Known, with tags; Unknown, as open questions with likely answers; What to look at first. Don't guess about the case.
- **Not verified:** always present. "None." when empty.

The file format is `engine/format.md`.

## Size

Aim at the middle of the band your brief gives, and treat the top as a ceiling. Writers who aim at the band as a whole fill it to the top. The bands are `[sizes]` in `guide.toml`; the defaults:

| Size | Words |
| --- | --- |
| S | 800 to 1,500 |
| M | 1,500 to 2,500 |
| L | 2,500 to 3,500 |
| XL | 3,500 to 4,500, only when your brief grants it |

The build counts the explanation, the case part and the positions. Above the XL ceiling, a topic is two topics: propose the split in your handoff. A fix to a topic near its ceiling cuts before it adds.

## Materials

- At least one, at most `materials.per_topic` (5), in rank order.
- Critical: at most `materials.critical_per_topic` (1), or `materials.critical_per_critical_topic` (2) in a critical topic, inside your cluster's quota from the topic map. Each says what it gives that the guide can't, names its part, and names what it passed over.
- Open every material before you list it, and record the date.
- Record every candidate in your dossier, `research/<id>-<slug>.md`, kept or dropped with the reason. Quote the sentence each outside claim rests on.
- In a tier whose facts age fast, a material older than `materials.max_age_months` (18) needs a reason.

`docs/standards/sources.md` has the rest.

## Visuals

A visual exists only when it passes four checks. It has a job, written first. A first-time reader is better off with it. The subject has a shape. It can be drawn truthfully, with unknown parts drawn as unknown. Many topics have none.

A visual that places someone's claim draws the whole claim. `docs/standards/visuals.md` has the test, and `engine/format.md` has the drawing rules.

## Writing

- One idea per sentence. Aim under 25 words, and under 20 for anything the reader has to do.
- Active voice, present tense, the condition first, contractions.
- Certainty: must, a good default is, can, might. No bare "should". No guess written as a fact.
- In topic text, "you" is the reader, and the guide is "this guide". No first person.
- No em dashes, en dashes or double hyphens in prose. Never "simple", "easy" or "quick".
- Explain in plain words first, then give the name.

`docs/standards/writing.md` has the rest.

## Checks before you hand off

1. **The format check:** `python3 engine/topic.py content/<tier>/<id>-<slug>`. Zero errors.
2. **The lint:** `python3 tools/lint.py content/<tier>/<id>-<slug>`. Zero errors. Explain each warning you leave in your handoff.
3. **The slop pass:** the `no-ai-slop` skill in detect mode on your prose. Fix what it finds.
4. **The private search:** read every sentence outside a private block for a private fact in other words. Look too for a person or arrangement known only from a private source. Read every block label and visual title as public text.
5. **The size:** the format check prints the word count. Check it against your band.
6. **The starting questions:** each one answered, or replaced with a reason.

## Tokens

Report what your run used in your handoff, as the agent tool reports it. The orchestrator compares it with the projection, so the plan changes before the budget runs out.

## Your handoff

Leave it where your brief says. `orchestration/handoffs/README.md` has the shape. In short: what exists, what you couldn't verify, and your token use. Add what you propose for shared files, such as the glossary or the topic map, and any conflict between documents.
