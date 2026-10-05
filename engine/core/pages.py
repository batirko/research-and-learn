"""Read and check the guide's pages without parts: the tier introductions
(content/<tier>/intro.md), the home page text (content/home.md) and the
open-questions page (content/questions.md).

They have no header and no parts. They use the Markdown of engine/format.md,
with [[ID]] links, provenance tags, :::private blocks and :::visual blocks.
"""

import re
from pathlib import Path

from .topicfile import (Report, check_svg, known_ids, parse_blocks, scan_text,
                        strip_comments, walk_blocks)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def heading_anchor(title, prefix=""):
    """The id the renderer gives a heading. Keep the two in step."""
    return prefix + re.sub(r"[^a-z0-9]+", "-", title.strip().lower()).strip("-")[:60]


def heading_levels(blocks):
    """Map Markdown heading depth to HTML levels: the shallowest heading in the file
    becomes <h2>, the next <h3>, and so on, never deeper than <h6>."""
    depths = set()
    for b in walk_blocks(blocks):
        if b["type"] != "markdown":
            continue
        in_code = False
        for line in b["text"].split("\n"):
            if line.lstrip().startswith("```"):
                in_code = not in_code
            m = HEADING_RE.match(line)
            if m and not in_code:
                depths.add(len(m.group(1)))
    top = min(depths) if depths else 2
    return {d: min(6, 2 + d - top) for d in range(1, 7)}


def check_blocks(blocks, S, rep, ids, folder, id_prefix):
    """The checks a topic's text gets, for a page without parts."""
    refs = {"topics": [], "questions": []}
    topic_ids, question_ids = ids
    for b in walk_blocks(blocks):
        texts = []
        if b["type"] == "markdown":
            texts.append(b["text"])
        elif b["type"] == "visual":
            texts += [b["caption"], b["title"] + " " + b["alt"] + " " + b.get("credit", "")]
            svg = folder / b["file"]
            if not svg.exists():
                rep.error(b["line"], "The visual file %s is not next to the page." % b["file"])
            else:
                check_svg(svg, id_prefix, b["line"], rep)
        for text in texts:
            scan_text(text, b.get("line") or 0, b.get("private", False), S, rep, topic_ids, question_ids, refs)
    return refs


def parse_page(path, S, ids=None, id_prefix=None):
    """Blocks, heading levels, links, errors and warnings of one page file."""
    path = Path(path)
    rep = Report(str(path))
    if not path.exists():
        rep.error(0, "%s doesn't exist." % path)
        return {"path": str(path), "blocks": [], "levels": heading_levels([]), "refs": {"topics": [], "questions": []},
                "errors": rep.errors, "warnings": rep.warnings}
    lines = strip_comments(path.read_text(encoding="utf-8")).splitlines()
    blocks = parse_blocks(lines, 1, S, rep)
    ids = ids if ids is not None else known_ids(S)
    prefix = id_prefix or (path.parent.name if path.name == "intro.md" else path.stem)
    refs = check_blocks(blocks, S, rep, ids, path.parent, prefix)
    return {"path": str(path), "blocks": blocks, "levels": heading_levels(blocks), "refs": refs,
            "errors": rep.errors, "warnings": rep.warnings}


# ---------------------------------------------------------------- the open-questions page

def question_start_re(S):
    """A line that opens a question: an optional heading or list marker, optional bold,
    then the ID. A line that opens with a link, such as [[OQ-04]], cites a question
    and doesn't open one."""
    return re.compile(r"^\s*(?:#{1,6}\s+)?(?:(?:[-*]|\d+\.)\s+)?(?:\*\*|__|\*|_)?\s*(%s)\b" % S.question_id_pattern)


def question_title(line, S):
    """The words of a question's opening line, without its marks and its ID."""
    qid = S.question_id_pattern
    s = re.sub(r"^\s*(?:#{1,6}\s+)?(?:(?:[-*]|\d+\.)\s+)?", "", line).strip()
    bold = re.match(r"^(\*\*|__)(.+?)\1\s*(.*)$", s)
    if bold:
        inner = re.sub(r"^%s\b[.:)\s-]*" % qid, "", bold.group(2).strip()).strip()
        s = inner or bold.group(3)
    else:
        s = re.sub(r"^[*_]?%s\b[.:)\s-]*" % qid, "", s)
    s = S.ref_re.sub(lambda m: m.group("text") or m.group("id"), s)
    s = S.tag_re.sub("", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[*_`]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def question_chunks(blocks, S):
    """Split the page at each line that opens a question, and at each other heading.

    Returns a list of {"qid", "title", "heading", "blocks"}. qid is the question's ID
    for a chunk that opens a question, else None. heading is the heading's text when the
    chunk opens with a heading. A private or visual block stays whole, in the chunk it
    follows: a question that opens inside a private block isn't split out.
    """
    start_re = question_start_re(S)
    chunks = [{"qid": None, "title": "", "heading": None, "blocks": []}]
    for b in blocks:
        if b["type"] != "markdown":
            chunks[-1]["blocks"].append(b)
            continue
        buf, start, in_code = [], b["line"], False

        def flush():
            if any(x.strip() for x in buf):
                lead = next(k for k, x in enumerate(buf) if x.strip())
                chunks[-1]["blocks"].append({"type": "markdown", "text": "\n".join(buf).strip("\n"),
                                             "private": False, "line": start + lead})
            buf.clear()

        for k, line in enumerate(b["text"].split("\n")):
            if line.lstrip().startswith("```"):
                in_code = not in_code
            q = None if in_code else start_re.match(line)
            h = None if in_code else HEADING_RE.match(line)
            if q or h:
                flush()
                start = b["line"] + k
                chunks.append({"qid": q.group(1) if q else None, "title": question_title(line, S) if q else "",
                               "heading": h.group(2).strip() if h else None, "blocks": []})
            buf.append(line)
        flush()
    return [c for c in chunks if c["blocks"]]


def report(path, S):
    """What engine/topic.py prints for a page without parts."""
    page = parse_page(path, S)
    out = [page["path"],
           "  %d blocks, %d private" % (len(page["blocks"]),
                                       len([b for b in walk_blocks(page["blocks"]) if b["type"] == "private"]))]
    if Path(path).resolve() == S.file("questions_page"):
        chunks = question_chunks(page["blocks"], S)
        qs = [c for c in chunks if c["qid"]]
        out.append("  %d questions found: %s" % (len(qs), " ".join(c["qid"] for c in qs)))
        seen = set()
        for c in qs:
            if c["qid"] in seen:
                page["warnings"].append({"line": c["blocks"][0]["line"], "code": "question-twice",
                                         "message": "%s opens twice. The page links to the first." % c["qid"]})
            seen.add(c["qid"])
        _, question_ids = known_ids(S)
        missing = sorted((question_ids or set()) - seen)
        if missing:
            out.append("  Not opened as a question on a line of its own: %s" % " ".join(missing))
    for e in page["errors"]:
        out.append("  ERROR line %s: %s" % (e["line"], e["message"]))
    for w in page["warnings"]:
        out.append("  warning line %s: %s" % (w["line"], w["message"]))
    out.append("%d errors, %d warnings" % (len(page["errors"]), len(page["warnings"])))
    return "\n".join(out), bool(page["errors"])
