"""Turn a parsed guide into the pages of the portal.

load() reads every source the settings name. build() renders every page and
writes the site. The checks in checks.py then read what build() wrote.
"""

import datetime
import html
import json
import re
import shutil
from pathlib import Path

from . import glossary, pages, topicmap
from . import render as md
from .settings import ENGINE, RANKS
from .topicfile import block_text, known_ids, parse_topic

ASSETS = ENGINE / "assets"
COVERS_LABEL = {"problem": "The problem", "solutions": "The solutions", "both": "The problem and the solutions"}
MAP_FIELD_LABEL = {"why": "Why this topic belongs", "starting questions": "Starting questions",
                   "visual": "Visual, a first guess", "prior art": "Earlier text to reuse"}
PRIVATE_TOGGLE = ('<button type="button" class="private-toggle" data-private-toggle aria-pressed="false">'
                  'Open all private facts</button>')
# Shown only on paper. site.js rewrites it before printing, with the count of closed blocks.
PRINT_NOTE = ('<p class="print-note" data-print-note>Private blocks print closed unless you open them before printing. '
              'A closed block prints its title only.</p>')
QUESTIONS_KEY = "questions"   # the open-questions page's key in the search index, beside the topic IDs

esc = md.esc
attr = md.attr


def fmt_min(minutes, approx=False):
    minutes = int(round(minutes))
    if minutes < 60:
        text = "%d min" % minutes
    else:
        h, m = divmod(minutes, 60)
        text = "%d h" % h + (" %d min" % m if m else "")
    return ("about " + text) if approx else text


class Site:
    """The parsed guide, and the pieces of HTML every page shares."""

    def __init__(self, S, share=False):
        self.S = S
        self.share = share   # a copy to share: every private block is left out

    # ---------------------------------------------------------------- loading

    def load(self):
        S = self.S
        tmap = topicmap.parse_topic_map(S)
        gloss = glossary.parse(S)
        questions = topicmap.parse_questions(S)
        ids = known_ids(S)

        written, problems = {}, []
        for f in sorted(S.content.glob("*/*/topic.md")) if S.content.exists() else []:
            if f.parent.parent.name not in S.tier_ids:
                problems.append("%s sits in a folder that isn't a tier, so the build skips it." % f.parent)
                continue
            t = parse_topic(f.parent, S, ids)
            tid = t.get("header", {}).get("id")
            if not tid:
                problems.append("%s has no id and was skipped." % f.parent)
                continue
            if tid in written:
                problems.append("%s and %s both say id %s. The build shows the first." % (written[tid]["folder"], f.parent, tid))
                continue
            t["folder"] = f.parent
            written[tid] = t

        topics = {}
        for tid in tmap["order"]:
            entry = tmap["topics"][tid]
            topics[tid] = {"id": tid, "title": entry["title"], "tier": entry["tier"],
                           "group": entry["group"], "rank": entry["rank"], "size": entry["size"],
                           "map": entry, "parsed": None}
        for tid, t in written.items():
            h = t["header"]
            if tid not in topics:
                topics[tid] = {"id": tid, "title": h.get("title", tid), "tier": h.get("tier", ""),
                               "group": "Not in the topic map", "rank": h.get("rank"), "size": h.get("size"),
                               "map": None, "parsed": None}
                problems.append("%s is written but not in the topic map." % tid)
            topics[tid]["parsed"] = t
            topics[tid]["title"] = h.get("title", topics[tid]["title"])
            topics[tid]["rank"] = h.get("rank", topics[tid]["rank"])
            topics[tid]["size"] = h.get("size", topics[tid]["size"])
            if h.get("tier") in S.tier_ids:
                topics[tid]["tier"] = h["tier"]

        for t in topics.values():
            t["href"] = t["id"].lower() + ".html"
            t["written"] = t["parsed"] is not None
            t["minutes"] = t["parsed"].get("minutes", 0) if t["written"] else topicmap.estimate_minutes(t["size"], S)

        groups = {key: [] for key in S.tier_ids}
        for tier in tmap["tiers"]:
            groups[tier["key"]] = [{"name": g["name"], "ids": list(g["ids"])} for g in tier["groups"]]
        for tid, t in topics.items():
            if t["map"] is None and t["tier"] in groups:
                groups[t["tier"]].append({"name": t["group"], "ids": [tid]})

        # The pages without parts: the tier introductions, the home page text, the open-questions page.
        page_files = {}
        for tier in S.tier_ids:
            path = S.intro(tier)
            if path.exists():
                page_files["intro-" + tier] = pages.parse_page(path, S, ids)
        for name, key in (("home", "home"), ("questions", "questions_page")):
            path = S.file(key)
            if path.exists():
                page_files[name] = pages.parse_page(path, S, ids, id_prefix=name)
        qpage = page_files.get("questions")
        if qpage:
            qpage["title"], qpage["blocks"] = split_title(qpage["blocks"])
            qpage["levels"] = pages.heading_levels(qpage["blocks"])
            qpage["chunks"] = pages.question_chunks(qpage["blocks"], S)
        if page_files.get("home"):
            hp = page_files["home"]
            hp["title"], hp["blocks"] = split_title(hp["blocks"])
            hp["levels"] = pages.heading_levels(hp["blocks"])

        q_ctx = {qid: {"title": q["title"], "href": "questions.html#" + qid.lower()} for qid, q in questions.items()}
        for c in (qpage or {}).get("chunks", []):
            # The page's own wording of a question becomes the tooltip of every link to it.
            if c["qid"] and c["title"]:
                q_ctx.setdefault(c["qid"], {"href": "questions.html#" + c["qid"].lower()})["title"] = c["title"]
        t_ctx = {tid: {"title": t["title"], "href": t["href"], "written": t["written"]} for tid, t in topics.items()}
        self.map, self.questions, self.topics, self.glossary = tmap, questions, topics, gloss
        self.groups, self.q_ctx, self.t_ctx, self.problems = groups, q_ctx, t_ctx, problems
        self.page_files, self.visuals = page_files, []
        self.built = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        return self

    def ctx(self, auto_private=False):
        return md.Context(self.S, self.t_ctx, self.q_ctx, auto_private=auto_private, share=self.share)

    def tier_ids(self, tier):
        return [tid for g in self.groups[tier] for tid in g["ids"]]

    def real_topics(self):
        """Topics in the map, in a tier the settings know."""
        return {k: v for k, v in self.topics.items() if v["tier"] in self.S.tier_ids and v["map"] is not None}

    # ---------------------------------------------------------------- small pieces

    def rank_chip(self, rank, extra=""):
        if rank not in RANKS:
            return '<span class="rank rank-unknown">No rank</span>'
        return '<span class="rank rank-%s">%s</span>%s' % (rank, esc(self.S.rank_label(rank)), extra)

    def rank_glyph(self, rank):
        label = esc(self.S.rank_label(rank))
        return '<span class="rank-glyph rank-%s" title="%s"><span class="vh">%s</span></span>' % (rank, label, label)

    def size_span(self, size):
        band = self.S.size_band(size or "")
        return '<span%s>Size %s</span>' % (' title="%s"' % attr(band) if band else "", esc(size or "?"))

    def action(self, rank):
        return self.S.ranks.get(rank, {}).get("action", "")

    # ---------------------------------------------------------------- page chrome

    def page(self, title, body, kind, current_tier=None, rail="", toc="", body_attrs=None):
        S = self.S
        nav = []
        for t in S.tiers:
            cur = ' aria-current="page"' if t.id == current_tier else ""
            nav.append('<a href="%s.html"%s>%s</a>' % (t.id, cur, esc(t.name)))
        secondary = [("topics.html", "All topics", "topics"), ("materials.html", "Materials", "materials"),
                     ("visuals.html", "Visuals", "visuals"), ("glossary.html", "Glossary", "glossary"),
                     ("questions.html", "Open questions", "questions"), ("notes.html", "My notes", "notes")]
        sec = "".join('<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if kind == k else "", label)
                      for href, label, k in secondary)
        attrs = " ".join('data-%s="%s"' % (k, attr(str(v))) for k, v in (body_attrs or {}).items())
        search = "" if kind == "search" else (
            '<form class="masthead-search" action="search.html" method="get" role="search">'
            '<label class="vh" for="masthead-q">Search the guide</label>'
            '<input id="masthead-q" type="search" name="q" placeholder="Search" autocomplete="off"></form>')
        layout_cls = "layout" + (" has-rail" if rail else "") + (" has-toc" if toc else "")
        config = json.dumps(S.js_config(), ensure_ascii=False).replace("</", "<\\/")
        footer_note = '<p>%s</p>' % esc(S.portal["footer_note"]) if S.portal["footer_note"] else ""
        if self.share:
            footer_note = '<p class="share-note">This copy leaves out every private block.</p>' + footer_note
        return """<!doctype html>
<html lang="%(lang)s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive">
<title>%(title)s</title>
<script>window.GUIDE=%(config)s;(function(){try{var d=document.documentElement,k=window.GUIDE.key,t=localStorage.getItem(k+'-theme');if(t==='light'||t==='dark'){d.setAttribute('data-theme',t);}if(localStorage.getItem(k+'-hide-context')==='1'){d.classList.add('hide-context');}}catch(e){}})();</script>
<link rel="stylesheet" href="assets/tokens.css">
<link rel="stylesheet" href="assets/visuals.css">
<link rel="stylesheet" href="assets/site.css">
</head>
<body class="page-%(kind)s" data-page="%(kind)s" %(attrs)s>
<a class="skip" href="#main">Skip to the text</a>
<header class="masthead">
  <div class="masthead-inner">
    <a class="wordmark" href="index.html"><span class="wordmark-mark" aria-hidden="true"></span>%(wordmark)s</a>
    <nav class="tiers" aria-label="Tiers">%(nav)s</nav>
    <nav class="secondary" aria-label="Indexes">%(sec)s</nav>
    %(search)s
    <button class="theme-toggle" type="button" data-theme-toggle>Theme: auto</button>
  </div>
</header>
<div class="%(layout)s">
%(rail)s
<main id="main" class="main">
%(body)s
</main>
%(toc)s
</div>
<footer class="colophon">
  <p>Built %(built)s. To rebuild, run <code>python3 engine/build.py</code>.</p>
  %(footer_note)s
</footer>
<script src="assets/notes.js"></script>
<script src="assets/site.js"></script>
</body>
</html>
""" % {"lang": attr(S.language), "title": esc(title), "config": config, "kind": kind, "attrs": attrs,
           "wordmark": esc(S.title), "nav": "".join(nav), "sec": sec, "layout": layout_cls, "rail": rail,
           "body": body, "toc": toc, "built": esc(self.built), "footer_note": footer_note, "search": search}

    def topic_row(self, t, show_tier=False):
        status = "written" if t["written"] else "planned"
        time = fmt_min(t["minutes"], approx=not t["written"])
        marks = []
        entry = t["map"] or {}
        if entry.get("pilot"):
            marks.append('<span class="mark">Pilot</span>')
        if entry.get("read_first_flag"):
            marks.append('<span class="mark">Read first</span>')
        if entry.get("ages_fast"):
            marks.append('<span class="mark">Ages fast</span>')
        if t["written"] and t["parsed"].get("errors"):
            marks.append('<span class="mark mark-warn">Format errors</span>')
        tier = '<span class="trow-tier">%s</span>' % esc(self.S.tier_label(t["tier"])) if show_tier else ""
        return ('<li class="trow is-%(status)s" data-topic-id="%(id)s" data-rank="%(rank)s" data-status="%(status)s">'
                '<a class="trow-link" href="%(href)s"><span class="trow-id">%(id)s</span>'
                '<span class="trow-title">%(title)s</span></a>'
                '<span class="trow-meta"><span class="trow-rank">%(chip)s</span><span class="trow-time">%(time)s</span>'
                '<span class="status status-%(status)s">%(slabel)s</span><span class="trow-extra">%(tier)s%(marks)s</span></span></li>') % {
            "status": status, "id": t["id"], "rank": t["rank"], "href": t["href"], "title": esc(t["title"]),
            "chip": self.rank_chip(t["rank"]), "time": time, "slabel": status.capitalize(), "tier": tier,
            "marks": "".join(marks)}

    def filters(self, statuses=True):
        ranks = "".join('<button type="button" class="filter rank-%s" data-filter="rank" data-value="%s" aria-pressed="false">%s</button>'
                        % (r, r, esc(self.S.rank_label(r))) for r in ["critical", "high", "medium"])
        status = ('<span class="filters-sep" aria-hidden="true"></span>'
                  '<button type="button" class="filter" data-filter="status" data-value="written" aria-pressed="false">Written only</button>') if statuses else ""
        return ('<div class="filters" role="group" aria-label="Filter topics"><span class="filters-label">Show</span>%s%s'
                '<button type="button" class="filter-reset" data-filter-reset hidden>Show all</button></div>' % (ranks, status))

    def rail_for(self, tier, current):
        S = self.S
        out = ['<nav class="rail" aria-label="Topics in %s"><p class="rail-tier"><a href="%s.html">%s</a></p>'
               % (esc(S.tier_label(tier)), tier, esc(S.tier_label(tier)))]
        for g in self.groups[tier]:
            out.append('<p class="rail-group">%s</p><ul>' % esc(g["name"]))
            for tid in g["ids"]:
                t = self.topics[tid]
                cur = ' aria-current="page"' if tid == current else ""
                cls = "rail-item" + ("" if t["written"] else " is-planned")
                out.append('<li class="%s" data-topic-id="%s"><a href="%s"%s>%s<span class="rail-id">%s</span>'
                           '<span class="rail-title">%s</span></a></li>'
                           % (cls, tid, t["href"], cur, self.rank_glyph(t["rank"]), tid, esc(t["title"])))
            out.append("</ul>")
        out.append("</nav>")
        return "".join(out)

    def pager(self, t):
        ids = self.tier_ids(t["tier"]) if t["tier"] in self.groups else []
        if t["id"] not in ids:
            return ""
        i = ids.index(t["id"])
        out = ['<nav class="pager" aria-label="Previous and next topic">']
        if i > 0:
            p = self.topics[ids[i - 1]]
            out.append('<a class="pager-prev" href="%s"><span>Previous</span>%s %s</a>' % (p["href"], p["id"], esc(p["title"])))
        if i + 1 < len(ids):
            n = self.topics[ids[i + 1]]
            out.append('<a class="pager-next" href="%s"><span>Next</span>%s %s</a>' % (n["href"], n["id"], esc(n["title"])))
        out.append("</nav>")
        return "".join(out)

    def private_actions(self, body):
        """The open-all control and the print note, for a page that holds private blocks."""
        if '<details class="private"' not in body:
            return ""
        return '<p class="topic-actions">%s</p>%s' % (PRIVATE_TOGGLE, PRINT_NOTE)

    def page_renderer(self, page, kind):
        """A renderer for a page without parts. Its visuals stay off the visual index."""
        r = TopicRenderer(self, {"parsed": {"folder": Path(page["path"]).parent, "header": {}}, "no_index": True, "id": kind})
        r.levels = page["levels"]
        return r

    # ---------------------------------------------------------------- planned topics

    def planned_page(self, t):
        S, ctx = self.S, self.ctx(auto_private=True)
        entry = t["map"]
        deps = entry["after"]
        if deps:
            first = ", ".join(md.inline("[[%s]]" % d, ctx) for d in deps)
        elif entry["read_first_flag"]:
            first = "Nothing. Read this topic before the others."
        else:
            first = "Nothing. It stands alone."
        facts = [("Read first", first)]
        if entry["updates"]:
            facts.append(("Updates", ", ".join(md.inline("[[%s]]" % d, ctx) for d in entry["updates"])))
        if entry["ages_fast"]:
            facts.append(("Freshness", "Its facts age fast."))
        facts.append(("Cluster", esc(entry["cluster"])))
        dl = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (k, v) for k, v in facts)
        meta = [self.rank_chip(t["rank"]), self.size_span(t["size"]),
                '<span>%s of reading</span>' % fmt_min(t["minutes"], approx=True), '<span class="status status-planned">Planned</span>']
        head = ('<header class="topic-head"><p class="crumbs"><a href="%s.html">%s</a><span>%s</span></p>'
                '<h1><span class="topic-id">%s</span> %s</h1><p class="topic-meta">%s</p><dl class="topic-facts">%s</dl></header>') % (
            t["tier"], esc(S.tier_label(t["tier"])), esc(t["group"]), t["id"], esc(t["title"]), "".join(meta), dl)
        note = ('<div class="banner banner-planned"><p><strong>Not written yet.</strong> This page shows the topic\'s entry in the '
                'topic map, written before any research. Its questions are starting points, and the writer can replace them.</p></div>')
        parts, leads = [], ""
        for label, text in entry["fields"]:
            text = re.sub(r"`(\[[^`\]]+\](?:\([^)`]+\))?)`", r"\1", text)   # a map can write tags as code
            low = label.lower()
            if low == "seeds":
                leads = ('<details class="leads"><summary>Research leads. Nobody has verified them.</summary>%s</details>'
                         % md.render(text, ctx))
                continue
            parts.append('<section class="part"><h2 class="part-title">%s</h2>%s</section>'
                         % (esc(MAP_FIELD_LABEL.get(low, label)), md.render(text, ctx)))
        inner = "".join(parts) + leads
        if '<details class="private"' in inner:
            head = head.replace("</dl></header>", '</dl><p class="topic-actions">%s</p>%s</header>' % (PRIVATE_TOGGLE, PRINT_NOTE))
        return '<article class="topic topic-planned">%s%s%s%s</article>' % (head, note, inner, self.pager(t))

    # ---------------------------------------------------------------- home

    def time_note(self):
        S = self.S
        bands = "; ".join("%s, %s to %s%s" % (k, format(S.sizes[k][0], ","), format(S.sizes[k][1], ","), " words" if k == "S" else "")
                          for k in ("S", "M", "L"))
        return ('<p>Reading time is words divided by %d a minute. Written topics are counted. Planned topics are estimated '
                'at the middle of their size, so the totals change as topics are written. The sizes are %s; and XL, %s to %s, '
                'for a few exceptions.</p>' % (S.wpm, bands, format(S.sizes["XL"][0], ","), format(S.sizes["XL"][1], ",")))

    def home_parts(self):
        S, topics = self.S, self.topics
        real = self.real_topics()
        written = [t for t in real.values() if t["written"]]
        steps, seen = [], set()
        for step in self.map["reading"]:
            rows = "".join(self.topic_row(topics[i], show_tier=True) for i in step["ids"] if i in topics)
            seen.update(step["ids"])
            note = step["note"][:1].upper() + step["note"][1:].rstrip(".")
            steps.append('<li class="step"><p class="step-note"><span class="step-n">%d</span>%s</p><ol class="trows">%s</ol></li>'
                         % (step["step"], esc(note), rows))
        rest = {r: [t for tid, t in real.items() if tid not in seen and t["rank"] == r] for r in ("critical", "high", "medium")}
        later = []
        for r, label in (("critical", "Other critical topics"), ("high", "Then the other high topics"), ("medium", "Then the medium topics")):
            if rest[r]:
                later.append('<details class="later"><summary>%s <span class="count">%d</span></summary><ol class="trows">%s</ol></details>'
                             % (label, len(rest[r]), "".join(self.topic_row(t, show_tier=True) for t in rest[r])))
        if not steps and not later and real:
            later.append('<ol class="trows">%s</ol>' % "".join(self.topic_row(t, show_tier=True) for t in real.values()))

        def totals_row(label, items, key, is_total=False):
            w = [t for t in items if t["written"]]
            total = sum(t["minutes"] for t in items)
            return ('<tr%s><th scope="row">%s</th><td>%d</td><td>%d</td><td data-total="%s-written" data-minutes="%d">%s</td>'
                    '<td data-total="%s-all" data-minutes="%d">%s</td></tr>') % (
                ' class="is-total"' if is_total else "", esc(label), len(items), len(w), key, sum(t["minutes"] for t in w),
                fmt_min(sum(t["minutes"] for t in w)), key, total, fmt_min(total, approx=len(w) < len(items)))

        tier_rows = "".join(totals_row(t.name, [x for x in real.values() if x["tier"] == t.id], "tier-" + t.id) for t in S.tiers)
        tier_rows += totals_row("All tiers", list(real.values()), "all", is_total=True)
        rank_tot = "".join(totals_row(S.rank_label(r), [t for t in real.values() if t["rank"] == r], "rank-" + r)
                           for r in RANKS if any(t["rank"] == r for t in real.values()))

        mats = [m for t in written for m in t["parsed"]["materials"]]

        def your_time(r):
            ms = [m["minutes"] or 0 for m in mats if m["rank"] == r]
            cap = S.ranks[r]["reader_minutes"]
            if cap == "full":
                return fmt_min(sum(ms))
            if cap == "optional" or not cap:
                return "Optional"
            return "up to " + fmt_min(sum(min(x, cap) for x in ms)) if ms else fmt_min(0)

        mat_rows = "".join('<tr><th scope="row">%s</th><td>%d</td><td data-total="mat-%s" data-minutes="%d">%s</td><td>%s</td><td>%s</td></tr>' % (
            esc(S.rank_label(r)), len([m for m in mats if m["rank"] == r]), r,
            sum(m["minutes"] or 0 for m in mats if m["rank"] == r),
            fmt_min(sum(m["minutes"] or 0 for m in mats if m["rank"] == r)), esc(self.action(r)), your_time(r)) for r in RANKS)

        tiers = "".join(
            '<li><a href="%s.html"><span class="tier-name">%s</span><span class="tier-q">%s</span>'
            '<span class="tier-count">%d topics, %d written</span></a></li>' % (
                tr["key"], esc(tr["name"]), esc(tr["question"]),
                len([t for t in real.values() if t["tier"] == tr["key"]]),
                len([t for t in written if t["tier"] == tr["key"]])) for tr in self.map["tiers"])
        status = ('<p class="home-status"><strong>%d of %d topics written.</strong> The rest show their plan from the topic map. '
                  '<span data-progress data-written="%s"></span></p>') % (
            len(written), len(real), " ".join(sorted(t["id"] for t in written)))
        tables = """
  <div class="table-wrap"><table class="totals"><thead><tr><th>Tier</th><th>Topics</th><th>Written</th><th>Written, reading time</th><th>All topics</th></tr></thead><tbody>%s</tbody></table></div>
  <div class="table-wrap"><table class="totals"><thead><tr><th>Topic rank</th><th>Topics</th><th>Written</th><th>Written, reading time</th><th>All topics</th></tr></thead><tbody>%s</tbody></table></div>
  <div class="table-wrap"><table class="totals"><thead><tr><th>Materials in written topics</th><th>Count</th><th>Listed time</th><th>What you do</th><th>Your time</th></tr></thead><tbody>%s</tbody></table></div>
""" % (tier_rows, rank_tot, mat_rows)
        n = len(S.tiers)
        words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
        heading = "The tier" if n == 1 else "The %s tiers" % words.get(n, str(n))
        return {"status": status, "steps": "".join(steps), "later": "".join(later), "tiers": tiers, "tables": tables,
                "tiers_heading": heading}

    def home_page(self):
        S = self.S
        p = self.home_parts()
        start = """
<section class="home-sec" id="start">
  <h2>Where to start</h2>
  <p>Read the critical topics first, in this order. Each step leans on the one before it.</p>
  <ol class="steps">%(steps)s</ol>
  %(later)s
</section>

<section class="home-sec" id="tiers">
  <h2>%(tiers_heading)s</h2>
  <ul class="tier-cards">%(tiers)s</ul>
</section>
""" % p
        time = """
<section class="home-sec" id="time">
  <h2>How long it takes</h2>
  %s
  %s
</section>
""" % (self.time_note(), p["tables"])
        hp = self.page_files.get("home")
        if hp:
            # The text says what the guide is, how the ranks work and what the private blocks are,
            # so the page drops the built-in versions of those.
            text = self.page_renderer(hp, "home").blocks(hp["blocks"], "about-")
            title = md.inline(hp["title"], self.ctx()) if hp.get("title") else esc(S.title)
            return """
<header class="home-head">
  <h1>%s</h1>
  %s
  %s
</header>

<section class="home-text">%s</section>
%s%s""" % (title, p["status"], self.private_actions(text), text, start, time)

        rank_table = "".join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            self.rank_chip(r), esc(S.ranks[r]["topic"]), esc(S.ranks[r]["material"])) for r in RANKS)
        lead = '<p class="lead">%s</p>' % esc(S.description) if S.description else ""
        has_private = any(t.private for t in S.tags)
        private = ("""
<section class="home-sec" id="private">
  <h2>Private facts</h2>
  <p>Facts from private sources sit in blocks marked <span class="private-inline">Private</span>, closed until you open them. Each fact carries a tag that names its source. Hover over a tag to see what it means.</p>
</section>
""") if has_private else ""
        return """
<header class="home-head">
  <h1>%(title)s</h1>
  %(lead)s
  %(status)s
</header>
%(start)s
<section class="home-sec" id="ranks">
  <h2>How the ranks work</h2>
  <p>Every topic, section and material has a rank. You read the guide's own text in full. A material's rank tells you how much of your time it deserves.</p>
  <div class="table-wrap"><table class="rank-table"><thead><tr><th>Rank</th><th>A topic or section</th><th>A material, and what you do with it</th></tr></thead><tbody>%(rank_table)s</tbody></table></div>
</section>
%(time)s%(private)s""" % {"title": esc(S.title), "lead": lead, "status": p["status"], "start": start,
                          "rank_table": rank_table, "time": time, "private": private}

    # ---------------------------------------------------------------- tiers and indexes

    def tier_page(self, tier):
        S = self.S
        tr = next(x for x in self.map["tiers"] if x["key"] == tier)
        ids = self.tier_ids(tier)
        real = [self.topics[i] for i in ids if self.topics[i]["map"] is not None]
        total = sum(t["minutes"] for t in real)
        nwritten = len([t for t in real if t["written"]])
        intro_page = self.page_files.get("intro-" + tier)
        if intro_page:
            r = TopicRenderer(self, {"parsed": {"folder": S.content / tier, "header": {}}, "intro_tier": tier})
            intro = '<section class="tier-map">%s</section>' % r.blocks(intro_page["blocks"])
        else:
            intro = ('<section class="tier-map tier-map-empty"><p>%s</p><p class="note">%s</p></section>'
                     % (esc(tr["blurb"]), esc(S.portal["tier_map_pending"])))
        groups = []
        for g in self.groups[tier]:
            rows = "".join(self.topic_row(self.topics[i]) for i in g["ids"])
            groups.append('<section class="group" data-filter-group><h2>%s</h2><ol class="trows">%s</ol></section>' % (esc(g["name"]), rows))
        if not groups:
            groups.append('<p class="note">The topic map has no topics in this tier yet.</p>')
        definition = S.tier_by_id[tier].definition
        return """
<header class="tier-head">
  <h1>%(name)s</h1>
  <p class="tier-question">%(q)s</p>
  %(def)s
  <p class="tier-stats">%(n)d topics · %(w)d written · %(time)s of reading</p>
</header>
%(intro)s
<div data-filterable>
%(filters)s
%(groups)s
</div>
""" % {"name": esc(tr["name"]), "q": esc(tr["question"]),
       "def": ('<blockquote class="tier-def"><p>“%s”</p><footer>%s</footer></blockquote>'
               % (esc(definition), esc(S.portal["definition_label"]))) if definition else "",
       "n": len(real), "w": nwritten, "time": fmt_min(total, approx=nwritten < len(real)),
       "intro": intro, "filters": self.filters(), "groups": "".join(groups)}

    def topics_page(self):
        S, out = self.S, []
        for tier in S.tier_ids:
            rows = []
            for g in self.groups[tier]:
                for tid in g["ids"]:
                    t = self.topics[tid]
                    if t["map"] is None:
                        continue
                    e = t["map"]
                    deps = ", ".join(md.inline("[[%s]]" % d, self.ctx()) for d in e["after"]) or ""
                    notes = [x for x in (("Pilot" if e["pilot"] else ""), ("Read first" if e["read_first_flag"] else ""),
                                         ("Ages fast" if e["ages_fast"] else "")) if x]
                    if e["updates"]:
                        notes.append("Updates " + ", ".join(e["updates"]))
                    rows.append(('<tr data-topic-id="%s" data-rank="%s" data-status="%s"><td class="c-id">%s</td>'
                                 '<td class="c-title"><a href="%s">%s</a><span class="c-group">%s</span></td><td>%s</td><td>%s</td>'
                                 '<td>%s</td><td><span class="status status-%s">%s</span></td><td>%s</td><td>%s</td><td>%s</td></tr>') % (
                        tid, t["rank"], "written" if t["written"] else "planned", tid, t["href"], esc(t["title"]), esc(g["name"]),
                        self.rank_chip(t["rank"]), esc(t["size"]), fmt_min(t["minutes"], approx=not t["written"]),
                        "written" if t["written"] else "planned", "Written" if t["written"] else "Planned",
                        esc(e["cluster"]), deps, esc(" · ".join(notes))))
            out.append('<section class="group" data-filter-group><h2>%s</h2><div class="table-wrap"><table class="map-table">'
                       '<thead><tr><th>ID</th><th>Topic</th><th>Rank</th><th>Size</th><th>Time</th><th>Status</th><th>Cluster</th>'
                       '<th>After</th><th>Notes</th></tr></thead><tbody>%s</tbody></table></div></section>'
                       % (esc(S.tier_label(tier)), "".join(rows)))
        return """
<header class="index-head">
  <h1>All topics</h1>
  <p class="lead">Every topic in the topic map, in its order. Written topics open their page. Planned topics open their entry in the map, so you can judge the plan.</p>
</header>
<div data-filterable>%s%s</div>
""" % (self.filters(), "".join(out))

    def materials_page(self):
        S, ctx = self.S, self.ctx()
        rows = {r: [] for r in RANKS}
        for tid in self.map["order"]:
            t = self.topics[tid]
            if not t["written"]:
                continue
            for m in t["parsed"]["materials"]:
                if m["rank"] in rows:
                    rows[m["rank"]].append((t, m))
        out = []
        for r in RANKS:
            items, lis = rows[r], []
            for t, m in items:
                f = m["fields"]
                title = md.inline(m["title"], ctx)
                if f.get("link"):
                    title = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (attr(f["link"]), title)
                lis.append('<li class="material rank-%s"><p class="mat-title-line">%s</p><p class="mat-meta">%s · %s · %s · from %s</p><p class="mat-get">%s</p></li>' % (
                    r, title, esc(f.get("type", "").capitalize()), esc(f.get("time", "")), md.inline(f.get("by", ""), ctx),
                    md.inline("[[%s]]" % t["id"], ctx), md.inline(f.get("what you get", ""), ctx)))
            minutes = sum(m["minutes"] or 0 for _, m in items)
            out.append('<section class="group"><p class="sec-meta">%s<span class="sec-time">%s</span></p><h2>%d %s material%s, %s</h2>%s</section>' % (
                self.rank_chip(r), esc(self.action(r)), len(items), esc(S.rank_label(r).lower()), "" if len(items) == 1 else "s", fmt_min(minutes),
                ('<ol class="materials">%s</ol>' % "".join(lis)) if lis else '<p class="note">None in the written topics yet.</p>'))
        return """
<header class="index-head">
  <h1>Materials</h1>
  <p class="lead">Every material from the written topics, by rank. Read the critical ones in full; skim the high and medium ones.</p>
</header>
%s
""" % "".join(out)

    # ---------------------------------------------------------------- open questions

    def question_refs(self):
        """Question ID -> the written topics that link to it."""
        refs = {}
        for t in self.topics.values():
            if t["written"]:
                for q in t["parsed"]["refs"]["questions"]:
                    if t["id"] not in refs.setdefault(q, []):
                        refs[q].append(t["id"])
        return refs

    def anchor_first_mention(self, fragment, qids):
        """For a question the page never opens on a line of its own, put its anchor on the
        first mention of its ID in the text, outside any link. When that mention sits in a
        private block, the anchor goes on the closed block itself: a browser opens a closed
        block to show a target inside it, and a link must not open a private fact."""
        want = set(qids)
        parts = re.split(r"(<[^>]+>)", fragment)
        in_link, private = 0, []
        for k, part in enumerate(parts):
            if part.startswith("<"):
                if re.match(r"<a\b", part):
                    in_link += 1
                elif part.startswith("</a"):
                    in_link = max(0, in_link - 1)
                elif part.startswith("<details"):
                    private.append(k if 'class="private"' in part else None)
                elif part.startswith("</details") and private:
                    private.pop()
                continue
            if in_link or not want:
                continue

            def sub(m):
                qid = m.group(1)
                if qid not in want:
                    return qid
                want.discard(qid)
                holder = next((i for i in reversed(private) if i is not None), None)
                if holder is not None and " id=" not in parts[holder]:
                    parts[holder] = parts[holder].replace('<details class="private"', '<details class="private" id="%s"' % qid.lower(), 1)
                    return qid
                return '<span class="q-anchor" id="%s">%s</span>' % (qid.lower(), qid)
            parts[k] = re.sub(r"(?<![\w-])(%s)(?!\w)" % self.S.question_id_pattern, sub, part)
        fragment = "".join(parts)
        if self.share and want:
            fragment = self.anchor_omitted(fragment, want)
        return fragment

    def anchor_omitted(self, fragment, qids):
        """In a shared copy, a question named only inside a private block gets its anchor on
        the block's stub, which lists the questions the block named."""
        for qid in sorted(qids):
            m = re.search(r'(<div class="private private-stub private-omitted" data-questions="[^"]*\b%s\b[^"]*">)' % re.escape(qid), fragment)
            if m:
                fragment = fragment[:m.end()] + '<span class="q-anchor" id="%s"></span>' % qid.lower() + fragment[m.end():]
        return fragment

    def questions_page(self):
        S = self.S
        refs = self.question_refs()
        ctx = self.ctx()
        qp = self.page_files.get("questions")
        if qp:
            r = self.page_renderer(qp, "questions")
            out, seen = [], set()
            for c in qp["chunks"]:
                inner = r.blocks(c["blocks"], "q-")
                qid = c["qid"]
                if qid and qid not in seen:
                    seen.add(qid)
                    cited = ", ".join(md.inline("[[%s|%s]]" % (i, i), ctx) for i in sorted(refs.get(qid, [])))
                    cited = '<p class="q-refs">Cited in %s</p>' % cited if cited else ""
                    out.append('<section class="oq" id="%s">%s%s</section>' % (qid.lower(), inner, cited))
                else:
                    if qid:
                        self.problems.append("%s opens %s twice. Links go to the first." % (S.paths["questions_page"], qid))
                    out.append(inner)
            body = "".join(out)
            unopened = [q for q in sorted(set(self.questions) | set(refs)) if q not in seen]
            if unopened:
                body = self.anchor_first_mention(body, unopened)
            title = md.inline(qp["title"], ctx) if qp.get("title") else "Open questions"
            return """
<header class="index-head">
  <h1>%s</h1>
  %s
</header>
<div class="q-page">%s</div>
""" % (title, self.private_actions(body), body)
        groups, cur = [], None
        for qid in sorted(self.questions, key=lambda q: (self.questions[q]["group"], q)):
            q = self.questions[qid]
            if q["group"] != cur or not groups:
                cur = q["group"]
                groups.append([cur, []])
            touched = ", ".join(md.inline("[[%s]]" % i, ctx) for i in sorted(refs.get(qid, [])))
            groups[-1][1].append('<li id="%s"><span class="q-id">%s</span><span class="q-title">%s</span>%s</li>' % (
                qid.lower(), qid, esc(q["title"]), ('<span class="q-refs">In %s</span>' % touched) if touched else ""))
        body = "".join('<section class="group">%s<ol class="questions">%s</ol></section>' % (
            ("<h2>%s</h2>" % esc(p)) if p else "", "".join(items)) for p, items in groups)
        if not groups:
            body = '<p class="note">No open questions yet.</p>'
        return """
<header class="index-head">
  <h1>Open questions</h1>
  <p class="lead">%s</p>
  <p class="note">This page shows each question's title only. Write %s to give the page its full text.</p>
</header>
%s
""" % (esc(S.portal["questions_lead"]), esc(S.paths["questions_page"]), body)

    # ---------------------------------------------------------------- glossary and visuals

    def glossary_page(self):
        S, ctx = self.S, self.ctx()

        def sentences(items):
            return " ".join(md.inline(glossary.link_ids(x, S), ctx) for x in items)

        def private_part(items):
            if not items or self.share:
                return ""
            return md.private_details("<p>%s</p>" % sentences(items), S.private_label)

        out, jump = [], []
        for sec in self.glossary:
            sid = "gl-" + re.sub(r"[^a-z0-9]+", "-", sec["title"].lower()).strip("-")
            jump.append('<li><a href="#%s">%s</a> <span class="count">%d</span></li>' % (sid, esc(sec["title"]), len(sec["rows"])))
            rows = []
            for r in sec["rows"]:
                homes = [h for h in r["homes"] if h in self.topics]
                home = ('<p class="gl-home">Explained in %s</p>' % ", ".join(md.inline("[[%s]]" % h, ctx) for h in homes)) if homes else ""
                avoid = ('<p class="gl-avoid"><span class="gl-label">Instead of</span> %s</p>' % md.inline(r["avoid"], ctx)) if r["avoid"] else ""
                # The filter matches public words only: the term, its public meaning and the avoided words.
                find = plain(" ".join([md.inline(r["use"], ctx), sentences(r["public"]), md.inline(r["avoid"], ctx), home])).lower()
                rows.append('<div class="gl-row" id="%s" data-gl-text="%s"><dt>%s</dt><dd><p>%s</p>%s%s%s</dd></div>' % (
                    r["anchor"], attr(find), md.inline(r["use"], ctx), sentences(r["public"]), private_part(r["private"]), home, avoid))
            notes = "".join('<div class="gl-note"><p>%s</p>%s</div>' % (sentences(x["public"]), private_part(x["private"]))
                            for x in sec["notes"])
            out.append('<section class="gl-sec" id="%s" data-gl-sec><h2>%s</h2><dl class="gl-list">%s</dl>%s</section>'
                       % (sid, esc(sec["title"]), "".join(rows), notes))
        body = "".join(out) or '<p class="note">The glossary is empty.</p>'
        actions = self.private_actions(body)
        return """
<header class="index-head">
  <h1>Glossary</h1>
  <p class="lead">Look up any term the guide uses. Each concept has one word across every topic, and a row links to the topic that explains it in full.</p>
  %(actions)s
</header>
<nav class="gl-jump" aria-label="Glossary sections"><ol>%(jump)s</ol></nav>
<div class="gl-find" data-gl-find hidden>
  <label for="gl-q">Find a term. It also finds the words listed under “Instead of”.</label>
  <input id="gl-q" type="search" autocomplete="off" data-gl-input>
  <p class="gl-status" data-gl-status aria-live="polite"></p>
</div>
%(body)s
""" % {"actions": actions, "jump": "".join(jump), "body": body}

    def visual_order(self):
        order = {tid: i for i, tid in enumerate(self.map["order"])}
        tiers = {t: i for i, t in enumerate(self.S.tier_ids)}

        def key(v):
            is_intro = v["owner"] in tiers
            return (tiers.get(v["tier"], 99), 0 if is_intro else 1, order.get(v["owner"], 999), v["owner"] or "", v["n"])
        return sorted(self.visuals, key=key)

    def visuals_page(self):
        S, ctx = self.S, self.ctx()
        vis = self.visual_order()
        by_tier = {t: [v for v in vis if v["tier"] == t] for t in S.tier_ids}

        def source(v):
            if v["owner"] in S.tier_ids:
                return '<a href="%s">%s</a>, the tier\'s map' % (v["page"], esc(S.tier_label(v["owner"])))
            return md.inline("[[%s]]" % v["owner"], ctx)

        def where(v):
            if not v["where_title"]:
                return ""
            target = v["where_anchor"] if v["private"] else v["anchor"]
            chip = self.rank_chip(v["where_rank"]) if v["where_rank"] else ""
            return ' · <a href="%s#%s">%s</a> %s' % (v["page"], target, md.inline(v["where_title"], ctx), chip)

        out, contents = [], []
        for tier in S.tier_ids:
            items = by_tier[tier]
            if not items:
                continue
            entries, toc = [], []
            for v in items:
                vid = "%s-visual-%d" % ((v["owner"] or tier).lower(), v["n"])
                title = md.inline(v["title"], ctx)
                label = "%s · Visual %d" % (v["owner"] if v["owner"] not in S.tier_ids else S.tier_label(tier), v["n"])
                toc.append('<li><a href="#%s"><span class="vx-id">%s</span><span class="vx-t">%s</span></a>%s</li>'
                           % (vid, esc(label), title, '<span class="private-inline">Private</span>' if v["private"] else ""))
                src = '<p class="vx-src">In %s%s</p>' % (source(v), where(v))
                if v["private"]:
                    # By its title only, as the closed block on the topic page shows it.
                    lab = ' <span class="private-label">%s</span>' % esc(v["private_label"]) if v["private_label"] else ""
                    entries.append('<article class="vx vx-private" id="%s"><div class="private private-stub"><p class="private-stub-head">'
                                   '<span class="private-mark">Private</span>%s</p><p class="private-visual"><span class="visual-n">%s</span> %s</p>'
                                   '<p class="private-stub-note">It sits in a private block. Open it in its topic.</p></div>%s</article>'
                                   % (vid, lab, esc(label), title, src))
                    continue
                credit = '<p class="visual-credit">%s</p>' % md.inline(v["credit"], ctx) if v["credit"] else ""
                entries.append('<article class="vx" id="%s"><figure class="visual"><figcaption class="visual-title"><span class="visual-n">%s</span> %s</figcaption>'
                               '%s<div class="visual-frame">%s</div><div class="visual-caption">%s%s</div>'
                               '<div class="vx-job"><p class="vx-label">Why this visual is here</p><p>%s</p></div></figure></article>'
                               % (vid, esc(label), title, src, v["svg"], md.render(v["caption"], ctx), credit, md.inline(v["job"], ctx)))
            contents.append('<li><p class="vx-tier">%s</p><ol>%s</ol></li>' % (esc(S.tier_label(tier)), "".join(toc)))
            out.append('<section class="group vx-group" id="visuals-%s"><h2>%s</h2>%s</section>' % (tier, esc(S.tier_label(tier)), "".join(entries)))
        n_topics = len({v["owner"] for v in vis if v["owner"] not in S.tier_ids})
        n_maps = len({v["owner"] for v in vis if v["owner"] in S.tier_ids})
        if not vis:
            out.append('<p class="note">No topic has a visual yet.</p>')
        return """
<header class="index-head">
  <h1>Visuals</h1>
  <p class="lead">Find any visual in the guide again. Each one shows what it's for and links to the section that uses it.</p>
  <p class="note">%(n)d visual%(s)s from %(t)d topic%(ts)s%(maps)s. A visual from a private block shows its title only, as it does on its closed block.</p>
</header>
<nav class="vx-contents" aria-label="All visuals"><ol>%(contents)s</ol></nav>
%(out)s
""" % {"n": len(vis), "s": "" if len(vis) == 1 else "s", "t": n_topics, "ts": "" if n_topics == 1 else "s",
       "contents": "".join(contents), "out": "".join(out),
       "maps": (" and %d tier map%s" % (n_maps, "" if n_maps == 1 else "s")) if n_maps else ""}

    # ---------------------------------------------------------------- search

    def public_inline(self, text, ctx):
        return "" if self.S.has_private_tag(text) else plain(md.inline(text, ctx))

    def index_blocks(self, blocks, ctx):
        """The public text of a list of blocks. Of a private block, only its label and the
        titles of its visuals, which the format makes public."""
        out = []
        for b in blocks:
            if b["type"] == "markdown" and not self.S.has_private_tag(b["text"]):
                out.append(plain(md.render(b["text"], ctx)))
            elif b["type"] == "private":
                out += [b.get("label", "")] + [self.public_inline(x["title"], ctx) for x in b["blocks"] if x["type"] == "visual"]
            elif b["type"] == "visual":
                out.append(self.public_inline(b["title"], ctx))
                if not self.S.has_private_tag(b["caption"]):
                    out.append(plain(md.render(b["caption"], ctx)))
        return " ".join(x if x[-1:] in ".?!:" else x + "." for x in out if x)

    def search_entries(self, t):
        """[topic id, anchor, title, rank, text] for each part and section of a written topic.
        Run it after the topic is rendered, which settles the section anchors."""
        S, ctx, p, rows = self.S, self.ctx(), t["parsed"], []

        def add(anchor, title, rank, text):
            if text.strip():
                rows.append([t["id"], anchor, title, rank or "", text.strip()])

        add("why", S.parts["why"], "", self.index_blocks(p["why"], ctx))
        add("short", S.parts["short"], "", " ".join(self.public_inline(x, ctx) for x in p["short"]))
        for sec in p["sections"]:
            add(sec.get("html_anchor", sec["anchor"]), self.public_inline(sec["title"], ctx), sec["rank"], self.index_blocks(sec["blocks"], ctx))
        if S.has_case:
            add("case", S.case["part"], "", " ".join(self.index_blocks(b["blocks"], ctx) for b in p["case"].values()))
        for pos in p["positions"]:
            add("positions", self.public_inline(pos["position"], ctx), "", " ".join(self.index_blocks(v, ctx) for v in pos["fields"].values()))
        for m in p["materials"]:
            f = m["fields"]
            add("materials", self.public_inline(m["title"], ctx), m["rank"],
                " ".join(self.public_inline(f.get(k, ""), ctx) for k in ("by", "type", "part", "what you get")))
        add("check", S.parts["check"], "", " ".join(self.public_inline(x, ctx) for x in p["check"]))
        return rows

    def question_search_entries(self):
        """[key, anchor, title, rank, text] for each question and each headed part of the
        open-questions page. Like a topic, it gives search its public text only."""
        qp = self.page_files.get("questions")
        if not qp:
            return []
        ctx, rows, seen = self.ctx(), [], set()
        for c in qp["chunks"]:
            text = self.index_blocks(c["blocks"], ctx)
            if c["qid"] and c["qid"] not in seen:
                seen.add(c["qid"])
                anchor, title = c["qid"].lower(), ("%s %s" % (c["qid"], c["title"])).strip()
            elif c["heading"]:
                anchor, title = pages.heading_anchor(c["heading"], "q-"), self.public_inline(c["heading"], ctx)
            else:
                anchor, title = "", "Open questions"
            if text.strip():
                rows.append([QUESTIONS_KEY, anchor, title, "", text.strip()])
        return rows

    def write_search_index(self, out_dir, entries):
        """The index ships as a script, because a page opened from disk can't fetch a file.
        Each page in it is [title, href, rank, written, is a topic]."""
        topics = {}
        for tid in self.map["order"] + sorted(k for k in self.topics if k not in self.map["topics"]):
            t = self.topics[tid]
            topics[tid] = [t["title"], t["href"], t["rank"] or "", 1 if t["written"] else 0, 1]
        if any(e[0] == QUESTIONS_KEY for e in entries):
            topics[QUESTIONS_KEY] = ["Open questions", "questions.html", "", 1, 0]
        payload = json.dumps({"topics": topics, "entries": entries}, ensure_ascii=False, separators=(",", ":"))
        payload = payload.replace("</", "<\\/")
        (out_dir / "assets" / "search-index.js").write_text(
            "/* Generated by engine/build.py. The search index: public text only. */\n"
            "window.GUIDE_SEARCH = %s;\n" % payload, encoding="utf-8")

    def search_page(self):
        real = list(self.real_topics().values())
        written = len([t for t in real if t["written"]])
        has_q = bool(self.page_files.get("questions"))
        return """
<header class="index-head">
  <h1>Search</h1>
  <p class="lead">Find words across the written topics%s. Search runs in this page, from the files on disk.</p>
</header>
<form class="search-form" action="search.html" method="get" role="search" data-search-form>
  <label for="search-q">Words to find. Put a phrase in quotes.</label>
  <input id="search-q" type="search" name="q" autocomplete="off" data-search-input>
</form>
<p class="search-status" data-search-status aria-live="polite"></p>
<div class="search-results" data-search-results></div>
<p class="note search-scope">Search covers %s. It leaves out what private blocks hold, and finds only their labels and the titles of the visuals inside them.</p>
<noscript><p class="note">Search needs JavaScript, and this browser has it turned off.</p></noscript>
<script src="assets/search-index.js"></script>
""" % (" and the open questions" if has_q else "",
       ("the text of the %d written topics, the titles of all %d, and the open questions" if has_q
        else "the text of the %d written topics and the titles of all %d") % (written, len(real)))

    # ---------------------------------------------------------------- notes

    def notes_page(self):
        """The shell of the notes page. assets/notes.js fills it from this browser's storage."""
        filters = "".join(
            '<button type="button" class="filter" data-notes-filter="%s" aria-pressed="false">%s <span class="ann-count" data-count></span></button>'
            % (key, label) for key, label in [("all", "All"), ("bookmark", "Bookmarks"), ("note", "Notes"),
                                              ("todo", "To-dos"), ("done", "Done")])
        return """
<header class="index-head">
  <h1>My notes</h1>
  <p class="lead">Everything you saved while reading: bookmarks, notes and to-dos, by page. To save a sentence, select it. To save a section, use the + beside its heading.</p>
</header>
<p class="note" data-notes-noscript>This page needs its script, and the script didn't run.</p>
<div class="notes-app" data-notes-app hidden>
  <div class="notes-store">
    <p class="notes-state" data-notes-state></p>
    <p class="notes-tools"><button type="button" data-notes-export>Download a copy</button>
    <label class="notes-import">Load a copy <input type="file" accept="application/json,.json" data-notes-import></label></p>
  </div>
  <form class="notes-add" data-notes-add>
    <label class="vh" for="notes-new">New to-do</label>
    <input id="notes-new" type="text" placeholder="Add a to-do" autocomplete="off">
    <button type="submit">Add</button>
  </form>
  <div class="filters" role="group" aria-label="Show">%s</div>
  <div class="notes-list" data-notes-list></div>
</div>
""" % filters

    # ---------------------------------------------------------------- writing the site

    def build(self, out_dir):
        S = self.S
        out_dir = Path(out_dir)
        marker = out_dir / ".built-by-engine"
        if out_dir.exists() and any(out_dir.iterdir()) and not marker.exists():
            raise SystemExit("%s holds files the build didn't write. Choose an empty folder, or delete it first." % out_dir)
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True)
        marker.write_text("Generated by engine/build.py. Don't edit; rebuild.\n", encoding="utf-8")
        assets = out_dir / "assets"
        assets.mkdir()
        tokens = (ASSETS / "tokens.css").read_text(encoding="utf-8")
        tokens = re.sub(r"--hue:\s*[0-9.]+;", "--hue: %s;" % S.portal["accent_hue"], tokens, count=1)
        (assets / "tokens.css").write_text(tokens, encoding="utf-8")
        for name in ("visuals.css", "site.css", "site.js", "notes.js"):
            shutil.copy(ASSETS / name, assets / name)

        def write(name, text):
            (out_dir / name).write_text(text, encoding="utf-8")

        suffix = " · " + S.title
        write("index.html", self.page(S.title, self.home_page(), "home"))
        for t in S.tiers:
            write(t.id + ".html", self.page(t.name + suffix, self.tier_page(t.id), "tier", current_tier=t.id,
                                            body_attrs={"tier": t.id}))
        write("topics.html", self.page("All topics" + suffix, self.topics_page(), "topics"))
        write("materials.html", self.page("Materials" + suffix, self.materials_page(), "materials"))
        write("questions.html", self.page("Open questions" + suffix, self.questions_page(), "questions"))
        write("search.html", self.page("Search" + suffix, self.search_page(), "search"))
        write("notes.html", self.page("My notes" + suffix, self.notes_page(), "notes"))
        entries = []
        for tid, t in self.topics.items():
            attrs = {"id": tid, "tier": t["tier"], "rank": t["rank"], "status": "written" if t["written"] else "planned",
                     "minutes": t["minutes"]}
            rail = self.rail_for(t["tier"], tid) if t["tier"] in self.groups else ""
            title = "%s %s%s" % (tid, t["title"], suffix)
            if t["written"]:
                try:
                    body, toc = TopicRenderer(self, t).render()
                    entries += self.search_entries(t)
                except Exception as exc:   # a half-written topic must not stop the build
                    self.problems.append("%s could not be rendered: %r" % (tid, exc))
                    body, toc = '<article class="topic"><div class="banner banner-error"><p>%s could not be rendered. See the build output.</p></div></article>' % tid, ""
                write(t["href"], self.page(title, body, "topic", current_tier=t["tier"], rail=rail, toc=toc, body_attrs=attrs))
            elif t["map"] is not None:
                write(t["href"], self.page(title, self.planned_page(t), "topic", current_tier=t["tier"], rail=rail, body_attrs=attrs))
        entries += self.question_search_entries()
        self.write_search_index(out_dir, entries)
        write("glossary.html", self.page("Glossary" + suffix, self.glossary_page(), "glossary"))
        write("visuals.html", self.page("Visuals" + suffix, self.visuals_page(), "visuals"))
        return self


def split_title(blocks):
    """When a page opens with its one '#' heading, that heading is the page title.
    Returns (title or "", the blocks without it)."""
    if not blocks or blocks[0]["type"] != "markdown":
        return "", blocks
    first = blocks[0]["text"].split("\n")
    m = re.match(r"^#\s+(.*)$", first[0])
    others = [b for b in blocks if b["type"] == "markdown" and re.search(r"^#\s", b["text"], re.M)]
    if not m or len(others) > 1 or len(re.findall(r"^#\s", blocks[0]["text"], re.M)) > 1:
        return "", blocks
    rest = "\n".join(first[1:]).strip("\n")
    head = [dict(blocks[0], text=rest)] if rest.strip() else []
    return m.group(1).strip(), head + blocks[1:]


def plain(fragment):
    """The visible text of rendered HTML, without provenance tags or URLs."""
    fragment = re.sub(r'<(a|span) class="tag\b[^"]*"[^>]*>[^<]*</\1>', "", fragment)
    fragment = re.sub(r"</?(?:p|li|ul|ol|h\d|div|blockquote|table|thead|tbody|tr|td|th|pre|figure|section|br)\b[^>]*>", " ", fragment)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    text = re.sub(r"https?://\S+", " ", html.unescape(fragment))
    text = re.sub(r"\s+", " ", text)
    return re.sub(r" ([,.;:!?)])", r"\1", text).strip()


# ---------------------------------------------------------------- topic pages

class TopicRenderer:
    def __init__(self, site, topic):
        self.site = site
        self.S = site.S
        self.t = topic
        self.p = topic["parsed"]
        self.ctx = site.ctx()
        self.visual_n = 0
        self.where = None          # (anchor, title, rank) of the part or section being rendered
        self.private_labels = []   # labels of the private blocks around the current block
        self.levels = None         # heading levels by '#' count, for a page without parts

    def blocks(self, blocks, anchor_prefix=""):
        out = []
        for b in blocks:
            if b["type"] == "markdown":
                out.append(md.render(b["text"], self.ctx, heading_level=4, anchor_prefix=anchor_prefix, levels=self.levels))
            elif b["type"] == "private" and self.site.share:
                out.append(self.omitted(b))
            elif b["type"] == "private":
                first = self.visual_n + 1
                self.ctx.private_depth += 1
                self.private_labels.append(b.get("label", ""))
                inner = self.blocks(b["blocks"], anchor_prefix)
                self.private_labels.pop()
                self.ctx.private_depth -= 1
                vis = [x for x in b["blocks"] if x["type"] == "visual"]
                titles = [(first + k, md.inline(x["title"], self.ctx)) for k, x in enumerate(vis)]
                out.append(md.private_details(inner, b.get("label", ""), titles))
            elif b["type"] == "visual":
                out.append(self.visual(b))
        return "\n".join(out)

    def omitted(self, b):
        """A private block, left out of a shared copy. Its visuals keep their numbers and their
        place in the visual index, by title only, as a closed block shows them."""
        titles = []
        self.private_labels.append(b.get("label", ""))
        for x in b["blocks"]:
            if x["type"] == "visual":
                self.visual_n += 1
                titles.append((self.visual_n, md.inline(x["title"], self.ctx)))
                if not self.t.get("no_index"):
                    self.record_visual(x, self.visual_n, "visual-%d" % self.visual_n, "")
        self.private_labels.pop()
        inner = "\n".join(block_text(x) for x in b["blocks"])
        return md.omitted_block(b.get("label", ""), titles, md.question_ids(inner, self.S))

    def visual(self, v):
        self.visual_n += 1
        n = self.visual_n
        path = self.p["folder"] / v["file"]
        try:
            svg = path.read_text(encoding="utf-8")
        except OSError:
            svg = '<p class="visual-missing">The file %s is missing.</p>' % esc(v["file"])
        svg = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", svg).strip()
        svg = re.sub(r"<svg\b", '<svg role="img" aria-label="%s" class="visual-svg"' % attr(v["alt"]), svg, count=1)
        svg = re.sub(r'(<svg\b[^>]*?)\s(?:width|height)="[^"]*"', r"\1", svg)
        svg = re.sub(r'(<svg\b[^>]*?)\s(?:width|height)="[^"]*"', r"\1", svg)
        credit = '<p class="visual-credit">%s</p>' % md.inline(v["credit"], self.ctx) if v.get("credit") else ""
        anchor = "visual-%d" % n
        if not self.t.get("no_index"):
            self.record_visual(v, n, anchor, svg)
        return ('<figure class="visual" id="%s"><figcaption class="visual-title"><span class="visual-n">Visual %d</span> %s</figcaption>'
                '<div class="visual-frame">%s</div><div class="visual-caption">%s%s</div>'
                '<details class="visual-job"><summary>Why this visual is here</summary><p>%s</p></details></figure>') % (
            anchor, n, md.inline(v["title"], self.ctx), svg,
            md.render(v["caption"], self.ctx), credit, md.inline(v["job"], self.ctx))

    def record_visual(self, v, n, anchor, svg):
        """Keep what the visual index needs. It reads the visuals as they render,
        so nobody keeps a list by hand."""
        t = self.t
        where = self.where or ("", "", None)
        self.site.visuals.append({
            "owner": t.get("id") or t.get("intro_tier"), "tier": t.get("tier") or t.get("intro_tier"),
            "page": t.get("href") or "%s.html" % t.get("intro_tier"), "n": n, "anchor": anchor,
            "where_anchor": where[0], "where_title": where[1], "where_rank": where[2],
            "private": bool(self.private_labels), "private_label": next((x for x in reversed(self.private_labels) if x), ""),
            "title": v["title"], "job": v["job"], "caption": v["caption"], "credit": v.get("credit", ""), "svg": svg})

    def section(self, s, used):
        anchor = s["anchor"]
        k = 2
        while anchor in used:
            anchor = "%s-%d" % (s["anchor"], k)
            k += 1
        used.add(anchor)
        s["html_anchor"] = anchor
        rank = s["rank"] or "unknown"
        self.where = (anchor, s["title"], s["rank"])
        return ('<section class="sec rank-%s" id="%s"><p class="sec-meta">%s<span class="sec-time">%s</span>%s</p>'
                '<h3><a class="sec-anchor" href="#%s">%s</a></h3>%s</section>') % (
            rank, anchor, self.site.rank_chip(rank), fmt_min(max(1, s.get("minutes", 0))),
            '<span class="sec-skip">You can skip it</span>' if rank == "context" else "",
            anchor, md.inline(s["title"], self.ctx), self.blocks(s["blocks"], anchor + "-"))

    def material(self, m):
        f = m["fields"]
        rank = m["rank"] or "unknown"
        title = md.inline(m["title"], self.ctx)
        if f.get("link"):
            title = '<a class="mat-title" href="%s" target="_blank" rel="noopener">%s</a>' % (attr(f["link"]), title)
        else:
            title = '<span class="mat-title">%s</span>' % title
        meta = [esc(f.get("type", "").capitalize()), md.inline(f.get("by", ""), self.ctx), esc(f.get("date", "")),
                esc(f.get("time", "")), esc((f.get("access") or "").capitalize())]
        if f.get("vendor") == "yes":
            meta.append('<span class="mat-vendor">Vendor content</span>')
        rows = ['<p class="mat-get">%s</p>' % md.inline(f.get("what you get", ""), self.ctx)]
        if f.get("part"):
            rows.append('<p class="mat-field"><span class="mat-label">Part</span> %s</p>' % md.inline(f["part"], self.ctx))
        if f.get("passed over"):
            rows.append('<p class="mat-field"><span class="mat-label">Passed over</span> %s</p>' % md.inline(f["passed over"], self.ctx))
        if f.get("steps"):
            rows.append('<div class="mat-field mat-steps"><span class="mat-label">Steps</span>%s</div>' % md.render(f["steps"], self.ctx))
        rows.append('<p class="mat-checked">Checked %s</p>' % esc(f.get("checked", "")))
        return ('<li class="material rank-%s" data-rank="%s"><p class="mat-rank">%s<span class="mat-action">%s</span></p>'
                '%s<p class="mat-meta">%s</p>%s</li>') % (
            rank, rank, self.site.rank_chip(rank), esc(self.site.action(rank)), title,
            " · ".join(x for x in meta if x), "".join(rows))

    def position(self, pos):
        out = ['<div class="position"><h3>%s</h3>' % md.inline(pos["position"], self.ctx)]
        for label in self.S.position_fields:
            key = label.lower()
            if key in pos["fields"]:
                out.append('<div class="pos-field"><p class="pos-label">%s</p>%s</div>' % (esc(label), self.blocks(pos["fields"][key])))
        out.append("</div>")
        return "".join(out)

    def header(self, status_html):
        t, h, S = self.t, self.p["header"], self.S
        facts = []
        deps = h.get("read first") or []
        facts.append(("Read first", ", ".join(md.inline("[[%s]]" % d, self.ctx) for d in deps) if deps else "Nothing. It stands alone."))
        if h.get("updates"):
            facts.append(("Updates", ", ".join(md.inline("[[%s]]" % d, self.ctx) for d in h["updates"])))
        if h.get("covers"):
            facts.append(("What it covers", COVERS_LABEL.get(h["covers"], esc(h["covers"]))))
        if h.get("check again"):
            facts.append(("Check again", esc(h["check again"])))
        dl = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (k, v) for k, v in facts)
        meta = [self.site.rank_chip(t["rank"]), self.site.size_span(t["size"]),
                '<span>%s of reading</span>' % fmt_min(t["minutes"]),
                '<span>Depth %s</span>' % esc(h.get("depth", "?")),
                '<span>Facts checked %s</span>' % esc(h.get("checked", "?"))]
        return ('<header class="topic-head"><p class="crumbs"><a href="%s.html">%s</a><span>%s</span></p>'
                '<h1><span class="topic-id">%s</span> %s</h1><p class="topic-meta">%s</p><dl class="topic-facts">%s</dl>'
                '<p class="topic-actions"><button type="button" class="read-toggle" data-read-toggle data-id="%s" aria-pressed="false">Mark as read</button>%s</p></header>') % (
            t["tier"], esc(S.tier_label(t["tier"])), esc(t["group"]), t["id"], esc(t["title"]),
            "".join(meta), dl, t["id"], status_html)

    def render(self):
        S, p = self.S, self.p
        parts, toc = [], []
        used = set()
        if p.get("errors"):
            items = "".join("<li>Line %s: %s</li>" % (e["line"], esc(e["message"])) for e in p["errors"])
            parts.append('<div class="banner banner-error"><details><summary><strong>%d format errors.</strong> The page shows what the build could read.</summary><ul>%s</ul></details></div>'
                         % (len(p["errors"]), items))
        part_keys = [x["key"] for x in p["parts"]]

        def part(pid, title, inner, extra_cls=""):
            toc.append('<li class="toc-part"><a href="#%s">%s</a></li>' % (pid, esc(title)))
            return '<section class="part %s" id="%s"><h2 class="part-title">%s</h2>%s</section>' % (extra_cls, pid, esc(title), inner)

        if "why" in part_keys:
            self.where = ("why", S.parts["why"], None)
            parts.append(part("why", S.parts["why"], self.blocks(p["why"])))
        if "short" in part_keys:
            items = "".join("<li>%s</li>" % md.inline(x, self.ctx) for x in p["short"])
            parts.append(part("short", S.parts["short"], "<ul>%s</ul>" % items, "part-short"))
        for hx in [x for x in p["parts"] if x["key"] == "explanation"]:
            pid = "explanation" if not hx["half"] else "explanation-" + hx["half"]
            secs = [s for s in p["sections"] if s["half"] == hx["half"]]
            inner = "".join(self.section(s, used) for s in secs)
            toc.append('<li class="toc-part"><a href="#%s">%s</a><ul>%s</ul></li>' % (
                pid, esc(hx["title"]), "".join(
                    '<li class="toc-sec rank-%s"><a href="#%s">%s<span class="toc-title">%s</span><span class="toc-time">%s</span></a></li>'
                    % (s["rank"], s["html_anchor"], self.site.rank_glyph(s["rank"]),
                       esc(re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), s["title"])),
                       fmt_min(max(1, s.get("minutes", 0)))) for s in secs)))
            parts.append('<section class="part part-explanation" id="%s"><h2 class="part-title">%s</h2>%s</section>' % (pid, esc(hx["title"]), inner))
        if "case" in part_keys:
            self.where = ("case", S.case["part"], None)
            inner = []
            for label in S.case_blocks:
                key = label.lower()
                if key in p["case"]:
                    slug = re.sub(r"[^a-z0-9]+", "-", key).strip("-")
                    inner.append('<div class="case-block case-%s"><h3>%s</h3>%s</div>' % (
                        slug, esc(label), self.blocks(p["case"][key]["blocks"], "case-" + slug + "-")))
            parts.append(part("case", S.case["part"], "".join(inner), "part-case"))
        if p["positions"]:
            self.where = ("positions", S.parts["positions"], None)
            parts.append(part("positions", S.parts["positions"], "".join(self.position(x) for x in p["positions"]), "part-positions"))
        if p["materials"]:
            crit = [m for m in p["materials"] if m["rank"] == "critical"]
            summary = "%d material%s." % (len(p["materials"]), "" if len(p["materials"]) == 1 else "s")
            if crit:
                summary += " Read the critical one%s in full: %s." % ("" if len(crit) == 1 else "s", fmt_min(sum(m["minutes"] or 0 for m in crit)))
            inner = '<p class="part-sum">%s</p><ol class="materials">%s</ol>' % (summary, "".join(self.material(m) for m in p["materials"]))
            parts.append(part("materials", S.parts["materials"], inner, "part-materials"))
        if "unverified" in part_keys:
            items = p["unverified"]
            if len(items) == 1 and items[0].strip().rstrip(".").lower() == "none":
                inner = "<p>Nothing. Every claim in this topic was confirmed.</p>"
            else:
                inner = "<ul>%s</ul>" % "".join("<li>%s</li>" % md.inline(x, self.ctx) for x in items)
            parts.append(part("not-verified", S.parts["unverified"], inner, "part-unverified"))
        if p["check"]:
            inner = "<ol>%s</ol>" % "".join("<li>%s</li>" % md.inline(x, self.ctx) for x in p["check"])
            parts.append(part("check", S.parts["check"], inner, "part-check"))
        parts.append(self.site.pager(self.t))
        has_ctx = any(s["rank"] == "context" for s in p["sections"])
        toc_html = toc_block(toc, has_ctx)
        inline_toc = toc_block(toc, has_ctx, inline=True)
        body = "".join(parts)
        has_private = '<details class="private"' in body
        status = PRIVATE_TOGGLE if has_private else ""
        return '<article class="topic">%s%s%s%s</article>' % (
            self.header(status), PRINT_NOTE if has_private else "", inline_toc, body), toc_html


def toc_block(items, has_context, inline=False):
    toggle = ('<button type="button" class="context-toggle" data-context-toggle aria-pressed="false">Hide context sections</button>'
              if has_context else "")
    if inline:
        return ('<details class="toc toc-inline" data-toc-inline><summary>On this page</summary>'
                '<ol>%s</ol>%s</details>' % ("".join(items), toggle))
    return ('<aside class="toc-wrap"><nav class="toc" aria-label="On this page"><p class="toc-head">On this page</p>'
            '<ol>%s</ol>%s</nav></aside>' % ("".join(items), toggle))
