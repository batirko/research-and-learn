# Glossary

One word per concept, across the whole guide. Two topics that name the same thing with different words are a defect.

Before you coin a term, check this list. To add or change a term, propose it in your handoff; the orchestrator edits this file. The portal's glossary page shows every row below, and the lint reads the "Don't use" column. Everything above the first `##` heading is for writers, and the page leaves it out.

**To fill this file.** The scaffold adds a `##` section for each area of the subject, with the terms the topic map already needs. Topic workers propose more as they write. Keep the section "This guide's own words" at the end: it explains the portal's words to the reader. Change a row there when the settings rename what it describes, and delete the row for the case when the guide has none.

**The shape the build reads.** Under each `##` heading, a table with exactly three columns, `| Use | Meaning | Don't use |`. Text under a heading outside a table shows on the page as a note, so write it for the reader.

- **Use:** the term in bold, as the guide writes it.
- **Meaning:** one or two sentences, for the reader. You can name the reader by first name; the page turns "Sam's hive" into "your hive".
- **Don't use:** the words the guide doesn't use for this concept, separated by commas. A plain word is banned everywhere, and the lint fails on it. A word in *italics* is banned in this row's sense only, and the lint warns, for a person to judge. A parenthesis after a word explains the ban, and the lint ignores it. Leave the cell empty when nothing is banned.

**Sentences the page treats differently,** in the Meaning column:

- "B01 is the home." names the topic that explains the concept. The page turns it into a link, and check 7 fails when the topic isn't in the topic map.
- A sentence that starts with a word in `glossary.bookkeeping`, such as "Added from P01.", is a note for writers. The page leaves it out.
- A decision reference such as (D4) is for writers too. The page drops it, and check 7 fails if one shows.
- A sentence with a private tag shows in a collapsed private block. So does a sentence that matches `privacy.glossary_source`, when the settings set it.

`engine/tests/fixture/context/glossary.md` is a small filled glossary. An example table, from the same guide on a first season keeping bees, where it sits under a heading such as "The colony":

```markdown
| Use | Meaning | Don't use |
| --- | --- | --- |
| **colony** | The bees that live together: one queen, thousands of workers and, in summer, drones. B01 is the home. | *hive* (for the bees) |
| **super** | A box above the brood where the bees store honey. Added from P01. | honey super |
| **brood** | Eggs, larvae and pupae, in their cells. Counted in frames, not cells (D4). Sam's mentor checks brood before anything else [private: mentor-call 08:15]. | |
```

## This guide's own words

| Use | Meaning | Don't use |
| --- | --- | --- |
| **topic** | One page of this guide. It explains one subject from the ground up, then lists a few ranked materials. | |
| **tier** | One of this guide's first-level groups of topics. Each tier answers one question, and its page opens with a map of its topics. | |
| **rank** | How much a topic, section or material matters for your goal: critical, high, medium or context. The home page says what each rank asks of you. | |
| **depth** | How far a topic takes you. At level 1 you can explain a concept in two sentences. At level 2 you can name the alternatives and why someone picks one. At level 3 you can say what a choice costs, where it breaks and what would change your mind. | |
| **material** | Something outside this guide to read, watch, hear or do. Each one has a rank and says what it gives you that this guide doesn't. | |
| **case** | The specific situation this guide prepares you for. A topic's "In your case" part holds what is known about it, what isn't, and what to look at first. | |
| **provenance tag** | The mark after a fact about your case that says where it came from, such as `[public]` or `[inference]`. Hover over one to see what it means. | |
| **private block** | A collapsed block that holds a fact from a private source. It opens when you select it, and search leaves it out. | |
| **open question** | Something nobody could settle when this guide was written. Each one has an ID, its likely answers and what would settle it. The open-questions page lists them all. | |
