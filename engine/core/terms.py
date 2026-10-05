"""Term lists: what a scan looks for, and how a term matches.

Two files use this syntax. A private-term list (tools/scan.py) names what would
identify a private source if it reached a public place. A never-publish list
(context/never-publish.md) names what must never reach the portal.

    One term per line. Matching ignores case.
    A word boundary applies at each end of a term that is a letter or a digit.
    A line that starts with "re:" is a Python regular expression. It ignores case
    too; write (?-i:...) inside it to match case exactly.

A private-term list also has sections: lines after "[block]" fail a scan, and
lines after "[warn]" are printed for a person to judge. Blank lines and lines
that start with "#" are comments.

Standard library only. Python 3.9 or later, so a git hook can run it anywhere.
"""

import re

BLOCK, WARN = "block", "warn"


class Term:
    """One line of a term list, compiled."""

    def __init__(self, raw, level=BLOCK, line=0):
        self.raw = raw
        self.level = level
        self.line = line
        if raw.startswith("re:"):
            pattern = raw[3:]
        else:
            pattern = re.escape(raw)
            if raw[:1].isalnum():
                pattern = r"\b" + pattern
            if raw[-1:].isalnum():
                pattern = pattern + r"\b"
        try:
            self.regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            self.error = None
        except re.error as exc:
            self.regex = None
            self.error = str(exc)

    def finditer(self, text):
        if self.regex is None:
            return iter(())
        return self.regex.finditer(text)


def parse_term_list(text):
    """Terms from a private-term list: [block] and [warn] sections, comments, re: lines.
    Returns (terms, problems). A line before any section counts as [block]."""
    terms, problems, level = [], [], BLOCK
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.lower() in ("[block]", "[warn]"):
            level = s.lower()[1:-1]
            continue
        t = Term(s, level, n)
        if t.error:
            problems.append("line %d: the regular expression doesn't compile (%s)" % (n, t.error))
        else:
            terms.append(t)
    return terms, problems


def parse_markdown_list(text):
    """Terms from a Markdown file such as context/never-publish.md: every list item
    in the file, wherever it sits, except inside a fenced code block. An item can
    sit in backticks, so Markdown leaves a regular expression alone:
    - `re:\\bsome phrase\\b`.

    Only list items count. Paragraphs around them explain the list."""
    terms, problems = [], []
    in_code = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^\s*[-*]\s+(.+?)\s*$", line)
        if not m:
            continue
        item = m.group(1)
        if len(item) >= 2 and item[0] == "`" and item[-1] == "`":
            item = item[1:-1]
        if not item:
            continue
        t = Term(item, BLOCK, n)
        if t.error:
            problems.append("line %d: the regular expression doesn't compile (%s)" % (n, t.error))
        else:
            terms.append(t)
    return terms, problems


def find(terms, text):
    """Yield (term, match) for every hit of every term in text."""
    for t in terms:
        for m in t.finditer(text):
            yield t, m


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1
