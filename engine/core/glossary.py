"""Read the glossary for the glossary page and for the lint.

The glossary is written for the guide's writers. The page is for its reader, so
this module keeps the terms and their meanings and leaves out the bookkeeping:

- Sentences that start with a bookkeeping word, such as "Added from B04.", and
  decision references such as "(D12)". glossary.bookkeeping and
  glossary.decision_prefix in the settings name them.
- A sentence such as "B04 is the home." becomes the row's link to its home topic.
- A sentence that carries a private provenance tag, or matches
  privacy.glossary_source, is private. The page shows it in a collapsed block.

When the settings name the reader, the page speaks to them: "Sam's plan" shows as
"your plan". The glossary's own first person ("our term") becomes "the guide's term".

The "Don't use" column lists the words the glossary bans. The lint reads them:
a plain word is banned everywhere, and a word in *italics* is banned in this
row's sense only, so the lint warns instead of failing.
"""

import re


def split_sentences(text):
    """Sentences, split after '.', '?' or '!' followed by a space and a capital,
    a quote or a link. Keeps backtick spans whole."""
    parts, cur, i, in_code = [], "", 0, False
    while i < len(text):
        ch = text[i]
        cur += ch
        if ch == "`":
            in_code = not in_code
        elif ch in ".?!" and not in_code and i + 1 < len(text) and text[i + 1] == " ":
            nxt = text[i + 2:i + 3]
            if nxt and (nxt.isupper() or nxt in "\"“'*["):
                parts.append(cur.strip())
                cur = ""
                i += 1
        i += 1
    if cur.strip():
        parts.append(cur.strip())
    return parts


def _verb(m):
    """'Sam reads' -> 'you read', 'Sam watches' -> 'you watch'."""
    word = m.group(1)
    if word in ("is", "was", "has", "does"):
        return "you " + {"is": "are", "was": "were", "has": "have", "does": "do"}[word]
    if re.search(r"(?:ch|sh|ss|x|o)es$", word):
        return "you " + word[:-2]
    if word.endswith("ies"):
        return "you " + word[:-3] + "y"
    return "you " + word[:-1]


def second_person(sentence, reader):
    """Speak to the reader: "Sam's plan" -> "your plan", "our term" -> "the guide's term"."""
    out = sentence
    if reader:
        name = re.escape(reader)
        out = re.sub(r"\b%s's\b" % name, "your", out)
        out = re.sub(r"\b%s ([a-z]+s)\b" % name, _verb, out)
        out = re.sub(r"\b%s\b" % name, "you", out)
        if sentence.startswith(reader):
            out = out[:1].upper() + out[1:]
    return re.sub(r"\bour (addition|reading|term|word|choice)\b", r"the guide's \1", out)


def clean_meaning(text, S):
    """(public sentences, private sentences, home topic IDs, dropped bookkeeping)."""
    public, private, homes, dropped = [], [], [], []
    bookkeeping = tuple(w + " " for w in S.glossary["bookkeeping"]) + tuple(w + "," for w in S.glossary["bookkeeping"])
    home_re = re.compile(r"\b(%s) (?:is the|is its) home\b" % S.topic_id_pattern)
    only_home_re = re.compile(r"^%s (?:is the|is its) home\.?$" % S.topic_id_pattern)
    prefix = S.glossary["decision_prefix"]
    decision_re = re.compile(r"\s*\((?:[^()]*?\b)?%s\d{1,4}(?:, %s\d{1,4})*\)" % (re.escape(prefix), re.escape(prefix))) \
        if prefix else None
    for s in split_sentences(text):
        if bookkeeping and s.startswith(bookkeeping):
            dropped.append(s)
            continue
        homes += home_re.findall(s)
        bare = decision_re.sub("", s).strip() if decision_re else s
        if bare != s:
            dropped.append(s)
        if not bare or bare in (".", ";"):
            continue
        if bare[-1:] not in ".?!" and not bare.endswith(('."', '.”', '?"', '!"')):
            bare += "."
        bare = re.sub(r"\s+([.,;])", r"\1", bare)
        if only_home_re.match(bare):
            continue
        bare = second_person(bare, S.reader)
        is_private = S.has_private_tag(bare) or bool(S.glossary_source_re and S.glossary_source_re.search(bare))
        (private if is_private else public).append(bare)
    seen = []
    for h in homes:
        if h not in seen:
            seen.append(h)
    return public, private, seen, dropped


def link_ids(text, S):
    """Topic IDs become links that show the ID, and question IDs become question links.
    Leaves code spans and existing [[...]] links alone."""
    def sub(chunk):
        chunk = re.sub(r"(?<![\[\w|])(%s)(?![\w\]])" % S.topic_id_pattern, r"[[\1|\1]]", chunk)
        return re.sub(r"(?<![\[\w|])(%s)(?![\w\]])" % S.question_id_pattern, r"[[\1]]", chunk)
    pieces = re.split(r"(`[^`]*`|\[\[[^\]]*\]\])", text)
    return "".join(p if p.startswith(("`", "[[")) else sub(p) for p in pieces)


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def slug(text):
    m = re.search(r"\*\*(.+?)\*\*", text)
    base = m.group(1) if m else text
    return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:60] or "term"


def parse(S):
    """Sections, each {"title", "rows", "notes", "dropped"}. A row is {"use", "public",
    "private", "homes", "avoid", "anchor", "line"}. A note is a paragraph outside a table,
    cleaned the same way. An empty list when the glossary doesn't exist."""
    path = S.file("glossary")
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    sections, cur, i = [], None, 0
    used = set()
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            cur = {"title": line[3:].strip(), "rows": [], "notes": [], "dropped": []}
            sections.append(cur)
            i += 1
            continue
        if cur is None:
            i += 1
            continue
        if line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            head = [h.lower() for h in split_row(line)]
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                cells = split_row(lines[j]) + ["", "", ""]
                row = dict(zip(head, cells))
                use, meaning = row.get("use", cells[0]), row.get("meaning", cells[1])
                public, private, homes, dropped = clean_meaning(meaning, S)
                anchor = base = "term-" + slug(use)
                k = 2
                while anchor in used:
                    anchor = "%s-%d" % (base, k)
                    k += 1
                used.add(anchor)
                cur["rows"].append({"use": use, "public": public, "private": private, "homes": homes,
                                    "avoid": row.get("don't use", row.get("don’t use", "")), "anchor": anchor,
                                    "line": j + 1})
                cur["dropped"] += dropped
                j += 1
            i = j
            continue
        if line.strip():
            j, para = i, []
            while j < len(lines) and lines[j].strip() and not lines[j].startswith(("#", "|")):
                para.append(lines[j].strip())
                j += 1
            public, private, homes, dropped = clean_meaning(" ".join(para), S)
            cur["dropped"] += dropped
            if public or private:
                cur["notes"].append({"public": public, "private": private})
            i = max(j, i + 1)
            continue
        i += 1
    return sections


def bans(sections):
    """The words the glossary bans, from its "Don't use" column.

    Returns [(word, sense_only, the term to use, the row's home topics)]. A plain
    word is banned everywhere. A word in *italics* is banned in the row's sense
    only. Quotes, backticks and bold around a word are dropped, and so is a
    parenthesis after it, which explains the ban."""
    out = []
    for sec in sections:
        for r in sec["rows"]:
            use = re.sub(r"[*`]", "", r["use"]).strip()
            text = re.sub(r"\([^)]*\)", "", r["avoid"])
            for item in re.split(r"[,;]", text):
                item = item.strip()
                if not item or item.lower() in ("none", "nothing", "-"):
                    continue
                sense = bool(re.fullmatch(r"\*[^*]+\*|_[^_]+_", item))
                word = re.sub(r"[*_`\"“”'‘’]", "", item).strip()
                if word and len(word) > 1:
                    out.append((word, sense, use, r["homes"]))
    return out
