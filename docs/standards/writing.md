# Standard: writing

How the guide's prose reads, and the workspace's own documents too. The rules follow the [Google developer documentation style guide](https://developers.google.com/style), with tighter limits. The lint checks what a script can, from the values in `[limits]` and `[lint]` in `guide.toml`.

Here, "you" is whoever writes or reviews a sentence the reader will see.

## Who is who

- **In topic text, "you" is the reader.** The guide calls itself "this guide". Don't write the reader's name in a topic: the lint flags `guide.reader` there.
- **The guide has no first person.** No "we", no "I", no "our".
- **Process words stay out of topic text.** The reader doesn't need to know about workers, dossiers or the topic map. `lint.meta_words` lists the words the lint flags.
- **In the workspace's documents, "you" is whoever the document is for.** In the README and the method page, that's the owner. In the standards, the briefs and the worker pack, it's the worker. Those documents name the reader.

## Sentences

- One idea per sentence.
- Aim under 25 words. Aim under 20 for anything the reader has to do. The lint warns above `limits.sentence_words` (35), and above `limits.sentence_words_action` (30) under "What to look at first".
- One topic per paragraph, and at most `limits.paragraph_sentences` (6) sentences.
- Active voice, present tense. Name who does the action.
- Put the condition first: "To check for a laying queen, look for eggs."
- Contractions are good, especially in negations. "Don't" is harder to misread than "do not".

## Certainty

Say exactly how sure you are.

| Word | Means |
| --- | --- |
| must | Required |
| a good default is | Recommended, and the reader can decline. In the workspace's documents: "we recommend" |
| can | Optional, or able to happen |
| might | A real possibility |

Avoid a bare "should": it reads as a requirement and as a suggestion. Never write a guess as a fact. When something is uncertain, say what would settle it.

## Explain, then name

Introduce an idea in plain words first, then give it its name.

- Weak: "Supersedure replaces a failing queen."
- Better: "When a queen starts to fail, the workers raise a new one while she still lays. For a while, the colony can have both. Beekeepers call this supersedure."

## Words

- **One word per concept.** `context/glossary.md` is the list. Repeat the right word, and don't rotate synonyms. The lint flags the words in the glossary's "Don't use" column.
- **Plain over specialised.** Use the technical name when it's the name the reader will hear in the case, and define it once.
- **No more than two nouns in front of another noun.**
- **Spell out an abbreviation at first use.** `lint.abbreviations` lists the ones the lint checks.
- **Never call anything "simple", "easy" or "quick".** A step that cost the writer no effort can still stop the reader.
- **Follow the guide's spelling,** `guide.spelling` (British by default). Names keep their own spelling.
- **In topic text, write "this guide",** not "the guide". The lint warns on the second.

## Dashes

Don't use em dashes, en dashes or double hyphens in prose. Use a full stop, a comma, a colon or parentheses. Write ranges with "to": 2024 to 2026, 10 to 15 minutes.

## Patterns to cut

Run the `no-ai-slop` skill, in `.claude/skills/no-ai-slop/`, on your prose before you hand it off. It finds these, among others:

- Contrast frames: "It's not X, it's Y." State Y.
- Openers that clear the throat: "Here's the thing", "It's worth noting".
- Claims of rare insight: "What most people miss".
- A colon followed by a dramatic reveal.
- Closing lines that restate the section or try to sound deep.
- Filler adverbs: "simply", "really", "truly", "fundamentally".
- Inflated verbs: "leverage", "utilise", "empower", "streamline".

## Structure

- **Headings say something.** "A queen develops from egg to adult in about 16 days" beats "Queen development".
- **Sentence case** in headings. No emoji. `lint.proper_nouns` lists the capitalised words the lint accepts in a heading.
- **Tables** for comparisons across the same attributes.
- **Lists** for parallel items, one or two sentences each.
- **Prose** for reasoning. Don't break an argument into bullets.
- **Bold** for the lead words of a list item and for a term at its definition. Not for emphasis inside a sentence.

## Numbers and dates

- A number has a unit, a date and a source.
- Write dates as `2026-10-05` in headers and fields, and as "5 October 2026" in prose, in the order `guide.language` uses.
- Mark anything that will age: "as of October 2026".

## Opinions

An opinion arrives with its background: the reasoning, the strongest case against, and what would change it. Without them, the reader can't weigh it. In a topic, it goes in "Positions".

## What stays verbatim

Quotes, error text, command output and code. Clean a spoken quote of filler words and slips of the tongue, and nothing else.

## Never at the cost of substance

When a rule here would cut reasoning the reader needs, keep the reasoning and split it into more short sentences.

## How a reviewer checks

1. Run the lint: `python3 tools/lint.py <paths>`. Every error is a finding. A warning is a finding unless the handoff explains it.
2. Run the `no-ai-slop` skill in detect mode, and list what it names.
3. Read every term against `context/glossary.md`. A synonym for a glossary term is a finding, even when the lint misses it.
4. Read every heading on its own. A heading that names a subject without saying something about it is a finding.
5. Search for the certainty words. A bare "should", or a guess stated as a fact, is a finding.
