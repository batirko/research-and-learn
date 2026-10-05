# The request

What the owner asked for, in their own words, and what the build assumed about it. When documents disagree, this one wins.

Status: template, not filled yet.

> **To fill this file.** The set-up skill fills it during the interview. Fill every section below in order, and delete each "To fill" note once its section holds the answer. Then change the status line above to "Status: filled at set-up on YYYY-MM-DD." After kickoff, the orchestrator adds the kickoff date and marks each assumption.
>
> Keep the owner's words as given, typing slips included, inside quotation marks. Put a cleaned version after them when the original is hard to read. Don't turn an answer into a requirement the owner didn't state; write it as an assumption instead.

## The request, as given

> **To fill:** the owner's request, word for word, with the date they gave it. If it came in several messages, keep each one and its date.

## The reader

> **To fill:** who the guide is for, in one or two sentences: their first name, and whether they are the owner. The detail goes in `context/reader.md`. The first name also goes in `guide.reader` in `guide.toml`.

## The goal

> **To fill:** what the reader must be able to do after reading, first in the owner's words, then as a numbered list of abilities. Each ability is something a person could watch the reader do. For example: "Sam can inspect a hive and say whether the colony has a laying queen." Every topic's "Why it matters" ties to at least one item, so keep the list short and concrete.

## The date and the hours

> **To fill:** the table below. "Reading days" counts from the expected end of kickoff to the date. "Reading hours" is days times hours a day. If the owner gave no hours, write the default you assumed and list it as an assumption.

| | |
| --- | --- |
| The date | |
| What happens on the date | |
| Hours a day for reading | |
| Reading days | |
| Reading hours in all | |

## The subject and the case

> **To fill:** the subject in one sentence. Then the case: the specific situation the guide prepares the reader for, such as a first season with one apiary and a local association. If the guide has no case, write "No case", and set `case.part` to `""` in `guide.toml`.

## The tiers, in the owner's words

> **To fill:** one row per tier. Keep the owner's words exactly. `guide.toml` holds a cleaned definition of each tier, and its `id`, `name` and `prefix`. The definitions don't change after set-up.

| Tier | The owner's words | Name and prefix in `guide.toml` |
| --- | --- | --- |
| | | |

## The sources

> **To fill:** what the owner gave: files placed in `context/sources/`, links, people the reader can ask. Mark each one public or private. `context/sources/README.md` lists the files and their tag names.

## What else the owner asked for

> **To fill:** any other preference, in the owner's words where they gave them. Cover length, visuals, language and spelling, privacy, who else will see the portal, and devices. Add any material they already want or don't. Write "Nothing else" when there was nothing.

## Assumptions to confirm at kickoff

> **To fill:** one row per assumption, with an ID that counts up from A1 and never gets reused. An assumption is anything the build will act on that the owner didn't say outright. Always cover these, even when the owner's answer seems clear:
>
> 1. The reading default: the reader reads the guide's text and critical materials in full, skims high and medium materials, and opens context ones when needed.
> 2. The hours a day, when the owner didn't give them.
> 3. The materials ceiling per topic, `materials.per_topic`.
> 4. The mode: lean, unless the owner chose full.
> 5. The language and spelling, `guide.language` and `guide.spelling`.
> 6. Private facts: collapsed in the portal, and what goes on the never-publish list.
> 7. Who sees the portal: the reader alone, on their own device, unless the owner said otherwise.
> 8. Whether the build can run unattended, and what will prompt for permission.
>
> The orchestrator fills the last column at kickoff: "Confirmed", or "Changed" with the decision's ID, such as "Changed, D3".

| ID | Assumption | Reason | If wrong | At kickoff |
| --- | --- | --- | --- | --- |
| A1 | | | | |
