# The topic file format

You write a topic in a plain text file that a person can edit and a script can build the portal from. This page says how. `docs/standards/topic-page.md` says what a topic contains; when the two disagree, the standard wins.

The headings below are the defaults. Your guide's `guide.toml` can rename every part, the case part's blocks, the lead-ins and the position fields, so check its `[parts]` and `[case]` tables before you write. The worked examples are the topics of the test guide in `engine/tests/fixture/content/`.

## In five lines

1. A topic is a folder, `content/<tier>/<id>-<slug>/`, that holds `topic.md` and any `.svg` visuals.
2. `topic.md` opens with a header of `key: value` lines between two `---` lines.
3. Each part is a `#` heading with a fixed name. Ranked things are `##` headings that end in `{critical}`, `{high}`, `{medium}` or `{context}`.
4. A private fact goes inside a `:::private` block. A visual is a `:::visual fig-name.svg` block. Link a topic as `[[B04]]` and an open question as `[[OQ-02]]`.
5. To check the file, run `python3 engine/topic.py content/<tier>/<id>-<slug>`. Zero errors means the build can read it.

## One topic is one folder

```
content/
  base/b01-how-a-colony-works/
    topic.md
    fig-brood-timeline.svg
  practical/p01-inspecting-a-hive/
    topic.md
```

- The folder name is the topic ID in lowercase, a hyphen and a short slug. It starts with the ID, such as `p01-`.
- The tier folder is the tier's `id` from `guide.toml`, and it matches the ID's prefix letter.
- The text is always in `topic.md`. A topic without a visual is a folder with one file.
- A visual's `.svg` file sits in the folder of the topic that uses it.

## The file at a glance

Every part, in the only order the build accepts.

```markdown
---
id: P01
title: Inspecting a hive
tier: practical
rank: critical
size: S
depth: 3
cluster: C2
read first: B01
checked: 2026-10-05
---

# Why it matters for your goal

Two to four sentences, with the evidence.

# The short version

- Five to eight lines a reader can keep in their head.

# Explanation

## A heading that says something {critical}

Text. `###` subheadings can sit inside a section.

## Another heading that says something {context}

Text.

# In your case

## Known

## Unknown

## What to look at first

# Positions

## The position, stated as a heading

**Why hold it.** ...

**The strongest case against.** ...

**What would change it.** ...

# Materials

## The material's title {high}

- link: https://...
- by: ...

# Not verified

- One claim per line, or "None."

# Check yourself

1. Up to five questions.
```

`# Positions` and `# Check yourself` are optional. `# In your case` exists only when the guide has a case: set `case.part` to `""` in `guide.toml` and the part leaves every topic.

## The header

Each line is `key: value`. A list is comma-separated, and brackets around it are optional. Don't quote values.

| Key | Required | Value |
| --- | --- | --- |
| `id` | Yes | The tier's prefix letter and two digits: `B04`, `P01` |
| `title` | Yes | The title from the topic map, in sentence case. A colon is fine |
| `tier` | Yes | The tier's `id` from `guide.toml`, such as `practical`. It matches the ID's letter |
| `rank` | Yes | `critical`, `high`, `medium` or `context`, from the topic map |
| `size` | Yes | `S`, `M`, `L` or `XL`, from the topic map |
| `depth` | Yes | `1`, `2` or `3`: the deepest level the topic reaches |
| `cluster` | Yes | The cluster from the topic map, such as `C2` |
| `read first` | Yes | Topic IDs to read before this one, or `none` |
| `checked` | Yes | The date you last checked the facts, such as `2026-10-05` |
| `updates` | In a tier that updates others | The IDs of the topics this one updates |
| `covers` | In a tier that updates others | `problem`, `solutions` or `both`: what today's tools change |
| `check again` | When it applies | A date. Use it when the topic rests on something that changes monthly |

A tier updates others when `guide.toml` gives it `updates = true`. In the default settings that is the Modern tier.

Don't write the reading time or the word count. The build counts them, so they never drift.

### Sizes

The scripts check the word count against the bands in `guide.toml` (`[sizes]`). The defaults:

| `size` | Words | Who decides |
| --- | --- | --- |
| `S` | 800 to 1,500 | The topic map |
| `M` | 1,500 to 2,500 | The topic map |
| `L` | 2,500 to 3,500 | The topic map |
| `XL` | 3,500 to 4,500 | The orchestrator, in your brief, before you write. An exception |

- Write the size the topic map gives. Write `XL` only when your brief grants it.
- Aim at the middle of the band. The top is a ceiling, not a target.
- Outside the band, the format check and the lint warn. Above the XL ceiling, the lint fails: the topic is two topics, so propose the split in your handoff.
- The build counts the explanation, the case part and the positions.

## The parts

Each part is a `#` heading with exactly its name, in this order. The names are the defaults from `guide.toml`.

| Part | Heading | Required | What goes under it |
| --- | --- | --- | --- |
| 2 | `# Why it matters for your goal` | Yes | Paragraphs. No headings |
| 3 | `# The short version` | Yes | One bulleted list of five to eight lines |
| 4 | `# Explanation` | Yes | Ranked `##` sections only. No text before the first `##` |
| 5 | `# In your case` | When the guide has a case | Exactly `## Known`, `## Unknown`, `## What to look at first`, in that order |
| 6 | `# Positions` | No | One `##` per position, three at most |
| 7 | `# Materials` | Yes | One `##` per material, in rank order |
| 8 | `# Not verified` | Yes | A bulleted list, or the single line `None.` |
| 9 | `# Check yourself` | No | A numbered list of up to five questions |

Part 1 is the header.

**A topic that covers both halves.** In a tier that updates others, a topic with `covers: both` replaces `# Explanation` with two parts: `# Explanation: the problem`, then `# Explanation: the solutions`. Each holds its own ranked sections. With `covers: problem` or `covers: solutions`, write a single `# Explanation`.

## Sections and ranks

A section of the explanation is a `##` heading that ends in its rank in braces:

```markdown
## Workers change jobs as they age, and the colony runs on that schedule {high}
```

- The rank is `{critical}`, `{high}`, `{medium}` or `{context}`.
- No section ranks above its topic. A high topic has no critical section.
- Inside a section, use `###` for subheadings. They take no rank. Don't use `####`.
- The build makes the anchor from the heading text, so a heading that says something also makes a readable link.

Two lead-ins mark the paragraphs a reader skims for. Both are optional.

```markdown
**For your goal.** One sentence on what this concept means for the reader's goal.

**Bridge.** One sentence that links the concept to something the reader has done.
```

The build styles them, so a reader can scan a section's consequences. Use them where the topic standard asks for a consequence or a bridge.

## Links and tags in the text

| You write | It means | The portal shows |
| --- | --- | --- |
| `[[B04]]` | A link to topic B04 | The topic's ID and title, linked. A topic not written yet links to its plan |
| `[[OQ-02]]` | An open question | The question's ID, linked to its place on the open-questions page |
| `[text](https://...)` | An ordinary link, for evidence next to a claim | A link |
| `[public](https://...)` | A provenance tag that carries its source | A tag that links to the source |
| `[source: club-handbook p. 4]` and the other tags | A provenance tag | A tag, styled by kind, with its meaning on hover |

To link with your own words, put them after a vertical bar: `[[B04|how a colony splits]]`. Inside a table, escape the bar: `[[B04\|how a colony splits]]`.

Link to topics that don't exist yet. The build reads every ID and title from the topic map.

**Provenance tags** come from the `[[tags]]` tables in `guide.toml`. With the default settings:

```
[public]   [public](https://...)   [source: name]   [source: name 12:30]
[private: name]   [private: name p. 4]   [inference]   [unverified]
```

A name is lowercase letters, digits and hyphens. A place inside the source, such as a page or a time stamp, can follow it. A private tag outside a private block is an error. A tag inside backticks is code, not a tag.

## Private facts

A private fact goes inside a private block. The portal marks the block and keeps it closed until the reader opens it.

```markdown
:::private What the mentor said about the bottom box
The mentor's colonies overwinter in a single box [private: mentor-call 12:40].
:::
```

- The words after `:::private` are the label. The label shows while the block is closed, so it names the subject and never the fact. It is optional, and it never holds a tag.
- A private block can hold anything a section holds: paragraphs, a list, a table, a quote, a visual.
- A private block sits on its own lines. It can't sit inside a list item or another private block.
- Write the public part of an argument outside the block and the private evidence inside it. Then the section still reads with the block closed.
- A closed block shows the number and title of each visual inside it. So a visual's title is public, even inside a private block: it names the subject, never a private fact, and holds no tag.
- Search leaves out what a private block holds. It finds the block by its label and its visuals' titles only.
- The reader can open every private block on a page at once. Each page starts with them closed.
- A copy built to share, `python3 engine/build.py --share`, leaves every private block out. Only its label and its visuals' titles stay, in a closed stub.
- What is on the never-publish list never enters a topic at all. The build fails if it reaches the portal.

## Visuals

A visual is a block that names its `.svg` file and carries its job statement.

```markdown
:::visual fig-brood-timeline.svg
title: A worker takes three weeks to emerge, a queen barely two
job: Shows the three development times side by side, which is why a colony without a queen can raise a new one before the old brood runs out. The text gives the numbers; the drawing gives the race.
alt: Three horizontal bars on a shared axis of days. The queen's bar ends at day 16, the worker's at day 21 and the drone's at day 24.
credit: Redrawn from the timings in [the source](https://...).

The caption, in Markdown: what to notice, not what is drawn.
:::
```

| Field | Required | What it holds |
| --- | --- | --- |
| `title` | Yes | A heading that says what the visual shows. It is public, even inside a private block, so it never states a private fact and holds no tag |
| `job` | Yes | What the reader understands with this visual that the text gives slower, less surely, or not at all. `docs/standards/visuals.md` has the test |
| `alt` | Yes | A description for a screen reader, in full sentences |
| `credit` | When the idea is borrowed | Where the idea comes from, with a link |
| caption | Yes | After a blank line. It says what to notice. Tags and links work here |

The portal shows the title, the visual and the caption. The job statement sits under the caption, closed, behind "Why this visual is here".

**Drawing the `.svg` file.** The build copies the file into the page, so it follows the portal's colours in both themes. That works only when the file follows these rules.

- Give it a `viewBox` and no `width` or `height`. Draw for a `viewBox` 720 units wide. Up to 960 is allowed.
- Colour and type come only from the classes below. No `fill` or `stroke` colours, no `style` attributes, no `<style>` element, no hex, `rgb()` or `oklch()`. `fill="none"` and `url(#...)` are fine.
- Text is real `<text>`, 12 units or larger. No images of text, no `<image>`, no `<foreignObject>`, no `<script>`.
- Every `id` starts with the topic ID in lowercase and a hyphen, such as `b01-arrow`. Several visuals share one page, and IDs must not collide.
- Draw what is unknown with the `-unknown` classes, and say in the caption what the dashed line means.

| Class | Use it for |
| --- | --- |
| `v-area` | A neutral box, region or bar. The default |
| `v-area-strong` | A neutral box that needs more weight than `v-area` |
| `v-area-accent` | The solid shape the reader must notice. Use it on one thing, or one kind of thing |
| `v-area-wash` | A light accent box that holds or frames the point |
| `v-area-unknown` | A box for something nobody knows: dashed outline, no fill |
| `v-line` | A connector or arrow |
| `v-line-strong` | A connector that carries the main path |
| `v-line-accent` | The path the reader must follow |
| `v-line-unknown` | A connection nobody has confirmed: dashed |
| `v-rule` | Axes, gridlines, dividers |
| `v-fill-ink`, `v-fill-accent`, `v-fill-neutral` | Arrowheads, dots and markers |
| `v-text` | Ordinary labels |
| `v-text-strong` | Row and column names |
| `v-text-muted` | Secondary labels, legends |
| `v-text-accent` | The one label that names the point |
| `v-text-on-accent` | Text inside a `v-area-accent` shape |
| `v-label` | Small uppercase mono labels: axes, units |

`engine/assets/visuals.css` defines the classes.

## Materials

Each material is a `##` heading with its title and rank, then one `- key: value` line per field.

```markdown
## The hive and the honey bee, chapter 2 {critical}

- link: https://...
- by: The author or the organisation
- date: 2015
- type: book
- time: 45 min
- part: chapter 2
- access: book to buy
- checked: 2026-10-05
- what you get: What the book gives that this guide doesn't, in one or two sentences.
- passed over: The obvious alternative, and why this one won.
```

| Field | Required | Value |
| --- | --- | --- |
| `link` | Yes, except for exercises | One stable URL, not a tracking link |
| `by` | Yes | The author or the organisation |
| `date` | Yes | A year. In a tier whose facts age fast, a year and a month: `2026-09` |
| `type` | Yes | One of `materials.types` in `guide.toml`. The defaults: `article`, `paper`, `book`, `video`, `talk`, `podcast`, `documentation`, `course`, `repository`, `tool`, `exercise` |
| `time` | Yes | What the recommended part costs: `12 min`, `2 h`, `1 h 30 min` |
| `part` | When the whole is too much. Required for a critical book | Chapters, sections or time stamps |
| `access` | Yes | `free`, `paywalled` or `book to buy` |
| `checked` | Yes | The date you opened and verified it |
| `what you get` | Yes | One or two sentences: what this gives that the guide doesn't |
| `passed over` | For a critical material | One line on the obvious alternative and why this one won |
| `steps` | For an exercise | The steps in outline, as a numbered list on the following lines |
| `vendor` | For vendor content | `yes` |

- One field per line. A long value can continue on lines indented by two spaces. That's how `steps` holds its list.
- Write materials in rank order: critical first, context last.
- An exercise has no `link`. Its `by` is `this guide` when the guide wrote it.
- Materials are public. No private tag goes in any field.
- The limits are in `guide.toml` (`[materials]`), and `docs/standards/sources.md` explains them.

## Positions

Each position is a `##` heading that states it, then three lead-in paragraphs with exactly these labels.

```markdown
## Leave a strong colony alone in a cold snap

**Why hold it.** The reasoning and the evidence.

**The strongest case against.** Stated fairly.

**What would change it.** The observation that would make you drop it.
```

A field runs until the next label, so it can hold several paragraphs, a list or a private block.

## Markdown you can use

- Paragraphs, separated by a blank line. Lines inside a paragraph can wrap.
- `**bold**` for a term at its definition and for lead words. `*italic*` sparingly.
- `` `code` `` and fenced code blocks.
- Bulleted lists with `-` and numbered lists with `1.`. Nest one level, indented by two spaces.
- Tables in pipe form, with a header row and a `| --- |` line.
- `>` for a quote.
- `<!-- comments -->` for notes to reviewers. The build drops them, and they don't count as words.

Not allowed: raw HTML, images (`![...]`), footnotes and `####` headings. A visual is always a `:::visual` block.

## What the build works out

- **Words and reading time.** It counts the explanation, the case part and the positions, then divides by `sizes.words_per_minute`.
- **Each material's time** from its `time` field, and the totals by rank and by tier.
- **Visual numbers,** in order of appearance.
- **Titles of linked topics,** from the topic map.

## Pages without parts

Three kinds of page hold free text in the same Markdown, with `[[ID]]` links, tags, `:::private` blocks and `:::visual` blocks.

- **A tier's map,** `content/<tier>/intro.md`, opens the tier's page. A visual's `.svg` file sits next to it, and its IDs start with the tier's `id` and a hyphen, such as `base-arrow`. Until the file exists, the tier page shows the tier's definition and says a map comes later.
- **The home page text,** `content/home.md`. It says what the guide is, how the ranks work, how to read it and what private blocks are. The build adds the reading order, the tiers and the totals below it.
- **The open-questions page,** `content/questions.md`. Open each question on a line that starts with its ID: `### OQ-02. Does the association lend extractors?`, `**OQ-02. Does the association lend extractors?**` or `- **OQ-02.** Does the association lend extractors?`. Everything up to the next question or heading belongs to it. Write the opening line outside a private block and keep private facts out of it: it shows in the open, and every link to the question shows it as a tooltip.

In all three, a first `#` heading is the page's title. Below it, the shallowest heading becomes the page's main heading. To check one, run `python3 engine/topic.py content/questions.md`.

## The topic map

The build reads `curriculum/topic-map.md` for every topic's ID, title, tier, group, rank, size and cluster. The template in that file shows the shape; the parts the build reads are these.

- **A tier** is a `#` heading with the tier's `name` from `guide.toml`: `# Base`. A line in italics right under it is the tier's question.
- **A group** inside a tier is a `##` heading.
- **A topic** is a `###` heading with its ID and title: `### B01 How a colony works`. The line under it reads `Critical | S | C1`, then any markers, each after a `|`: `read first`, `after B01`, `updates B01, P01`, `facts age fast`, `pilot`.
- **Its fields** are `**Why:**`, `**Starting questions:**`, `**Seeds:**`, `**Visual:**` and any others, each opening a line. A planned topic's page shows them.
- **The reading order** is a numbered list under `## Reading order`, before the first tier. Each line names topic IDs, then a colon and a note.
- **Cluster quotas** sit in a table before the first tier, one row per cluster, with the quota in the last column: `| C1 | B01, B02 | The colony | 1 |`.

The marker words and the headings come from `[map]` in `guide.toml`.

## The open questions

The build reads `context/open-questions.md` for each question's ID and title only, because a question's body can hold private facts without tags. A question opens on its own line as `**OQ-01. The question?**`. A `##` heading groups the questions under it. When `map.question_groups` is set, such as to `Priority`, only questions under a `## Priority N: ...` heading count.

## Check your file

```
python3 engine/topic.py content/practical/p01-inspecting-a-hive
```

It prints what a script extracts: the header, every section with its rank and word count, every material, the positions, the visuals and the tags. Then it lists errors and warnings.

- **An error** means the build can't read the file correctly. Fix every one.
- **A warning** points at a standard the file seems to miss, such as a size outside its band. Fix it, or say why in your handoff.

Add `--json` to see the full structure the build uses. The lint, `python3 tools/lint.py`, checks the writing on top of this.

## For scripts

`engine/core/topicfile.py` is the reference reader of this format. `parse_topic(folder, settings)` returns a dictionary with these keys: `header`, `words`, `minutes`, `parts`, `why`, `short`, `sections`, `case`, `positions`, `materials`, `unverified`, `check`, `visuals`, `refs`, `tags`, `errors`, `warnings`. Body text comes back as a list of blocks, each `markdown`, `private` or `visual`, and each carries `private: true` when it sits inside a private block.
