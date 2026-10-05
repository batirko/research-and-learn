"""Read and check one topic folder written in the topic file format.

engine/format.md specifies the format. This module is its reference reader: the
build imports parse_topic(), and engine/topic.py runs it on one folder so a writer
can see what a script extracts.

Every finding carries a code, so the lint can carry structure findings over
once and report the ones it owns in its own words.
"""

import re
from pathlib import Path

from .settings import RANKS

TOPIC_FILE = "topic.md"

ACCESS = ["free", "paywalled", "book to buy"]
MATERIAL_FIELDS = ["link", "by", "date", "type", "time", "part", "access", "checked",
                   "what you get", "passed over", "steps", "vendor"]

BAD_REF_RE = re.compile(r"\[\[([^\]]*)\]\]")
RANK_ATTR_RE = re.compile(r"^(?P<title>.*?)\s*\{(?P<rank>[A-Za-z]+)\}\s*$")
FENCE_OPEN_RE = re.compile(r"^:::\s*(?P<name>[a-z]+)\s*(?P<arg>.*?)\s*$")
FENCE_CLOSE_RE = re.compile(r"^:::\s*$")
FIELD_RE = re.compile(r"^-\s+(?P<key>[a-z][a-z ]*?)\s*:\s?(?P<value>.*)$")
LEADIN_RE = re.compile(r"^\*\*(?P<label>[^*]+?)\.\*\*\s*(?P<rest>.*)$")
TIME_RE = re.compile(r"^(?:(?P<h>\d+)\s*h)?\s*(?:(?P<m>\d+)\s*min)?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MATERIAL_DATE_RE = re.compile(r"^\d{4}(?:-\d{2})?(?:-\d{2})?$")
CODE_SPAN_RE = re.compile(r"`[^`\n]*`")


class Report:
    def __init__(self, path):
        self.path = path
        self.errors = []
        self.warnings = []

    def error(self, line, msg, code="structure"):
        self.errors.append({"line": line, "message": msg, "code": code})

    def warn(self, line, msg, code="structure"):
        self.warnings.append({"line": line, "message": msg, "code": code})


def norm_key(key):
    return re.sub(r"[\s_-]+", " ", key.strip().lower())


def rank_index(rank):
    return RANKS.index(rank) if rank in RANKS else None


def slugify(text):
    text = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:60] or "section"


def strip_comments(text):
    """Remove HTML comments, keeping line numbers stable."""
    return re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)


def known_ids(S):
    """Topic IDs and titles from the topic map, and question IDs from the open questions.
    Either is None when its file doesn't exist."""
    topics, questions = None, None
    tm = S.file("topic_map")
    if tm.exists():
        topics = {}
        rx = re.compile(r"^### (%s) (.+)$" % S.topic_id_pattern)
        for line in tm.read_text(encoding="utf-8").splitlines():
            m = rx.match(line)
            if m:
                topics[m.group(1)] = m.group(2).strip()
    oq = S.file("open_questions")
    if oq.exists():
        questions = set(re.findall(r"(?<![\w-])%s(?!\w)" % S.question_id_pattern, oq.read_text(encoding="utf-8")))
    return topics, questions


# ---------------------------------------------------------------- header

def parse_header(lines, S, rep):
    """Return (header dict, index of the first body line)."""
    keys = S.header_keys()
    if not lines or lines[0].strip() != "---":
        rep.error(1, "The file must start with a header between two '---' lines.")
        return {}, 0
    header = {}
    for i in range(1, len(lines)):
        raw = lines[i]
        if raw.strip() == "---":
            return header, i + 1
        if not raw.strip():
            continue
        if ":" not in raw:
            rep.error(i + 1, "A header line must read 'key: value'.")
            continue
        key, value = raw.split(":", 1)
        key, value = norm_key(key), value.strip()
        if key not in keys:
            rep.error(i + 1, "Unknown header key '%s'." % key)
            continue
        if keys[key][2]:
            items = [v.strip() for v in value.strip("[]").split(",") if v.strip()]
            value = [] if items in ([], ["none"]) else items
        header[key] = value
    rep.error(1, "The header has no closing '---' line.")
    return header, len(lines)


def check_header(h, folder, S, rep):
    tier = S.tier_by_id.get(h.get("tier", ""))
    for key, (req, req_updates, _) in S.header_keys().items():
        if key not in h and (req or (req_updates and tier is not None and tier.updates)):
            rep.error(1, "Header is missing '%s'." % key)
    tid = h.get("id", "")
    letters = ", ".join(t.prefix for t in S.tiers)
    if tid and not S.topic_id_re.match(tid):
        rep.error(1, "id must be a tier letter (%s) and two digits, such as %s05." % (letters, S.tiers[0].prefix))
    elif tid and h.get("tier") and S.tier_of_id(tid) != h.get("tier"):
        rep.error(1, "tier '%s' doesn't match the id %s." % (h.get("tier"), tid))
    if h.get("tier") and tier is None:
        rep.error(1, "tier must be one of: %s." % ", ".join(S.tier_ids))
    if h.get("rank") and h["rank"] not in RANKS:
        rep.error(1, "rank must be critical, high, medium or context.")
    if h.get("size") and h["size"] not in S.sizes:
        rep.error(1, "size must be S, M, L or XL.")
    if h.get("depth") and h["depth"] not in ("1", "2", "3"):
        rep.error(1, "depth must be 1, 2 or 3.")
    if h.get("cluster") and not S.cluster_re.match(h["cluster"]):
        rep.error(1, "cluster must look like %s7." % S.cluster_prefix)
    for key in ("checked", "check again"):
        if h.get(key) and not DATE_RE.match(h[key]):
            rep.error(1, "%s must be a date such as 2026-10-04." % key)
    for key in ("read first", "updates"):
        for ref in h.get(key, []) or []:
            if not S.topic_id_re.match(ref):
                rep.error(1, "'%s' in %s is not a topic id." % (ref, key))
    if tier is not None and tier.updates and h.get("covers") not in ("problem", "solutions", "both"):
        rep.error(1, "covers must be problem, solutions or both.")
    if tier is not None and not tier.updates:
        for key in ("updates", "covers"):
            if key in h:
                rep.error(1, "'%s' belongs only to topics in a tier that updates others." % key)
    content = S.content
    try:
        inside = folder.resolve().relative_to(content)
    except ValueError:
        inside = None
    if inside is not None and h.get("tier") and inside.parts[:1] != (h["tier"],):
        rep.error(1, "The folder isn't under %s/%s/." % (S.paths["content"], h["tier"]))
    if tid and not folder.name.startswith(tid.lower() + "-"):
        rep.error(1, "The folder name must start with '%s-'." % tid.lower())


# ---------------------------------------------------------------- blocks

def parse_blocks(lines, start_line, S, rep, private=False):
    """Split a run of body lines into markdown, private and visual blocks."""
    blocks, buf, i = [], [], 0
    buf_line = [start_line]

    def flush():
        text = "\n".join(buf).strip("\n")
        if text.strip():
            lead = next(k for k, l in enumerate(buf) if l.strip())
            blocks.append({"type": "markdown", "text": text, "private": private,
                           "line": buf_line[0] + lead})
        buf.clear()

    in_code = False
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code:
            mo = FENCE_OPEN_RE.match(line)
            if mo and not FENCE_CLOSE_RE.match(line):
                flush()
                name, arg = mo.group("name"), mo.group("arg")
                depth, j = 1, i + 1
                while j < len(lines):
                    if FENCE_CLOSE_RE.match(lines[j]):
                        depth -= 1
                        if depth == 0:
                            break
                    elif FENCE_OPEN_RE.match(lines[j]):
                        depth += 1
                    j += 1
                if j >= len(lines):
                    rep.error(start_line + i, "':::%s' has no closing ':::' line." % name)
                inner = lines[i + 1:j]
                if name == "private":
                    if private:
                        rep.error(start_line + i, "A private block can't sit inside another.")
                    blocks.append({"type": "private", "label": arg,
                                   "blocks": parse_blocks(inner, start_line + i + 1, S, rep, True),
                                   "line": start_line + i})
                    if arg and S.tag_re.search(arg):
                        rep.error(start_line + i, "A private label shows while collapsed. Keep tags out of it.")
                elif name == "visual":
                    blocks.append(parse_visual(arg, inner, start_line + i, S, rep, private))
                else:
                    rep.error(start_line + i, "Unknown block ':::%s'. Use private or visual." % name)
                i = j + 1
                continue
            if FENCE_CLOSE_RE.match(line):
                rep.error(start_line + i, "A ':::' line closes nothing.")
                i += 1
                continue
        if not buf:
            buf_line[0] = start_line + i
        buf.append(line)
        i += 1
    flush()
    return blocks


def parse_visual(arg, inner, line_no, S, rep, private):
    vis = {"type": "visual", "file": arg, "private": private, "line": line_no,
           "title": "", "job": "", "alt": "", "credit": "", "caption": ""}
    k = 0
    while k < len(inner) and inner[k].strip():
        m = re.match(r"^(title|job|alt|credit):\s*(.*)$", inner[k].strip())
        if not m:
            break
        vis[m.group(1)] = m.group(2).strip()
        k += 1
    vis["caption"] = "\n".join(inner[k:]).strip()
    if not arg.endswith(".svg") or "/" in arg:
        rep.error(line_no, "A visual names one .svg file next to the text: ':::visual fig-name.svg'.")
    for key in ("title", "job", "alt"):
        if not vis[key]:
            rep.error(line_no, "The visual %s is missing '%s:'." % (arg, key))
    if not vis["caption"]:
        rep.error(line_no, "The visual %s has no caption. Say what to notice." % arg)
    if S.tag_re.search(vis["title"]):
        rep.error(line_no, "A visual's title is public: it shows on a collapsed private block. Keep tags out of it.")
    return vis


# ---------------------------------------------------------------- body

def split_by_heading(lines, start_line, level):
    """Return (lead lines, [(title, line_no, body lines)]) for '#'*level headings."""
    prefix = "#" * level + " "
    lead, sections, cur, in_code = [], [], None, False
    for k, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and line.startswith(prefix):
            cur = (line[len(prefix):].strip(), start_line + k, [])
            sections.append(cur)
        elif cur is None:
            lead.append(line)
        else:
            cur[2].append(line)
    return lead, sections


def list_items(text):
    return [m.group(1).strip() for m in re.finditer(r"^(?:[-*]|\d+\.)\s+(.*)$", text, re.M)]


def parse_fields(body, line_no, rep, where):
    """Parse '- key: value' lines with indented continuation lines."""
    fields, order, cur = {}, [], None
    for k, line in enumerate(body):
        if not line.strip():
            continue
        m = FIELD_RE.match(line)
        if m and not line.startswith(" "):
            cur = norm_key(m.group("key"))
            if cur in fields:
                rep.error(line_no + k + 1, "%s repeats the field '%s'." % (where, cur))
            fields[cur] = m.group("value").strip()
            order.append(cur)
        elif cur and line.startswith("  "):
            fields[cur] = (fields[cur] + "\n" + line[2:]).strip("\n")
        else:
            rep.error(line_no + k + 1, "%s holds only '- key: value' lines." % where)
    return fields, order


def parse_material(title_raw, line_no, body, S, rep):
    m = RANK_ATTR_RE.match(title_raw)
    title, rank = (m.group("title"), m.group("rank").lower()) if m else (title_raw, None)
    if rank not in RANKS:
        rep.error(line_no, "The material '%s' needs a rank: {critical}, {high}, {medium} or {context}." % title)
    fields, order = parse_fields(body, line_no, rep, "The material '%s'" % title)
    for key in fields:
        if key not in MATERIAL_FIELDS:
            rep.error(line_no, "The material '%s' has an unknown field '%s'." % (title, key))
    mtype = fields.get("type", "")
    required = ["by", "date", "type", "time", "access", "checked", "what you get"]
    if mtype != "exercise":
        required.append("link")
    else:
        required.append("steps")
    if rank == "critical":
        required.append("passed over")
        if mtype == "book":
            required.append("part")
    for key in required:
        if not fields.get(key):
            rep.error(line_no, "The material '%s' is missing '%s'." % (title, key))
    if mtype and mtype not in S.material_types:
        rep.error(line_no, "The material '%s' has an unknown type '%s'. The types are: %s."
                  % (title, mtype, ", ".join(S.material_types)))
    if fields.get("access") and fields["access"] not in ACCESS:
        rep.error(line_no, "access must be free, paywalled or book to buy.")
    if fields.get("checked") and not DATE_RE.match(fields["checked"]):
        rep.error(line_no, "checked must be a date such as 2026-10-04.")
    if fields.get("date") and not MATERIAL_DATE_RE.match(fields["date"]):
        rep.error(line_no, "date must be a year, a year and month, or a full date: 2026-09.")
    if fields.get("vendor") and fields["vendor"] != "yes":
        rep.error(line_no, "vendor takes only the value yes.")
    minutes = None
    tm = TIME_RE.match(fields.get("time", "").strip())
    if fields.get("time") and (not tm or not (tm.group("h") or tm.group("m"))):
        rep.error(line_no, "time must read like '25 min', '2 h' or '1 h 30 min'.")
    elif tm:
        minutes = int(tm.group("h") or 0) * 60 + int(tm.group("m") or 0)
    if fields.get("link") and not re.match(r"^https?://\S+$", fields["link"]):
        rep.error(line_no, "link must be one full URL.")
    return {"title": title, "rank": rank, "minutes": minutes, "fields": fields,
            "field_order": order, "line": line_no}


def parse_position(statement, line_no, body, S, rep):
    labels = [f.lower() for f in S.position_fields]
    fields, cur = {}, None
    collected = {}
    for k, line in enumerate(body):
        m = LEADIN_RE.match(line)
        if m and m.group("label").strip().lower() in labels:
            cur = m.group("label").strip().lower()
            collected[cur] = ([m.group("rest")], line_no + k + 1)
        elif cur is None:
            if line.strip():
                rep.error(line_no + k + 1, "A position starts with '**%s.**' under its heading." % S.position_fields[0])
        else:
            collected[cur][0].append(line)
    for label, key in zip(S.position_fields, labels):
        if key not in collected:
            rep.error(line_no, "The position '%s' is missing '**%s.**'." % (statement, label))
        else:
            lines, start = collected[key]
            fields[key] = parse_blocks(lines, start, S, rep)
    return {"position": statement, "fields": fields, "line": line_no}


def section_record(half, title_raw, line_no, body, topic_rank, S, rep):
    m = RANK_ATTR_RE.match(title_raw)
    title, rank = (m.group("title"), m.group("rank").lower()) if m else (title_raw, None)
    if rank not in RANKS:
        rep.error(line_no, "The section '%s' needs a rank: {critical}, {high}, {medium} or {context}." % title)
    elif topic_rank in RANKS and rank_index(rank) < rank_index(topic_rank):
        rep.error(line_no, "The section '%s' ranks above its topic (%s)." % (title, topic_rank))
    for k, line in enumerate(body):
        if re.match(r"^#{4,}\s", line):
            rep.error(line_no + k + 1, "Use '###' at most inside a section.")
    return {"part": "explanation", "half": half, "title": title, "rank": rank, "anchor": slugify(title),
            "line": line_no, "blocks": parse_blocks(body, line_no + 1, S, rep)}


def parse_body(lines, first_line, header, S, rep):
    topic_rank = header.get("rank")
    parts = S.part_list()
    halves_map = S.halves()
    lead, parts_raw = split_by_heading(lines, first_line, 1)
    if any(l.strip() for l in lead):
        rep.error(first_line, "Text before the first part. Every line belongs under a '#' part.")

    out = {"parts": [], "sections": [], "materials": [], "positions": [], "case": {},
           "why": [], "short": [], "unverified": [], "check": []}
    order_keys = [p[0] for p in parts]
    seen, last_index, halves = [], -1, []
    tier = S.tier_by_id.get(header.get("tier", ""))
    short_lo, short_hi = S.limits["short_lines"]

    for title, line_no, body in parts_raw:
        low = title.lower().strip()
        key, half = None, None
        if low in halves_map:
            key, half = "explanation", halves_map[low]
            halves.append(half)
        else:
            for pk, heading, _ in parts:
                if low == heading:
                    key = pk
        if key is None:
            names = ", ".join("'# %s'" % h for _, h, _ in parts)
            rep.error(line_no, "Unknown part '# %s'. The parts are, in order: %s." % (title, names))
            continue
        idx = order_keys.index(key)
        if idx < last_index:
            rep.error(line_no, "The part '# %s' is out of order." % title)
        if key in seen and key != "explanation":
            rep.error(line_no, "The part '# %s' appears twice." % title)
        seen.append(key)
        last_index = idx
        out["parts"].append({"key": key, "title": title, "half": half, "line": line_no})

        if key in ("explanation", "case", "positions", "materials"):
            plead, subs = split_by_heading(body, line_no + 1, 2)
            if any(l.strip() for l in plead):
                rep.error(line_no, "Under '# %s', every line belongs to a '##' heading." % title)
            if not subs:
                rep.error(line_no, "'# %s' has no '##' headings." % title)
            if key == "explanation":
                for st, sl, sb in subs:
                    out["sections"].append(section_record(half, st, sl, sb, topic_rank, S, rep))
            elif key == "case":
                names = [s[0].lower() for s in subs]
                want = [b.lower() for b in S.case_blocks]
                if names != want:
                    rep.error(line_no, "'# %s' holds %s, in that order."
                              % (title, ", ".join("'## %s'" % b for b in S.case_blocks)))
                for st, sl, sb in subs:
                    out["case"][st.lower()] = {"title": st, "line": sl, "blocks": parse_blocks(sb, sl + 1, S, rep)}
            elif key == "positions":
                if len(subs) > S.limits["positions"]:
                    rep.warn(line_no, "More than %d positions." % S.limits["positions"], "positions")
                for st, sl, sb in subs:
                    out["positions"].append(parse_position(st, sl, sb, S, rep))
            else:
                for st, sl, sb in subs:
                    out["materials"].append(parse_material(st, sl, sb, S, rep))
        else:
            for k, line in enumerate(body):
                if line.startswith("#"):
                    rep.error(line_no + k + 1, "'# %s' takes no headings inside it." % title)
            blocks = parse_blocks(body, line_no + 1, S, rep)
            text = "\n".join(b["text"] for b in blocks if b["type"] == "markdown")
            if key == "why":
                out["why"] = blocks
            elif key == "short":
                out["short"] = list_items(text)
                if not short_lo <= len(out["short"]) <= short_hi:
                    rep.warn(line_no, "The short version has %d lines. The standard asks for %d to %d."
                             % (len(out["short"]), short_lo, short_hi), "short")
            elif key == "unverified":
                items = list_items(text)
                out["unverified"] = items if items else [text.strip()]
                if not text.strip():
                    rep.error(line_no, "'# %s' is empty. Write 'None.' when nothing is unverified." % title)
            elif key == "check":
                out["check"] = list_items(text)
                if len(out["check"]) > S.limits["check_questions"]:
                    rep.warn(line_no, "More than %d questions in '# %s'." % (S.limits["check_questions"], title), "check")

    for pk, heading, required in parts:
        if required and pk not in seen:
            rep.error(first_line, "The part '# %s' is missing." % (heading[0].upper() + heading[1:]))
    covers = header.get("covers")
    if covers == "both" and sorted(halves) != ["problem", "solutions"]:
        rep.error(first_line, "covers: both needs '# %s' and '# %s'." % (S.parts["problem"], S.parts["solutions"]))
    if covers in ("problem", "solutions") and halves:
        rep.error(first_line, "Split the explanation into halves only when covers is both.")
    if halves and not (tier is not None and tier.updates):
        rep.error(first_line, "Only topics in a tier that updates others split the explanation into halves.")
    return out


# ---------------------------------------------------------------- inline scan

def walk_blocks(blocks):
    for b in blocks:
        yield b
        if b["type"] == "private":
            yield from walk_blocks(b["blocks"])


def all_block_lists(out):
    yield out["why"]
    for s in out["sections"]:
        yield s["blocks"]
    for v in out["case"].values():
        yield v["blocks"]
    for p in out["positions"]:
        yield from p["fields"].values()


def block_text(b):
    if b["type"] == "markdown":
        return b["text"]
    if b["type"] == "visual":
        return b["caption"]
    return ""


def scan_text(text, base, private, S, rep, topic_ids, question_ids, refs, tags=None):
    """The checks on one run of text: private tags outside private blocks, [public]
    without a link, links to unknown IDs, malformed links."""
    scan = CODE_SPAN_RE.sub(lambda m: " " * len(m.group(0)), text)   # a tag in backticks is code
    scan = scan.replace("\\|", "|")                                    # a table escapes [[ID|words]]

    def at(pos):
        return (base + scan[:pos].count("\n")) if base else 0

    for t in S.tag_re.finditer(scan):
        line = at(t.start())
        tag = t.group("tag")
        is_private = S.is_private_tag(tag)
        if tags is not None:
            tags.append({"tag": tag, "url": t.group("url"), "private": is_private})
        if is_private and not private:
            rep.error(line, "The private tag [%s] sits outside a ':::private' block." % tag, "private-tag")
        starts = [m.end() for m in re.finditer(r"\n\n|\n\s*(?:[-*]|\d+\.)\s", scan[:t.start()])]
        para_start = starts[-1] if starts else 0
        if S.tag_kind(tag) == "public" and not t.group("url") and "](http" not in scan[para_start:t.start()]:
            rep.warn(line, "[public] without a link. Write [public](https://...) or put the link next to the claim.", "public-link")
    for r in S.ref_re.finditer(scan):
        line = at(r.start())
        rid = r.group("id")
        if S.question_id_re.match(rid):
            refs["questions"].append(rid)
            if question_ids is not None and rid not in question_ids:
                rep.warn(line, "[[%s]] is not in %s." % (rid, S.paths["open_questions"]), "unknown-question")
        else:
            refs["topics"].append(rid)
            if topic_ids is not None and rid not in topic_ids:
                rep.warn(line, "[[%s]] is not in the topic map." % rid, "unknown-topic")
    for bad in BAD_REF_RE.finditer(scan):
        if not S.ref_re.fullmatch(bad.group(0)):
            rep.error(at(bad.start()), "'%s' is not a topic or question link. Write [[%s01]] or [[%s01]]."
                      % (bad.group(0), S.tiers[0].prefix, S.question_prefix), "bad-link")


def scan_inline(out, S, rep, topic_ids, question_ids):
    tags, refs, visuals = [], {"topics": [], "questions": []}, []
    texts = []
    for blocks in all_block_lists(out):
        for b in walk_blocks(blocks):
            if b["type"] == "visual":
                visuals.append(b)
            if b["type"] in ("markdown", "visual"):
                texts.append((block_text(b), b.get("private", False), b.get("line")))
            if b["type"] == "visual":
                texts.append((b["title"] + " " + b["alt"] + " " + b["credit"], b["private"], b["line"]))
    for t in out["short"] + out["check"] + out["unverified"]:
        texts.append((t, False, None))
    for m in out["materials"]:
        for v in m["fields"].values():
            texts.append((v, False, m["line"]))
    for text, private, base in texts:
        scan_text(text, base, private, S, rep, topic_ids, question_ids, refs, tags)
    return tags, refs, visuals


# ---------------------------------------------------------------- counting

def plain_words(text, S):
    text = S.ref_re.sub(lambda m: m.group("text") or m.group("id"), text)
    text = S.tag_re.sub("", text)
    text = re.sub(r"\]\([^)]*\)", "]", text)
    text = re.sub(r"^\s*\|?[\s:|-]+\|?\s*$", "", text, flags=re.M)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", text))


def blocks_words(blocks, S):
    return sum(plain_words(block_text(b), S) for b in walk_blocks(blocks))


def count_words(out, S):
    """Words in the explanation, the case part and the positions."""
    total = 0
    for s in out["sections"]:
        n = blocks_words(s["blocks"], S)
        s["words"] = n
        s["minutes"] = round(n / S.wpm, 1)
        total += n
    for v in out["case"].values():
        total += blocks_words(v["blocks"], S)
    for p in out["positions"]:
        total += plain_words(p["position"], S)
        for blocks in p["fields"].values():
            total += blocks_words(blocks, S)
    return total


# ---------------------------------------------------------------- visuals

def check_svg(svg, id_prefix, line, rep):
    text = svg.read_text(encoding="utf-8")
    name = svg.name
    if "viewBox" not in text:
        rep.error(line, "%s needs a viewBox." % name, "svg")
    for pattern, msg in [
        (r"<(script|style|image|foreignObject)\b", "no <script>, <style>, <image> or <foreignObject>"),
        (r"\b(?:fill|stroke|stop-color|color)=\"(?!none\"|currentColor\"|url\()|\bstyle=\"|(?:rgb|hsl|oklch)\(",
         "colours only through the v- classes, with no style attribute"),
        (r"font-family", "fonts only through the v- classes"),
        (r"(?:href|src)=\"https?:", "no links to outside files"),
    ]:
        if re.search(pattern, text):
            rep.error(line, "%s: %s." % (name, msg), "svg")
    prefix = id_prefix.lower() + "-"
    for i in re.findall(r"\bid=\"([^\"]+)\"", text):
        if not i.startswith(prefix):
            rep.error(line, "%s: the id '%s' must start with '%s'." % (name, i, prefix), "svg")


# ---------------------------------------------------------------- entry

def parse_topic(folder, S, ids=None):
    """Parse and check one topic folder. ids is (topic ids, question ids), read from the
    map and the open questions when not given."""
    folder = Path(folder)
    rep = Report(str(folder))
    path = folder / TOPIC_FILE
    if not path.exists():
        rep.error(0, "No %s in %s." % (TOPIC_FILE, folder))
        return {"path": str(path), "errors": rep.errors, "warnings": rep.warnings}
    raw = path.read_text(encoding="utf-8")
    lines = strip_comments(raw).splitlines()
    header, body_start = parse_header(lines, S, rep)
    check_header(header, folder, S, rep)
    out = parse_body(lines[body_start:], body_start + 1, header, S, rep)

    topic_ids, question_ids = ids if ids is not None else known_ids(S)
    tags, refs, visuals = scan_inline(out, S, rep, topic_ids, question_ids)

    for v in visuals:
        svg = folder / v["file"]
        if not svg.exists():
            rep.error(v["line"], "The visual file %s is not in the topic folder." % v["file"])
        else:
            check_svg(svg, header.get("id", ""), v["line"], rep)

    words = count_words(out, S)
    minutes = round(words / S.wpm)
    size = header.get("size")
    if size in S.sizes:
        lo, hi = S.sizes[size]
        if not lo <= words <= hi:
            rep.warn(1, "%d words is outside size %s (%d to %d)." % (words, size, lo, hi), "size")
    if header.get("rank") == "critical" and words:
        ctx = sum(s.get("words", 0) for s in out["sections"] if s["rank"] == "context")
        if ctx * 2 > sum(s.get("words", 0) for s in out["sections"]):
            rep.warn(1, "More than half of this critical topic sits in context sections.", "context-share")
    crit = [m for m in out["materials"] if m["rank"] == "critical"]
    cap = S.materials["critical_per_critical_topic"] if header.get("rank") == "critical" else S.materials["critical_per_topic"]
    if len(crit) > cap:
        rep.error(1, "%d critical materials. This topic allows %d." % (len(crit), cap), "critical-topic")
    if not out["materials"]:
        rep.error(1, "A topic needs at least one material.")
    if len(out["materials"]) > S.materials["per_topic"]:
        rep.warn(1, "%d materials. The ceiling is %d." % (len(out["materials"]), S.materials["per_topic"]), "materials-ceiling")
    ranks = [rank_index(m["rank"]) for m in out["materials"] if m["rank"] in RANKS]
    if ranks != sorted(ranks):
        rep.warn(1, "List materials in rank order: critical first, context last.", "material-order")

    return {
        "path": str(path),
        "header": header,
        "words": words,
        "minutes": minutes,
        "parts": out["parts"],
        "why": out["why"],
        "short": out["short"],
        "sections": out["sections"],
        "case": out["case"],
        "positions": out["positions"],
        "materials": out["materials"],
        "unverified": out["unverified"],
        "check": out["check"],
        "visuals": [{k: v[k] for k in ("file", "title", "job", "alt", "credit", "caption", "private")} for v in visuals],
        "refs": {"topics": sorted(set(refs["topics"])), "questions": sorted(set(refs["questions"]))},
        "tags": tags,
        "errors": rep.errors,
        "warnings": rep.warnings,
    }


def summary(t, S):
    h = t.get("header", {})
    lines = ["%s  %s" % (h.get("id", "?"), h.get("title", "?")),
             "  tier %s · rank %s · size %s · depth %s · cluster %s · %d words · %d min"
             % (h.get("tier"), h.get("rank"), h.get("size"), h.get("depth"), h.get("cluster"),
                t.get("words", 0), t.get("minutes", 0)),
             "  read first %s · checked %s" % (", ".join(h.get("read first", [])) or "none", h.get("checked"))]
    if "updates" in h or "covers" in h or "check again" in h:
        lines.append("  updates %s · covers %s · check again %s"
                     % (", ".join(h.get("updates", [])), h.get("covers"), h.get("check again", "not set")))
    lines.append("Parts: " + " / ".join(p["title"] for p in t.get("parts", [])))
    lines.append("Sections:")
    for s in t.get("sections", []):
        half = " [%s]" % s["half"] if s.get("half") else ""
        lines.append("  %-8s %-62s %4d words%s" % (s["rank"], s["title"][:62], s.get("words", 0), half))
    lines.append("Materials:")
    for m in t.get("materials", []):
        f = m["fields"]
        lines.append("  %-8s %s" % (m["rank"], m["title"]))
        lines.append("           %s · %s · %s · %s · %s min · checked %s%s"
                     % (f.get("type"), f.get("by"), f.get("date"), f.get("access"), m["minutes"],
                        f.get("checked"), " · vendor" if f.get("vendor") else ""))
        for key in ("link", "part", "what you get", "passed over", "steps"):
            if f.get(key):
                lines.append("           %s: %s" % (key, f[key].replace("\n", " ")[:110]))
    lines.append("Positions: " + " | ".join(p["position"] for p in t.get("positions", [])))
    lines.append("Visuals: " + ", ".join("%s%s" % (v["file"], " (private)" if v["private"] else "")
                                         for v in t.get("visuals", [])))
    private = [x["tag"] for x in t.get("tags", []) if x["private"]]
    public = [x["tag"] for x in t.get("tags", []) if not x["private"]]
    lines.append("Tags: %d private (%s) · %d other (%s)" % (len(private), ", ".join(private), len(public), ", ".join(public)))
    refs = t.get("refs", {"topics": [], "questions": []})
    lines.append("Links: topics %s · questions %s" % (", ".join(refs["topics"]), ", ".join(refs["questions"])))
    for e in t.get("errors", []):
        lines.append("ERROR   line %s: %s" % (e["line"], e["message"]))
    for w in t.get("warnings", []):
        lines.append("warning line %s: %s" % (w["line"], w["message"]))
    lines.append("%d errors, %d warnings" % (len(t.get("errors", [])), len(t.get("warnings", []))))
    return "\n".join(lines)
