# Never publish

What must never reach the portal, not even inside a collapsed private block. The build reads this file after every build. Its guard fails when a term appears anywhere in the portal: a page, a script, a stylesheet or a drawing. The lint fails when a term appears in a topic.

A private block keeps a fact out of sight until the reader opens it. This list is for facts the reader doesn't need, or that must not travel with the portal. Examples: an address, a door code, someone else's phone number, something said in confidence. Writers keep these facts out of every topic, and the guard catches the ones that slip through.

**To fill this file.** The set-up skill and the scaffold add a term whenever the owner names something that must never publish, or the sources hold one. Workers propose terms in their handoff, and the orchestrator adds them. Change nothing else in this file. Write instructions and notes as paragraphs, never as list items.

**The shape the build reads.** Every Markdown list item in this file is a term, wherever it sits, except inside a fenced code block. So the terms are the only list items here, one term per item. Matching ignores case. A term that starts or ends with a letter or a digit matches whole words only at that end.

An item that starts with `re:` is a Python regular expression, which also ignores case. Write `(?-i:...)` inside it to match case exactly. Put a regular expression in backticks, so Markdown leaves it alone. A regular expression that doesn't compile fails the guard.

For example, in a guide on a first season keeping bees:

```markdown
- Hollow Lane
- `re:\bmentor's (?:home|phone)\b`
```

The first item keeps the street where the apiary stands out of the portal. The second keeps out any sentence about the mentor's home or phone.

This list sits in the workspace, so anyone who has the workspace can read it. Keep a term short enough to catch the fact without restating it.

## The list
