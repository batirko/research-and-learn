# Standard: a topic

What every topic contains, how deep it goes, and when it's done. This standard fixes the content. `engine/format.md` is the file format that encodes it, and this page doesn't restate the format. When the two disagree, this standard wins; say so in your handoff.

Here, "you" is the topic worker who writes a topic or the review worker who checks it. Part headings are the defaults from `[parts]` and `[case]` in `guide.toml`.

## The parts, in order

| # | Part | What it holds | Required |
| --- | --- | --- | --- |
| 1 | **Header** | ID, title, tier, rank, size, depth, the topics to read first, the date you checked the facts. The build adds the reading time | Yes |
| 2 | **Why it matters for your goal** | Two to four sentences, with the evidence | Yes |
| 3 | **The short version** | A few lines the reader can keep in their head | Yes |
| 4 | **Explanation** | The guide's own explanation, from the ground up, in ranked sections | Yes |
| 5 | **In your case** | What is known about the case, tagged. What is unknown. What to look at first | When the guide has a case |
| 6 | **Positions** | A stance worth holding, where a real debate exists | When it applies |
| 7 | **Materials** | The ranked list of outside materials. At least one | Yes |
| 8 | **Not verified** | What you couldn't confirm | Yes, even when empty |
| 9 | **Check yourself** | Questions at the topic's depth | Optional |

Visuals sit inside parts 4 and 5, where they do their job. `visuals.md` decides whether one exists.

## Part 2: why it matters for your goal

`context/reader.md` lists what the goal asks of the reader. Tie the topic to at least one item, and give the evidence. Write `limits.why_sentences` public sentences: 2 to 4 by default.

If you can't tie the topic to the goal, say so in your handoff. The topic might not belong.

## Part 3: the short version

Write `limits.short_lines` lines, 5 to 8 by default. Each line is a claim the reader can keep in their head. A line that only lists what the topic covers is a table of contents.

## Part 4: the explanation

**Start from zero.** Assume the reader has heard the word and nothing more. Define each term at first use, or link to the topic that defines it.

**Explain the mechanism.** Say how the thing works, what it costs and where it breaks. A list of vocabulary isn't an explanation.

**Close each concept with its consequence.** One sentence on what it means for the reader's goal, after the `parts.consequence` lead-in ("For your goal").

**Bridge, briefly.** After the explanation, you can add one sentence that links the concept to something the reader has done, after the `parts.bridge` lead-in ("Bridge"). `context/reader.md` lists what they've done. A bridge never replaces the explanation.

**One home per concept.** `curriculum/topic-map.md` names the home of each concept that several topics touch. If your topic isn't the home, link to the home by ID and add only what is specific to your topic. Workers can't see each other's drafts, so this rule is what stops two topics from explaining one concept twice.

**Rank every section.** Each section carries one of the four ranks.

- No section ranks above its topic. A high topic has no critical section.
- A context section holds background the reader can skip without losing the thread.
- When more than half of a critical topic sits in context sections, it's two topics, or it's too long.

**Headings say something.** "Workers change jobs as they age, and the colony runs on that schedule" tells the reader more than "Worker roles".

## Depth

| Level | The reader can |
| --- | --- |
| 1 | Explain the concept to someone new in two sentences |
| 2 | Name the alternatives and say why someone picks one |
| 3 | Say what a choice costs, where it breaks, and what evidence would change their mind |

| Topic rank | Depth to reach |
| --- | --- |
| Critical | Level 3 on its critical sections, level 2 elsewhere |
| High | Level 2 |
| Medium | Level 1 to 2 |
| Context | Level 1 |

The header's `depth` is the deepest level the topic reaches.

**Level 3 goes where the reader decides.** Where the reader makes the choice, level 3 covers the mechanism itself. Where someone else makes it, level 3 covers what that choice costs the reader and when it would change their plans. A beekeeper decides when to add a box to a hive, so that topic explains the mechanism in full. A beekeeper doesn't build hive scales, so that topic explains what a scale's readings show and where they mislead, not the electronics inside.

## Part 5: the case part

The case is the specific situation the guide prepares the reader for. When the guide has none, `case.part` is empty and this part leaves every topic.

The part has three blocks, always in this order.

1. **Known.** Facts about the case, each with a provenance tag. A fact from a private source sits in a private block.
2. **Unknown.** The open questions that touch this topic, by their IDs from `context/open-questions.md`. Give the likely answers and what each would mean for the reader.
3. **What to look at first.** What to look at, whom to ask and what to try, early in the case. The lint holds sentences here to `limits.sentence_words_action` (30) words.

**Don't guess about the case.** "Your association probably lends extractors" is a defect. "Whether your association lends extractors is unknown [[OQ-02]]. Ask the secretary before you buy one" is fine.

**Treat the context notes as a first reading.** They keep evidence apart from interpretation, and the interpretation came before anyone knew the case well. When your research contradicts a reading, the evidence wins. Weigh both in the topic, and say so in your handoff.

**Weigh every explanation your sources give.** When your sources give several explanations for the same thing, the topic weighs all of them. It doesn't pick one before the evidence does.

## Part 6: positions

Use this part when practitioners disagree and the reader will have to take a side. Each position has a heading that states it and the three fields in `parts.position_fields`:

- **Why hold it:** the reasoning and the evidence.
- **The strongest case against:** stated fairly.
- **What would change it:** the observation that would make the reader drop it.

A topic holds at most `limits.positions` (3). Many topics have none. Keep opinions out of the explanation. An opinion the reader must weigh goes here, with its reasoning and the case against it.

## Part 7: materials

At least one, ranked, in rank order. `sources.md` decides what qualifies and how it ranks.

## Part 8: not verified

List what you couldn't confirm: a claim that rests on one weak source, a page you couldn't open, an exercise step you couldn't run. Write "None." when the list is empty. The part is always present, so "None." tells the reviewer you checked.

## Part 9: check yourself

Up to `limits.check_questions` (5) questions. Each tests the topic's depth, and the topic answers it. A question that only asks the reader to recall a term tests level 1, whatever the topic's depth.

## Topics in a tier that updates others

A tier with `updates = true` in the settings holds topics that say what today's tools change.

- The header names the topics this one updates, and says what it covers: the problem, the solutions or both.
- With both, the explanation splits into two halves, each with its own ranked sections.
- Each half says what changed, against the topic it updates. It doesn't explain the updated topic again.

A tier with `fast = true` holds facts that age fast.

- Date each fact that will age: "as of October 2026".
- Materials carry a year and a month. A material older than `materials.max_age_months` (18) needs a stated reason.
- Give the topic a `check again` date when it rests on something that changes monthly.

## Size

The topic map gives each topic a size. The bands are in `[sizes]`; the defaults:

| Size | Words | Who decides |
| --- | --- | --- |
| S | 800 to 1,500 | The topic map |
| M | 1,500 to 2,500 | The topic map |
| L | 2,500 to 3,500 | The topic map |
| XL | 3,500 to 4,500 | The orchestrator, in your brief, before you write |

- The build counts the explanation, the case part and the positions. Reading time is words divided by `sizes.words_per_minute` (220).
- **Aim at the middle of the band,** and treat the top as a ceiling. Writers who aim at the band as a whole fill it to the top.
- **XL is an exception.** The orchestrator grants it to a topic unique in how critical it is and what it carries. The guide has at most `sizes.xl_allowed` (5). You can ask for XL in your handoff. You can't take it.
- **Above the XL ceiling, a topic is two topics.** Propose the split in your handoff.
- **A fix to a topic near its ceiling cuts before it adds.**

## Done means

A topic is done when all of these hold.

1. It answers its starting questions from the topic map. Where you replaced or dropped one, your handoff says which and why.
2. A reader new to the subject can follow it without opening a material.
3. Every term is defined or linked, and matches `context/glossary.md`.
4. Every section has a rank no higher than the topic's, and the depth matches the rank.
5. Every fact about the case has a provenance tag. No guess is written as a fact.
6. Every outside claim has a source that the session opened.
7. The materials follow `sources.md`, and there is at least one.
8. Each visual passed `visuals.md`, or there is none.
9. The text follows `writing.md` and has had its slop pass.
10. The size fits its band.
11. No private fact shows in public text, restated or not.
12. The format check and the lint pass, and the checks the run's mode calls for have passed. `orchestration/playbook.md` says which.

## How a reviewer checks

1. **Read it once as the reader.** Come to it new to the subject, with no material open. Note each place you got lost, and each passage that's hard to follow where a visual might help.
2. **Run the scripts.** `python3 engine/topic.py <topic folder>` is the format check. `python3 tools/lint.py <topic folder>` is the lint. An error is a finding. A warning is a finding unless the handoff explains it.
3. **Walk the "Done means" list,** item by item.
4. **Check the case facts.** Compare each tagged claim with its source, by searching the source for the cited line. An independent review does this in full; without one, the facts check does.
5. **Search the public text for private facts.** Read every sentence outside a private block for a private fact in other words. The lint helps only where `privacy.source_words` names the words that point at a private source, such as "the call". Read every private block's label and every visual's title as public text, because the portal shows them on a closed block.
6. **Write findings as you go,** into the review file that `reviews/README.md` describes, so a stop loses nothing.
