# Context

What is known about the reader, the goal and the case. **Context notes** are the files in this folder. The guide is built on them: read the note you need before you research a topic, so you don't rediscover it.

The set-up skill and the scaffold skill write the first versions. After that, the orchestrator and context workers change them. Other workers propose changes in their handoff.

## The notes

| File | What it answers |
| --- | --- |
| `reader.md` | Who reads the guide, what they've done, and what that means for how you write |
| `glossary.md` | The one word to use for each concept. Check it before you coin a term |
| `open-questions.md` | What nobody can settle yet, with what would settle each question |
| `never-publish.md` | What must never reach the portal, even collapsed |
| `sources/` | The frozen sources: notes, transcripts, documents and saved pages the owner gave |

**Case notes** hold what is known about the case. Each one answers one question about it, and its name says which: `case.md` for the situation itself, or `association.md` for an organisation in it. Whoever writes a case note adds its row to the table above. A guide with no case has none.

## Every fact about the case carries its origin

A **provenance tag** after a fact says where it came from. A fact about the case without one is a defect, in these notes and in the guide. The tags come from `[[tags]]` in `guide.toml`. The defaults:

| Tag | Meaning | Private |
| --- | --- | --- |
| `[public]`, or `[public](https://...)` | From a public page. The link sits next to the claim, or in the tag | No |
| `[source: name]` | From a document in `sources/`. A place inside it can follow the name: `[source: club-handbook p. 4]` | No |
| `[private: name]` | From a private source, such as a conversation: `[private: mentor-call 12:40]` | Yes |
| `[inference]` | Reasoning from other facts. Say which facts | No |
| `[unverified]` | A single weak source, or a memory. Never state it as fact | No |

- **A name** is lowercase letters, digits and hyphens. `sources/README.md` lists each source's name.
- **A private tag sits inside a private block,** in a topic and on every page the portal shows. The portal keeps the block closed until the reader opens it.
- **To add a tag,** add a `[[tags]]` table to `guide.toml` with its form, its title and, for a private one, `private = true`. Say why in the decision log.

## Evidence and interpretation

These notes hold two kinds of statement.

- **Evidence** is what someone said, wrote or published, with a tag.
- **Interpretation** is what the scaffold or a worker made of it. It sits under a heading that says so, such as "Reading" or "Hypotheses", and carries `[inference]` where it sits next to evidence.

The scaffold writes its interpretation before anyone knows the case well. So it's a first reading. When research contradicts it, the evidence wins, and the worker says so in its handoff.

**A case note has this shape.** A first line says what the note answers. The evidence follows in sections, then the reading, then the open questions the note raises, by ID.

**A note about people** records what each person does in the case and what they expect, with tags. Personal details the reader doesn't need stay out. A detail that must never reach the portal goes on the never-publish list.

## Quotes

Clean a spoken quote of filler words and slips of the tongue, and nothing else. When the exact wording matters, read the source at its time stamp.

## Frozen sources

The files in `sources/` are frozen. Nobody edits them, even to fix an error.

- **When a worker finds an error in a source,** it says so in its handoff, with the evidence. The orchestrator adds the correction to the list of known errors in `orchestration/worker-pack.md` and to the decision log. Every later worker reads the correction there.
- **When a source has a newer version,** it goes in as a new file, with its own date. The old one stays.

## When a fact changes

1. Change the note, keep the tag, and add the date of the change.
2. If a written topic rests on the old fact, tell the orchestrator, which marks the topic for a fix on the board.
3. If the fact is still a guess, it belongs in `open-questions.md`, not in a note.
4. If the change settles an open question, move the question to "Settled" in `open-questions.md`. It keeps its ID.
