---
name: set-up
description: Starts a new guide in this workspace by interviewing the owner. Use when someone asks for help understanding or preparing for something by a date ("help me prepare for X by Y", "I sit an exam in March and need to understand X", "set up a guide"), or when docs/request.md still says it's a template. Writes guide.toml, docs/request.md, context/reader.md and context/never-publish.md, and saves the owner's sources in context/sources/.
---

# Set-up

You turn the owner's first message into a configured workspace. The **owner** is the person who runs the workspace. The **reader** is the person the guide is for, and is often the owner. After you, the scaffold skill researches the case and proposes the topic map.

## What you produce

- `guide.toml`: the settings.
- `docs/request.md`, `context/reader.md` and `context/never-publish.md`, each filled as its own instructions say.
- The owner's sources in `context/sources/`, listed in `context/sources/README.md`.

You don't research the subject, and you don't propose topics. The scaffold does both.

## Before you ask anything

1. Read `docs/request.md`. When its status line no longer says it's a template, a guide already exists. Ask the owner whether to adjust it or start over, and change nothing until they answer.
2. Read `guide.toml`, `context/reader.md`, `context/never-publish.md` and `context/sources/README.md`, including the instructions in each.
3. Read the owner's first message closely, and note every answer it already gives. Don't ask for those again.

## How to ask

- Ask two or three questions at a time, in plain words, the most important first.
- Give every question a default, and say what it is. "I don't know" takes the default.
- Every default you take becomes an assumption in `docs/request.md`, so the kickoff confirms it.
- Take an answer in any form. Keep the owner's words for the request, and turn them into settings yourself.
- Explain the method only when asked. One sentence of why per round is enough.
- The goal is the one answer without a default. Everything else has one, so finish within a few rounds.

## The interview

Ask in this order, and skip what the first message answered.

**1. The goal and the date.**

- What must the reader be able to do after reading? Ask for abilities someone could watch them use: "after one inspection, say whether the colony has a laying queen". The goal has no default. When the owner can't name it, draft two or three abilities from their message and ask them to correct the draft.
- By what date, and what happens on it? Default: four weeks from today.
- Who reads the guide? Default: the owner.

**2. The reader and the hours.**

- The reader's first name. Topic text speaks to the reader as "you", and the lint flags the name in a topic.
- What do they know already, in the subject and next to it? What have they done that a topic could build on? Default: they've heard of the subject and haven't studied it.
- How many hours a day can they read, and are there days with none? Default: one hour a day, every day until the date.

**3. The subject and the case.**

- The subject, in a phrase.
- Is there a case: one specific situation the guide prepares for, such as a job, a race, a move or an exam? What's known about it already? Default: no case.
- The names that come with the case: organisations, people, places. They go into `case.terms`, so the lint asks for a provenance tag where a topic names one.

**4. The sources.**

- What does the owner have: notes, transcripts, documents, saved pages, links, people the reader can ask? Default: nothing, and the scaffold works from public pages.
- Which of them are private, such as a conversation, a personal note or something given in confidence? Default: a conversation or a personal note is private, and a published document isn't.
- Ask the owner to put the files in `context/sources/`, or to paste them to you. Save pasted text as it was given, in a new file. Name each file as `context/sources/README.md` says: the name its tag will use, then a date. `mentor-call-2026-09-20.md` gives `[private: mentor-call 12:40]`.

**5. The tiers.** Show the three tiers in `guide.toml`, each with its question and definition.

- Do they fit the subject, or how would the owner split it? The owner can rename, redefine, add or drop a tier. Default: the three as they stand.
- Get the owner's own words for each definition. The definitions don't change after set-up.

**6. Language, privacy and the rest.**

- The language and spelling. Default: the language of the owner's messages, and its usual spelling. The portal's own labels are in English in this version.
- Is there anything that must never reach the portal, not even in a collapsed block? Examples: a remark made in confidence, a third person's private details, an address. Default: nothing.
- Who else will see the portal? Default: the reader alone, on their own device.
- Anything else: length, visuals, materials they already want or don't. Default: nothing else.

Don't ask about the mode or about unattended running. The request lists both as assumptions, and the kickoff settles them.

## Write the files

1. **The sources.** Check that each file is in `context/sources/` under its name and date, and add its row to the list in `context/sources/README.md`. From now on, nobody edits a source.
2. **`guide.toml`.** Fill these keys. The comments in the file explain each one.
   - `[guide]`: `title`, a short name for the guide. `language` and `spelling`. `reader`, the first name. `description`, one or two sentences on what the reader gets and by when.
   - `[[tiers]]`: one table per tier, with `id`, `name`, `prefix`, `question` and `definition`. The `id` is the tier's folder name, in lowercase. The `prefix` is one capital letter, different for each tier. Keep `updates` and `fast` on the tier that holds what today's tools change, if one does.
   - `[case]`: `terms`, the case's names. With no case, set `part = ""`.
   - `[portal]`: `storage_prefix`, a slug that no other guide on this machine uses. Pages opened from disk can share the browser's storage.
   - `[privacy]`: a writer might name a private source in a sentence, such as "the interview". Add a pattern for that name, as the comments there say.
   - Leave the sizes and the material limits as they are. The scaffold sets them against the hours.
3. **`docs/request.md`.** Fill it as its instructions say, with the owner's words in quotation marks. Its assumptions table covers the items its instructions list, and every default you took. Then change its status line from "template, not filled yet" to "filled at set-up on" and today's date, as its instructions say.
4. **`context/reader.md`.** Fill it as its instructions say.
5. **`context/never-publish.md`.** Add each term under its last heading, one list item per term. The build blocks every list item in this file. So write terms only as list items, and any explanation as a paragraph. Keep a term short enough to catch the fact without restating it. Put a regular expression, which starts with `re:`, in backticks. With nothing to block, leave the list empty.
6. **Check the settings.** Run `python3 engine/build.py`. A problem in `guide.toml` stops it at once, with a message that names the key; fix it and run again. Other failures come from files the scaffold hasn't filled yet, and you can leave them.

## Hand over to the scaffold

Tell the owner, in a few lines:

- what you recorded: the reader, the goal, the date and the hours, the case and the tiers;
- the defaults you took, which they confirm or change at kickoff;
- what happens next. The scaffold reads their sources and public pages about the case, and writes what is known and what isn't. It drafts a glossary and proposes a topic map sized to their hours, with a pilot of one topic per tier. They have nothing to do while it runs, and it ends with a few questions for them;
- that they can still add sources to `context/sources/` before the scaffold starts.

Then offer to start the scaffold.
