# Open questions

What nobody can settle yet about the case. Each question says what would settle it.

The guide uses this list twice. It keeps writers from stating a guess as a fact. And at integration it becomes the open-questions page, `content/questions.md`: the reader's list of things to find out.

**IDs are stable.** Cite a question by its ID, such as OQ-02, in a topic as `[[OQ-02]]`. An ID is never reused. A question that gets settled moves to "Settled" at the bottom and keeps its ID, so links to it still work.

**To fill this file.** The scaffold writes the first questions from its research on the case. After that, topic workers propose new ones in their handoff, and the orchestrator adds them with the next free ID. Questions about the subject in general don't belong here: a topic answers those from sources. A guide with no case can leave this list empty.

**The shape the build reads.** A question opens on its own line, in bold: the ID, a full stop, a space and the question, such as `**OQ-02. Does the association lend extractors?**`. The build reads only that line, for the question's ID and title. The ID's prefix is `map.question_prefix` in `guide.toml`, `OQ-` by default. `engine/tests/fixture/context/open-questions.md` is a small filled example. The opening line shows on the portal and in every link's tooltip, so keep private facts out of it.

**Group the questions** under `##` headings, by what the answer would change, most important first, such as "Priority 1: what changes the plan". When `map.question_groups` is set, such as to `Priority`, only questions under a `## Priority N: ...` heading count.

**Under each opening line,** write these, in this order:

1. **Why it matters:** which part of the goal or which decision waits on it.
2. **Likely answers:** the two or three most likely, and what each would mean for the reader.
3. **What would settle it:** a document to read, a person to ask, a thing to try.
4. **Touches:** the topics that cite it, as `[[ID]]` links.
5. **Evidence so far,** with provenance tags. A private fact here keeps its private tag. The build never reads a question's body, but `content/questions.md` shows what it copies from here, and there a private fact sits in a private block.

**Using a question in a topic.** State it in the topic's case part, under "Unknown", with its ID. Give the likely answers and what each would mean. Never fill the gap with a plausible guess written as fact.

## Settled

None yet.
