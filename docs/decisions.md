# Decisions

The decision log: every settled question, with what was decided, why, and what would reverse it. Read it before you reopen something that looks settled. Add an entry when a standard, the settings, the topic map or the plan changes.

The orchestrator owns this file. Workers propose entries in their handoff. When the owner confirms or changes something, that gets an entry too, in their words.

## How to write an entry

Group entries under a heading that dates the event that produced them, such as `## 2026-10-05: kickoff` or `## 2026-10-06: from the pilot reviews`. Add new groups at the bottom, so the log reads in order.

Each entry has four pieces:

1. **The ID and the decision,** in bold, as one sentence. The ID is `glossary.decision_prefix` from `guide.toml` (D by default) and a number. Numbers count up across the whole log and are never reused.
2. **What,** when the bold sentence needs detail: the values, the files, the topics it touches.
3. ***Why:*** the reason. Quote the owner when the decision is theirs. Name the evidence when it came from a check.
4. ***Reverse if:*** the observation that would undo it. Write "never" only for a rule the guide can't work without.

```markdown
**D4. Swarm control waits until the inspection topic is live.**
P02 builds on P01's inspection routine and links to it throughout.
*Why:* P02's starting questions assume the reader can already read a frame.
*Reverse if:* the swarm season starts before P01 is done.
```

**To cite a decision elsewhere,** write its ID in parentheses, such as (D4). The glossary page drops these references, and check 7 fails if one shows there.

**To reverse a decision,** add a new entry that says "Reverses D4" and why. Leave the old entry in place, and add "Reversed by D9." to the end of its bold sentence.

**To record the kickoff,** add one entry that names the assumptions in `docs/request.md` the owner confirmed and one entry for each one they changed.

## The log

None yet.
