"""Render the Markdown subset that engine/format.md allows, plus the guide's own
inline marks: topic links [[B04]], question links [[OQ-02]] and provenance tags
such as [source: field-notes] or [public](https://...).

Standard library only. The renderer is small on purpose: it handles what the
format allows and nothing else.
"""

import html
import re


def esc(text):
    return html.escape(text, quote=False)


def attr(text):
    return html.escape(text, quote=True)


class Context:
    """What the renderer needs to know about the rest of the guide."""

    def __init__(self, S, topics, questions, auto_private=False):
        self.S = S
        self.topics = topics          # id -> {"title", "href", "written"}
        self.questions = questions    # id -> {"title", "href"}
        self.auto_private = auto_private
        self.private_depth = 0


# ---------------------------------------------------------------- inline

def render_ref(m, ctx):
    rid, text = m.group("id"), m.group("text")
    if ctx.S.question_id_re.match(rid):
        q = ctx.questions.get(rid)
        title = q["title"] if q else "Open question"
        href = q["href"] if q else "questions.html"
        label = esc(text) if text else esc(rid)
        return '<a class="ref ref-q" href="%s" title="%s">%s</a>' % (attr(href), attr(title), label)
    t = ctx.topics.get(rid)
    if not t:
        return '<span class="ref ref-missing" title="Not in the topic map">%s</span>' % esc(text or rid)
    cls = "ref" if t["written"] else "ref ref-planned"
    tip = t["title"] if t["written"] else t["title"] + " (planned, not written yet)"
    if text:
        inner = esc(text)
    else:
        inner = '<span class="ref-id">%s</span> %s' % (esc(rid), esc(t["title"]))
    return '<a class="%s" href="%s" title="%s">%s</a>' % (cls, attr(t["href"]), attr(tip), inner)


def render_tag(m, ctx):
    tag, url = m.group("tag"), m.group("url")
    spec = ctx.S.tag_spec(tag)
    kind = spec.kind if spec else tag
    private = bool(spec and spec.private)
    cls = "tag tag-private" if private else "tag tag-%s" % re.sub(r"[^a-z]+", "-", kind.lower()).strip("-")
    title = spec.title if spec else ""
    label = "[%s]" % esc(tag)
    if url:
        return '<a class="%s" href="%s" title="%s" target="_blank" rel="noopener">%s</a>' % (
            cls, attr(url), attr(title), label)
    return '<span class="%s" title="%s">%s</span>' % (cls, attr(title), label)


def emphasis(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*(?![\s*])(.+?)(?<![\s*])\*(?![*\w])", r"<em>\1</em>", text)
    return text


def inline(text, ctx):
    held = []

    def keep(fragment):
        held.append(fragment)
        return "\x00%d\x00" % (len(held) - 1)

    text = re.sub(r"`([^`]+)`", lambda m: keep("<code>%s</code>" % esc(m.group(1))), text)
    text = ctx.S.ref_re.sub(lambda m: keep(render_ref(m, ctx)), text)
    text = ctx.S.tag_re.sub(lambda m: keep(render_tag(m, ctx)), text)

    def link(m):
        label, url = m.group(1), m.group(2)
        external = re.match(r"^https?://", url) is not None
        extra = ' target="_blank" rel="noopener"' if external else ""
        return keep('<a href="%s"%s>%s</a>' % (attr(url), extra, emphasis(esc(label))))

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = emphasis(esc(text))
    for _ in range(3):  # held fragments can hold other held fragments
        text = re.sub(r"\x00(\d+)\x00", lambda m: held[int(m.group(1))], text)
    return text


# ---------------------------------------------------------------- blocks

LIST_RE = re.compile(r"^(?P<indent>\s*)(?P<marker>[-*]|\d+\.)\s+(?P<text>.*)$")


def is_table_start(lines, i):
    return (lines[i].lstrip().startswith("|") and i + 1 < len(lines)
            and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]) is not None)


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    cells = re.split(r"(?<!\\)\|", line)
    return [c.strip().replace("\\|", "|") for c in cells]


def heading_id(title, prefix=""):
    return prefix + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]


def render(text, ctx, heading_level=4, anchor_prefix="", levels=None):
    """Render a Markdown string. '###' headings become <h{heading_level}>, or, when
    levels is given, <h{levels[depth]}> by the number of '#' marks."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.lstrip().startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("```"):
                j += 1
            out.append("<pre><code>%s</code></pre>" % esc("\n".join(lines[i + 1:j])))
            i = j + 1
            continue
        hm = re.match(r"^(#{1,6})\s+(.*)$", line)
        if hm:
            title = hm.group(2).strip()
            level = levels[len(hm.group(1))] if levels else heading_level
            out.append('<h%d id="%s">%s</h%d>' % (level, attr(heading_id(title, anchor_prefix)), inline(title, ctx), level))
            i += 1
            continue
        if is_table_start(lines, i):
            head = split_row(lines[i])
            j = i + 2
            rows = []
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            chunk = "\n".join(lines[i:j])
            body = ['<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>' %
                    "".join("<th>%s</th>" % inline(c, ctx) for c in head)]
            for r in rows:
                body.append("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c, ctx) for c in r))
            body.append("</tbody></table></div>")
            out.append(wrap_private("".join(body), chunk, ctx))
            i = j
            continue
        if line.lstrip().startswith(">"):
            j = i
            quoted = []
            while j < len(lines) and lines[j].lstrip().startswith(">"):
                quoted.append(re.sub(r"^\s*>\s?", "", lines[j]))
                j += 1
            chunk = "\n".join(quoted)
            out.append(wrap_private("<blockquote>%s</blockquote>" % render(chunk, ctx, heading_level, levels=levels), chunk, ctx))
            i = j
            continue
        if LIST_RE.match(line):
            j, items = i, []
            while j < len(lines):
                cur = lines[j]
                m = LIST_RE.match(cur)
                if m:
                    items.append({"indent": len(m.group("indent").replace("\t", "    ")),
                                  "ordered": m.group("marker")[0].isdigit(),
                                  "text": m.group("text")})
                    j += 1
                elif cur.strip() and cur.startswith("  ") and items:
                    items[-1]["text"] += " " + cur.strip()
                    j += 1
                elif not cur.strip() and j + 1 < len(lines) and (
                        LIST_RE.match(lines[j + 1]) or lines[j + 1].startswith("  ")):
                    j += 1
                else:
                    break
            chunk = "\n".join(lines[i:j])
            out.append(wrap_private(render_list(items, ctx), chunk, ctx))
            i = j
            continue
        j, para = i, []
        while j < len(lines) and lines[j].strip() and not (
                LIST_RE.match(lines[j]) or lines[j].lstrip().startswith(("```", ">", "#"))
                or is_table_start(lines, j)):
            para.append(lines[j].strip())
            j += 1
        if not para:
            para.append(lines[j].strip())
            j += 1
        chunk = " ".join(para)
        out.append(wrap_private(render_paragraph(chunk, ctx), chunk, ctx))
        i = j
    return "\n".join(out)


def render_paragraph(text, ctx):
    m = re.match(r"^\*\*([^*]+?)\.\*\*\s*(.*)$", text)
    leadins = ctx.S.leadins()
    if m and m.group(1).strip().lower() in leadins:
        kind = leadins[m.group(1).strip().lower()]
        return '<p class="leadin leadin-%s"><span class="leadin-label">%s</span> %s</p>' % (
            kind, esc(m.group(1).strip()), inline(m.group(2), ctx))
    return "<p>%s</p>" % inline(text, ctx)


def render_list(items, ctx):
    if not items:
        return ""
    base = items[0]["indent"]
    tag = "ol" if items[0]["ordered"] else "ul"
    html_out = ["<%s>" % tag]
    k = 0
    while k < len(items):
        item = items[k]
        sub = []
        k += 1
        while k < len(items) and items[k]["indent"] > base:
            sub.append(items[k])
            k += 1
        html_out.append("<li>%s%s</li>" % (inline(item["text"], ctx), render_list(sub, ctx) if sub else ""))
    html_out.append("</%s>" % tag)
    return "".join(html_out)


def wrap_private(fragment, source, ctx):
    """In auto-private mode, collapse any block that cites a private source."""
    if ctx.auto_private and ctx.private_depth == 0 and ctx.S.has_private_tag(source):
        return private_details(fragment, ctx.S.private_label)
    return fragment


def private_details(inner_html, label="", visuals=()):
    """A collapsed private block. visuals is [(number, title html)] for the visuals inside it:
    their titles are public (format.md), so the closed block shows them."""
    label_html = ' <span class="private-label">%s</span>' % esc(label) if label else ""
    vis_html = "".join('<span class="private-visual"><span class="visual-n">Visual %d</span> %s</span>' % (n, title)
                       for n, title in visuals)
    return ('<details class="private"><summary><span class="private-mark">Private</span>%s%s'
            '</summary><div class="private-body">%s</div></details>' % (label_html, vis_html, inner_html))
