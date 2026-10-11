# Porting record

This project is the generic, open-source version of a private working guide built on the same method. That guide logs every functional or structural addition in its own `docs/porting.md`, as entries named PORT-001, PORT-002 and so on. The contract at the top of that log is the agreement between the two projects: it writes the entries, and this file records what this project did with each one.

An entry is ported, adapted or skipped. Ported means the feature works here as it works there. Adapted means it was rebuilt to fit this engine: settings in `guide.toml`, no guide content in `engine/`, and nothing that assumes one subject or one reader. Skipped means it doesn't belong here, and the reason says why. Nothing here copies the other project's files.

## Where the next pass starts

Assessed through **PORT-005**. The next pass starts at PORT-006.

## The record

| Entry | What it is | Decision | Done in |
| --- | --- | --- | --- |
| PORT-001 | Concept map: each topic's key concepts, where each is explained and where it's used | Adapted | 2026-10-11 |
| PORT-002 | Reading progress on All topics, and a tier filter | Ported | 2026-10-11 |
| PORT-003 | A second "Mark as read" button at the end of each topic | Ported | 2026-10-11 |
| PORT-004 | The header hides as you scroll down and comes back as you scroll up | Ported | 2026-10-11 |
| PORT-005 | Concept index: one row per concept, and each row is a card | Ported, with PORT-001 | 2026-10-11 |
| No entry | The password-protected hosted copy, and notes synced through it | Skipped | 2026-10-11 |

## Notes on each entry

### PORT-001: adapted

The map, its index, the section that ends each topic page and check 9 work as they do there. What changed to fit this engine:

- **Tiers and words come from the settings.** The tier names, the tier filter and the rank labels read `guide.toml`, so a guide with two tiers or five gets the right map. The tier filter hides when a guide has one tier.
- **The data file and the limit are settings:** `paths.concepts` and `limits.concepts_per_topic`. The `--concepts` build flag wasn't ported: `--guide` already builds the test guide from its own files.
- **The lint checks the concept text.** The other project checked it for dashes inside check 9. Here `tools/lint.py` lints every name, definition and how line as prose, so the glossary's banned words, the spelling and the reader's name apply too.
- **The case's own nouns** in the rule on uses read from `case.terms` and the glossary, not from a list of names.
- **Added here: check 9 holds the glossary's homes.** A concept whose name or alias is a glossary term must have the glossary's home. This enforces "one home per concept", which the other project's check didn't test.
- **Added here: fingerprints of each topic's concept pass.** The other project names a known limit: when a topic changes, its uses go stale, and no check notices. Here the concept file keeps a fingerprint of each topic's text from its pass. The build and `engine/concepts.py` name every topic that changed since. Neither fails the build, because a changed topic can keep its concepts.
- **Added here: a topic no pass has read yet needs no concepts.** Guides here go live in waves, so check 9 asks for concepts only from topics a pass has read, or that already have some. The build names the topics still unread.
- **The method and the workflow.** `docs/method.md` gains "Key concepts" and a rule from experience. The playbook gains the concept pass, the concept worker and the ownership of the file. `orchestration/briefs/concepts.md` is a new template, with a filled example, because the other project didn't keep its briefs.

A known limit, not fixed: the ring has a minimum size, so a guide with a few topics draws a large map with much empty space. It reads correctly.

### PORT-002: ported

The tier buttons come from the settings, and they hide when a guide has one tier. The commit behind the entry also marks read topics in the All topics table, which the entry doesn't name. That came along, because the progress block counts those marks.

### PORT-003 and PORT-004: ported

The sticky panels here are the topic list, the contents, and the concept map's two panels. Each sits below the header.

### PORT-005: ported, with PORT-001

The index was built in its final form, so PORT-001's first version of the index never existed here.

### The hosted copy: skipped

The other project's log gives these two features no entry: the password-protected hosted copy, and the bookmarks, notes and read marks synced through it. Both depend on one hosting provider and on a guide with one reader. This project's portal opens from disk and keeps everything in the reader's browser, by design.
