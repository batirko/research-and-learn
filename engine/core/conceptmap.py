"""The concept map: concepts.html, and the section that ends every topic page.

Reads the concept file (paths.concepts, content/concepts.json by default) and draws the map
as a static SVG at build time. The geometry is a circle and a few Bézier curves, so the page
needs no library and nothing from the network. assets/conceptmap.js adds the interactions on
top of the same markup. The page works without it: the map keeps its links, and the text
index under the map lists every concept.

A concept is explained in its home topic and used in other topics. The map draws it once,
as a leaf under its home topic. Each use is a curve from that leaf to the using topic's
node, bundled toward the centre. Bundling follows the guide's own tree: a curve between
topics in one group stays inside the group, a curve between groups of one tier goes through
the tier, and a curve between tiers goes through the centre.

engine/format.md, "The concept file", describes the file. Without it, the build skips the
page, its link and the topic sections.
"""

import hashlib
import json
import math
import re
from html import unescape as html_unescape

from . import render as md
from .settings import RANKS

esc = md.esc
attr = md.attr

SECTION_ID = "concepts-on-this-page"

# ---- geometry, in SVG units. The map is drawn around (0, 0).
PITCH = 15          # distance between two leaves along the outer ring
TOPIC_GAP = 10      # extra space after each topic's leaves
TIER_GAP = 46       # extra space between tiers
MIN_SLOTS = 3       # a topic with fewer leaves still gets room for its node
R_TIER = 118
R_GROUP = 275       # an invisible waypoint for bundling
R_TOPIC = 425
NODE_R = 13
LEAF_SIZE = 9
LABEL_FONT = 12
LABEL_GAP = 11
BETA = 0.86         # how tightly curves bundle: 0 is a straight line, 1 follows the tree
CHAR_W = 0.56       # average glyph width as a share of the font size, for the extent only


def num(v):
    s = ("%.1f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pt(r, theta):
    return (r * math.cos(theta), r * math.sin(theta))


# ---------------------------------------------------------------- loading

def fingerprint(text):
    """A short hash of a topic's text, blind to changes in white space only. The concept file
    keeps one per topic, from the pass that read it, so the build can say which topics have
    changed since."""
    norm = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def topic_fingerprint(t):
    folder = (t.get("parsed") or {}).get("folder")
    if not folder or not (folder / "topic.md").exists():
        return None
    return fingerprint((folder / "topic.md").read_text(encoding="utf-8"))


def load(S):
    """Read the concept file. Returns {"concepts": [...], "read": {topic ID: fingerprint},
    "path": Path, "problems": [...]}, or None when the file doesn't exist."""
    path = S.file("concepts")
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return {"concepts": [], "read": {}, "path": path, "problems": ["%s is not valid JSON: %s" % (path.name, exc)]}
    concepts = []
    for c in raw.get("concepts", []):
        concepts.append({
            "id": str(c.get("id", "")), "name": c.get("name", ""), "home": c.get("home", ""),
            "anchor": c.get("anchor", ""), "rank": c.get("rank", ""),
            "definition": c.get("definition", ""), "aliases": list(c.get("aliases", [])),
            "refs": [{"topic": r.get("topic", ""), "anchor": r.get("anchor", ""), "how": r.get("how", "")}
                     for r in c.get("refs", [])]})
    read = {str(k): str(v) for k, v in (raw.get("read") or {}).items()}
    return {"concepts": concepts, "read": read, "path": path, "problems": []}


def stale(site):
    """Notes for the build's output: written topics whose text changed since their concept
    pass, and written topics no pass has read yet. Neither fails the build."""
    cm = site.concepts
    if not cm:
        return []
    out, unread = [], []
    for tid in site.map["order"]:
        t = site.topics.get(tid)
        if not t or not t["written"]:
            continue
        if tid not in cm["read"]:
            unread.append(tid)
        elif topic_fingerprint(t) != cm["read"][tid]:
            out.append("%s changed since its concept pass. Check its concepts and uses, then run "
                       "python3 engine/concepts.py --stamp %s" % (tid, tid))
    if unread:
        out.append("No concept pass has read %s yet." % ", ".join(unread))
    return out


def tier_name(S, tier):
    return S.tier_label(tier)


def mapped_topics(site):
    """The written topics of the topic map, in tier and topic-map order, with their group."""
    out = []
    for tier in site.S.tier_ids:
        for g in site.groups.get(tier, []):
            for tid in g["ids"]:
                t = site.topics.get(tid)
                if t and t["written"] and t["map"] is not None:
                    out.append({"id": tid, "tier": tier, "group": g["name"], "topic": t})
    return out


def short_title(title, limit=30):
    head = title.split(": ", 1)[0]
    if len(head) <= limit:
        return head
    cut = head[:limit].rsplit(" ", 1)[0]
    return cut + "…"


# ---------------------------------------------------------------- layout

def bspline_path(points):
    """A clamped uniform cubic B-spline through a control polygon, as an SVG path."""
    c = [points[0]] * 3 + points[1:-1] + [points[-1]] * 3
    segs = []
    for i in range(len(c) - 3):
        q1, q2, q3 = c[i + 1], c[i + 2], c[i + 3]
        b1 = ((2 * q1[0] + q2[0]) / 3, (2 * q1[1] + q2[1]) / 3)
        b2 = ((q1[0] + 2 * q2[0]) / 3, (q1[1] + 2 * q2[1]) / 3)
        b3 = ((q1[0] + 4 * q2[0] + q3[0]) / 6, (q1[1] + 4 * q2[1] + q3[1]) / 6)
        segs.append("C%s %s %s %s %s %s" % (num(b1[0]), num(b1[1]), num(b2[0]), num(b2[1]), num(b3[0]), num(b3[1])))
    return "M%s %s" % (num(points[0][0]), num(points[0][1])) + "".join(segs)


def straighten(points, beta=BETA):
    n = len(points) - 1
    if n < 1:
        return points
    (x0, y0), (xn, yn) = points[0], points[-1]
    out = []
    for i, (x, y) in enumerate(points):
        t = i / n
        out.append((beta * x + (1 - beta) * (x0 + t * (xn - x0)), beta * y + (1 - beta) * (y0 + t * (yn - y0))))
    return out


def build_layout(site, concepts):
    topics = mapped_topics(site)
    by_home = {}
    for c in concepts:
        by_home.setdefault(c["home"], []).append(c)

    spans = {}
    cursor = 0.0
    last_tier = None
    for t in topics:
        if t["tier"] != last_tier:
            cursor += TIER_GAP if last_tier is not None else 0
            last_tier = t["tier"]
        n = len(by_home.get(t["id"], []))
        length = max(n, MIN_SLOTS) * PITCH + TOPIC_GAP
        spans[t["id"]] = (cursor, cursor + length)
        cursor += length
    total = max(cursor + TIER_GAP, 1.0)
    r_leaf = max(total / (2 * math.pi), R_TOPIC + 190)
    # If the ring is wider than the leaves need, spread the topics over the whole circle.
    stretch = (2 * math.pi * r_leaf) / total
    start = -math.pi / 2

    def theta(length):
        return start + (length * stretch) / r_leaf

    nodes = {}
    for t in topics:
        a, b = spans[t["id"]]
        mid = (a + b) / 2.0
        leaves = by_home.get(t["id"], [])
        n = len(leaves)
        leaf_pos = [(c, theta(mid + (i - (n - 1) / 2.0) * PITCH)) for i, c in enumerate(leaves)]
        nodes[t["id"]] = {"t": t, "theta": theta(mid), "span": (a, b), "leaves": leaf_pos}

    tiers, groups = {}, {}
    for tier in site.S.tier_ids:
        members = [t for t in topics if t["tier"] == tier]
        if not members:
            continue
        a = spans[members[0]["id"]][0]
        b = spans[members[-1]["id"]][1]
        tiers[tier] = {"theta": theta((a + b) / 2.0), "ids": [m["id"] for m in members]}
        names = []
        for m in members:
            if m["group"] not in names:
                names.append(m["group"])
        for name in names:
            ids = [m["id"] for m in members if m["group"] == name]
            groups[(tier, name)] = {"theta": theta((spans[ids[0]][0] + spans[ids[-1]][1]) / 2.0), "ids": ids}
    return {"nodes": nodes, "tiers": tiers, "groups": groups, "r_leaf": r_leaf, "topics": topics, "by_home": by_home}


# ---------------------------------------------------------------- the map

def label_side(theta):
    """Text on the right half reads outward as it is; on the left half it flips, so it stays upright."""
    right = math.cos(theta) >= -1e-9
    deg = math.degrees(theta)
    return right, (deg if right else deg + 180.0)


def draw_map(site, concepts, lay):
    S = site.S
    r_leaf = lay["r_leaf"]
    nodes, tiers, groups = lay["nodes"], lay["tiers"], lay["groups"]
    topic_of = {t["id"]: t for t in lay["topics"]}
    xs, ys = [-NODE_R, NODE_R], [-NODE_R, NODE_R]

    def grow(x, y, pad=0):
        xs.extend([x - pad, x + pad])
        ys.extend([y - pad, y + pad])

    # Incoming curves per topic, so their ends fan out along the node's inner edge.
    incoming = {}
    for c in concepts:
        for r in c["refs"]:
            if r["topic"] in nodes and c["home"] in nodes:
                incoming.setdefault(r["topic"], []).append(c)
    end_offset = {}
    for tid, cs in incoming.items():
        th = nodes[tid]["theta"]

        def side(c, th=th):
            d = nodes[c["home"]]["theta"] - th
            return math.atan2(math.sin(d), math.cos(d))
        cs_sorted = sorted(cs, key=lambda c: (side(c), c["id"]))
        k = len(cs_sorted)
        spread = min(NODE_R - 2.5, 0.9 * (k - 1) / 2.0)
        for i, c in enumerate(cs_sorted):
            end_offset[(c["id"], tid)] = 0.0 if k == 1 else -spread + 2 * spread * i / (k - 1)

    # Tree edges, one path per tier, and a fan from each topic to its leaves.
    edges, fans = [], []
    for tier in S.tier_ids:
        if tier not in tiers:
            continue
        tx, ty = pt(R_TIER, tiers[tier]["theta"])
        cx0, cy0 = pt(30, tiers[tier]["theta"])
        d = ["M%s %sL%s %s" % (num(cx0), num(cy0), num(tx), num(ty))]
        for tid in tiers[tier]["ids"]:
            nd = nodes[tid]
            nx, ny = pt(R_TOPIC, nd["theta"])
            d.append("M%s %sL%s %s" % (num(tx), num(ty), num(nx), num(ny)))
            sx, sy = pt(R_TOPIC + NODE_R, nd["theta"])
            for c, lth in nd["leaves"]:
                lx, ly = pt(r_leaf - LEAF_SIZE / 2 - 2, lth)
                fans.append('<path class="cx-fan" data-c="%s" d="M%s %sL%s %s"/>' % (
                    attr(c["id"]), num(sx), num(sy), num(lx), num(ly)))
        edges.append('<path class="cx-edge" data-tier="%s" d="%s"/>' % (attr(tier), "".join(d)))

    # The curves: one per use.
    curves = []
    for c in concepts:
        home = c["home"]
        if home not in nodes:
            continue
        hn = nodes[home]
        li = [lth for cc, lth in hn["leaves"] if cc["id"] == c["id"]]
        if not li:
            continue
        start_pt = pt(r_leaf - LEAF_SIZE / 2 - 3, li[0])
        h_tier = topic_of[home]["tier"]
        h_group = (h_tier, topic_of[home]["group"])
        for r in c["refs"]:
            tid = r["topic"]
            if tid not in nodes or tid == home:
                continue
            tth = nodes[tid]["theta"]
            t_tier = topic_of[tid]["tier"]
            t_group = (t_tier, topic_of[tid]["group"])
            off = end_offset.get((c["id"], tid), 0.0)
            ex, ey = pt(R_TOPIC - NODE_R - 1, tth)
            ex += -math.sin(tth) * off
            ey += math.cos(tth) * off
            path = [start_pt, pt(R_TOPIC, hn["theta"]), pt(R_GROUP, groups[h_group]["theta"])]
            if h_tier == t_tier:
                if h_group != t_group:
                    path += [pt(R_TIER, tiers[h_tier]["theta"]), pt(R_GROUP, groups[t_group]["theta"])]
            else:
                path += [pt(R_TIER, tiers[h_tier]["theta"]), (0.0, 0.0), pt(R_TIER, tiers[t_tier]["theta"]),
                         pt(R_GROUP, groups[t_group]["theta"])]
            path.append((ex, ey))
            curves.append('<path class="cx-ref" data-from="%s" data-to="%s" d="%s"/>' % (
                attr(c["id"]), tid, bspline_path(straighten(path))))

    # The tier nodes and the centre.
    tier_nodes = []
    for tier in S.tier_ids:
        if tier not in tiers:
            continue
        x, y = pt(R_TIER, tiers[tier]["theta"])
        label = tier_name(S, tier)
        w, h = max(78, int(len(label) * 12 * CHAR_W + 24)), 26
        tier_nodes.append(
            '<a class="cx-tier" href="%s.html" data-tier="%s"><title>%s</title>'
            '<rect x="%s" y="%s" width="%d" height="%d" rx="13"/><text x="%s" y="%s" text-anchor="middle" dy="0.35em">%s</text></a>'
            % (attr(tier), attr(tier), esc(label), num(x - w / 2), num(y - h / 2), w, h, num(x), num(y), esc(label)))
    centre = ('<g class="cx-centre"><circle r="34"/><text text-anchor="middle" y="-3">The</text>'
              '<text text-anchor="middle" y="11">guide</text></g>')

    # Topic nodes and leaves, in tree order, which is the keyboard order too.
    nodes_svg = []
    for tid in [t["id"] for t in lay["topics"]]:
        nd = nodes[tid]
        topic = nd["t"]["topic"]
        th = nd["theta"]
        x, y = pt(R_TOPIC, th)
        n_own = len(nd["leaves"])
        uses = len({c["id"] for c in incoming.get(tid, [])})
        right, deg = label_side(th)
        tx, ty = pt(R_TOPIC - NODE_R - 6, th)
        title_attrs = 'transform="translate(%s %s) rotate(%s)" text-anchor="%s"' % (
            num(tx), num(ty), num(deg), "end" if right else "start")
        nodes_svg.append(
            '<a class="cx-topic" href="%s" data-t="%s" data-tier="%s" data-x="%s" data-y="%s">'
            '<title>%s %s. Explains %d concept%s and uses %d from other topics.</title>'
            '<circle class="cx-node" cx="%s" cy="%s" r="%d"/>'
            '<text class="cx-id" x="%s" y="%s" text-anchor="middle" dy="0.35em">%s</text>'
            '<text class="cx-ttl" %s dy="0.35em">%s</text></a>' % (
                topic["href"], tid, attr(nd["t"]["tier"]), num(x), num(y), tid, esc(topic["title"]),
                n_own, "" if n_own == 1 else "s", uses, num(x), num(y), NODE_R, num(x), num(y), tid,
                title_attrs, esc(short_title(topic["title"]))))
        grow(x, y, NODE_R)
        for c, lth in nd["leaves"]:
            lx, ly = pt(r_leaf, lth)
            lright, ldeg = label_side(lth)
            half = LEAF_SIZE / 2.0
            nodes_svg.append(
                '<a class="cx-leaf" href="%s#%s" data-c="%s" data-rank="%s" data-home="%s" data-x="%s" data-y="%s">'
                '<title>%s. %s. Explained in %s.</title>'
                '<rect class="cx-glyph" x="%s" y="%s" width="%d" height="%d" rx="1"/>'
                '<text class="cx-lab" transform="translate(%s %s) rotate(%s)" x="%d" text-anchor="%s" dy="0.35em">%s</text></a>' % (
                    topic["href"], attr(c["anchor"]), attr(c["id"]), attr(c["rank"]), tid, num(lx), num(ly),
                    esc(c["name"]), esc(S.rank_label(c["rank"]) if c["rank"] in RANKS else "No rank"), tid,
                    num(lx - half), num(ly - half), LEAF_SIZE, LEAF_SIZE,
                    num(lx), num(ly), num(ldeg), LABEL_GAP if lright else -LABEL_GAP,
                    "start" if lright else "end", esc(c["name"])))
            width = len(c["name"]) * LABEL_FONT * CHAR_W + LABEL_GAP + 10
            ex, ey = pt(r_leaf + width, lth)
            grow(lx, ly, LABEL_FONT)
            grow(ex, ey, LABEL_FONT)

    min_x, max_x = min(xs) - 14, max(xs) + 14
    min_y, max_y = min(ys) - 14, max(ys) + 14
    w, h = max_x - min_x, max_y - min_y
    defs = ('<defs>'
            '<marker id="cx-dot" markerUnits="userSpaceOnUse" viewBox="-3 -3 6 6" markerWidth="6" markerHeight="6"><circle class="cx-m-dot" r="2"/></marker>'
            '<marker id="cx-ring" markerUnits="userSpaceOnUse" viewBox="-4 -4 8 8" markerWidth="8" markerHeight="8"><circle class="cx-m-ring" r="2.6"/></marker>'
            '<marker id="cx-dot-on" markerUnits="userSpaceOnUse" viewBox="-4 -4 8 8" markerWidth="8" markerHeight="8"><circle class="cx-m-dot-on" r="3"/></marker>'
            '<marker id="cx-ring-on" markerUnits="userSpaceOnUse" viewBox="-5 -5 10 10" markerWidth="10" markerHeight="10"><circle class="cx-m-ring-on" r="3.4"/></marker>'
            '</defs>')
    return ('<svg class="cx-svg" data-cx-svg viewBox="%s %s %s %s" style="aspect-ratio:%s / %s" role="group" '
            'aria-label="Concept map. Every topic with its concepts, and a curve from each concept to the topics that use it. The index below lists the same content as text.">'
            '%s<g class="cx-edges">%s</g><g class="cx-fans">%s</g><g class="cx-refs">%s</g>%s%s<g class="cx-nodes">%s</g></svg>') % (
        num(min_x), num(min_y), num(w), num(h), num(w), num(h), defs, "".join(edges), "".join(fans), "".join(curves),
        "".join(tier_nodes), centre, "".join(nodes_svg))


# ---------------------------------------------------------------- the text index

def topic_href(site, tid):
    t = site.topics.get(tid)
    return t["href"] if t else tid.lower() + ".html"


def draw_index(site, concepts, lay):
    """Under each topic, the concepts it explains, one row each. A concept's definition and
    uses sit in a details element, so the page gives them without a script. The script makes
    each row a card: on a wide screen it fills a panel beside the index, on a phone it opens
    in place."""
    S, topics, read = site.S, site.topics, site.concepts["read"]
    out = []
    for tier in S.tier_ids:
        tier_topics = [tid for g in site.groups.get(tier, []) for tid in g["ids"]
                       if tid in topics and topics[tid]["map"] is not None]
        if not tier_topics:
            continue
        secs = []
        for tid in tier_topics:
            t = topics[tid]
            own = lay["by_home"].get(tid, [])
            if not t["written"] or (not own and tid not in read):
                why = "Not written yet, so it has no concepts." if not t["written"] else "Not read for concepts yet."
                secs.append('<article class="cx-topic-sec is-planned" id="cx-%s" data-cx-topic="%s" data-tier="%s">'
                            '<h4><a href="%s"><span class="cx-tid">%s</span> %s</a></h4>'
                            '<p class="cx-none">%s</p></article>' % (
                                tid.lower(), tid, attr(tier), t["href"], tid, esc(t["title"]), why))
                continue
            items = []
            for c in own:
                rows = "".join(
                    '<li><a class="cx-use" data-for="%s" data-topic="%s" href="%s#%s"><span class="cx-tid">%s</span> %s</a>'
                    '<span class="cx-how">%s</span></li>' % (
                        attr(c["id"]), r["topic"], topic_href(site, r["topic"]), attr(r["anchor"]), r["topic"],
                        esc(topics[r["topic"]]["title"]) if r["topic"] in topics else "", esc(r["how"]))
                    for r in c["refs"])
                # A concept no other topic uses keeps the control for its definition, with no visible label.
                label = ('Used in <span class="count">%d</span>' % len(c["refs"]) if c["refs"]
                         else '<span class="vh">Definition of %s</span>' % esc(c["name"]))
                uses = ('<details class="cx-uses" data-c="%s"><summary%s>%s</summary>'
                        '<p class="cx-def">%s</p>%s</details>' % (
                            attr(c["id"]), "" if c["refs"] else ' class="is-bare"', label, esc(c["definition"]),
                            '<ul class="cx-uses-list">%s</ul>' % rows if rows
                            else '<p class="cx-none">Not used in other topics.</p>'))
                items.append(
                    '<li class="cx-concept" id="c-%s" data-c="%s" data-rank="%s">'
                    '<p class="cx-name">%s <a href="%s#%s" title="%s">%s</a></p>%s</li>' % (
                        attr(c["id"]), attr(c["id"]), attr(c["rank"]), site.rank_chip(c["rank"]),
                        t["href"], attr(c["anchor"]), attr(c["definition"]), esc(c["name"]), uses))
            if not items:
                items.append('<li class="cx-none">No concepts yet.</li>')
            secs.append(
                '<article class="cx-topic-sec" id="cx-%s" data-cx-topic="%s" data-tier="%s">'
                '<h4><a href="%s"><span class="cx-tid">%s</span> %s</a> %s</h4>'
                '<ul class="cx-list">%s</ul></article>' % (
                    tid.lower(), tid, attr(tier), t["href"], tid, esc(t["title"]), site.rank_chip(t["rank"]), "".join(items)))
        out.append('<section class="cx-tier-sec" data-cx-tier-sec="%s"><h3>%s</h3>%s</section>' % (
            attr(tier), esc(tier_name(S, tier)), "".join(secs)))
    return "".join(out)


# ---------------------------------------------------------------- the section at the end of a topic page

def anchor_titles(body, ids):
    """The title of the section or heading behind each anchor, read from the page's own markup.
    An anchor inside a private block gets a plain label, so the table never shows a private title."""
    out = {}
    for i in ids:
        m = re.search(r'<(\w+)\b[^>]*\bid="%s"[^>]*>' % re.escape(attr(i)), body)
        if not m:
            continue
        before = body[:m.start()]
        last_open = before.rfind('<details class="private"')
        if last_open >= 0 and before.find("</details>", last_open) < 0:
            out[i] = "A private section"
            continue
        tag = m.group(1)
        rest = body[m.end():]
        if tag in ("h2", "h3", "h4", "h5"):
            inner = rest.split("</%s>" % tag, 1)[0]
        else:
            hm = re.search(r"<h[2-5][^>]*>(.*?)</h[2-5]>", rest, re.S)
            inner = hm.group(1) if hm else ""
        text = html_unescape(re.sub(r"<[^>]*>", "", inner))
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 90:
            text = text[:90].rsplit(" ", 1)[0] + "…"
        if text:
            out[i] = esc(text)
    return out


def topic_section(site, tid, body):
    """The folded section that ends a topic page: the concepts it explains, and the concepts it
    uses from other topics. `body` is the page's markup so far, for the titles of the sections
    that use each concept. Returns (html, contents entry), or ("", "") when the topic has no
    concepts and no pass has read it."""
    cm = site.concepts
    if not cm:
        return "", ""
    own = [c for c in cm["concepts"] if c["home"] == tid]
    if not own and tid not in cm["read"]:
        return "", ""
    titles = anchor_titles(body, {r["anchor"] for c in cm["concepts"] for r in c["refs"] if r["topic"] == tid})
    order = {t: i for i, t in enumerate(site.map["order"])}
    used = sorted(((c, r) for c in cm["concepts"] for r in c["refs"] if r["topic"] == tid),
                  key=lambda cr: (order.get(cr[0]["home"], 999), cr[0]["name"]))

    rows = []
    for c in own:
        links = ", ".join('<a class="cx-tuse" data-for="%s" data-topic="%s" href="%s#%s" title="%s">%s</a>' % (
            attr(c["id"]), r["topic"], topic_href(site, r["topic"]), attr(r["anchor"]), attr(r["how"]), r["topic"])
            for r in c["refs"]) or '<span class="cx-none">No other topic yet</span>'
        rows.append('<tr data-cx-row="explained" data-c="%s"><td>%s</td><td><a class="cx-tname" href="#%s">%s</a></td><td>%s</td></tr>' % (
            attr(c["id"]), site.rank_chip(c["rank"]), attr(c["anchor"]), esc(c["name"]), links))
    explained = ('<details class="cx-sub"><summary>Concepts explained here <span class="count">%d</span></summary>'
                 '<div class="table-wrap"><table class="cx-ttable" data-cx-table="explained"><thead><tr><th>Rank</th><th>Concept</th><th>Used in</th></tr></thead>'
                 '<tbody>%s</tbody></table></div></details>') % (len(own), "".join(rows))

    if used:
        rows = []
        for c, r in used:
            rows.append(
                '<tr data-cx-row="used" data-c="%s" data-from="%s"><td>%s</td><td>%s</td>'
                '<td><a class="cx-tsec" href="#%s">%s</a></td><td>%s</td><td><a class="cx-thome" href="%s#%s">%s</a></td></tr>' % (
                    attr(c["id"]), c["home"], site.rank_chip(c["rank"]), esc(c["name"]), attr(r["anchor"]),
                    titles.get(r["anchor"]) or esc(r["anchor"]), esc(r["how"]),
                    topic_href(site, c["home"]), attr(c["anchor"]), c["home"]))
        borrowed = ('<details class="cx-sub"><summary>Concepts used here from other topics <span class="count">%d</span></summary>'
                    '<div class="table-wrap"><table class="cx-ttable" data-cx-table="used"><thead><tr><th>Rank</th><th>Concept</th><th>Section of this page</th><th>How</th><th>Explained in</th></tr></thead>'
                    '<tbody>%s</tbody></table></div></details>') % (len(used), "".join(rows))
    else:
        borrowed = '<p class="cx-tnone" data-cx-table="none">This topic uses no concept from other topics.</p>'
    summary = "%d explained here, %d used from other topics" % (len(own), len(used))
    html_ = ('<section class="part part-concepts" id="%s"><h2 class="part-title">Concepts on this page</h2>'
             '<details class="cx-fold"><summary>%s</summary>%s%s'
             '<p class="note"><a href="concepts.html#cx-%s">See these concepts on the concept map</a></p></details></section>') % (
        SECTION_ID, esc(summary), explained, borrowed, tid.lower())
    toc = '<li class="toc-part"><a href="#%s">Concepts on this page</a></li>' % SECTION_ID
    return html_, toc


# ---------------------------------------------------------------- the page

def embedded(site, concepts):
    topics = {}
    for tid, t in site.topics.items():
        if t["map"] is not None:
            topics[tid] = [t["title"], t["href"], t["tier"], t["rank"] or "", 1 if t["written"] else 0]
    rows = [[c["id"], c["name"], c["home"], c["anchor"], c["rank"], c["definition"], c["aliases"],
             [[r["topic"], r["anchor"], r["how"]] for r in c["refs"]]] for c in concepts]
    tiers = {t.id: t.name for t in site.S.tiers}
    text = json.dumps({"topics": topics, "tiers": tiers, "concepts": rows}, ensure_ascii=False, separators=(",", ":"))
    return text.replace("<", "\\u003c").replace("&", "\\u0026")


def page_body(site):
    S = site.S
    concepts = site.concepts["concepts"]
    lay = build_layout(site, concepts)
    svg = draw_map(site, concepts, lay)
    index = draw_index(site, concepts, lay)
    n_refs = sum(len(c["refs"]) for c in concepts)
    n_topics = len({c["home"] for c in concepts})
    n_unused = sum(1 for c in concepts if not c["refs"])
    present = [r for r in RANKS if any(c["rank"] == r for c in concepts)]
    rank_btns = "".join(
        '<button type="button" class="filter" data-cx-rank="%s" aria-pressed="false"><span class="rank-glyph rank-%s" aria-hidden="true"></span> %s</button>'
        % (r, r, esc(S.rank_label(r))) for r in present)
    tier_btns = "".join(
        '<button type="button" class="filter" data-cx-tier="%s" aria-pressed="false">%s</button>' % (attr(t), esc(tier_name(S, t)))
        for t in S.tier_ids if t in lay["tiers"])
    tier_filter = ('<div class="filters cx-filters" role="group" aria-label="Show the concepts of one tier">'
                   '<span class="filters-label">Concepts of</span>%s</div>' % tier_btns) if len(lay["tiers"]) > 1 else ""
    legend = "".join('<li><span class="rank-glyph rank-%s" aria-hidden="true"></span>%s</li>' % (r, esc(S.rank_label(r)))
                     for r in present)
    tier_hint = " To see where one tier's ideas travel, pick that tier." if tier_filter else ""
    return """
<header class="index-head">
  <h1>Concept map</h1>
  <p class="lead">The key ideas of every topic, and where each idea travels. A concept is explained in one topic, its home, and used in others.</p>
  <p class="cx-counts">%(nc)d concepts in %(nt)d topics. %(nr)d uses, %(nu)d concepts used nowhere else. <a href="#cx-index">Skip to the index</a></p>
</header>

<div class="cx-explain">
  <p><span class="cx-js-only">Select a concept to see where it is explained and where it is used. Select a topic to see what it explains and what it uses from other topics.%(tier_hint)s</span>
  <span class="cx-nojs-only">Each concept links to the section that explains it. The index under the map lists where each concept is used.</span></p>
  <p class="cx-key-text">A square is a concept, under the topic that explains it, and its fill shows its rank. A circle is a topic. A curve runs from a concept, at its solid dot, to each topic that uses it, at an open ring.</p>
</div>

<div class="cx-controls" data-cx-controls hidden>
  <div class="gl-find cx-find">
    <label for="cx-q">Find a concept. It matches names and definitions.</label>
    <input id="cx-q" type="search" autocomplete="off" data-cx-input>
  </div>
  <div class="filters cx-filters" role="group" aria-label="Filter concepts by rank"><span class="filters-label">Rank</span>%(rank_btns)s</div>
  %(tier_filter)s
  <button type="button" class="filter-reset" data-cx-reset hidden>Show all</button>
  <p class="gl-status" data-cx-status aria-live="polite"></p>
</div>

<section class="cx-stage" data-cx-stage aria-label="Concept map">
  <ul class="cx-legend" aria-label="Key">
    %(legend)s
    <li class="cx-line-key"><svg viewBox="0 0 54 10" aria-hidden="true"><path d="M5 5 C 20 1, 34 9, 49 5"/><circle class="k-dot" cx="5" cy="5" r="2.6"/><circle class="k-ring" cx="49" cy="5" r="3"/></svg>explained here, used there</li>
  </ul>
  <div class="cx-wrap">
    <div class="cx-frame" data-cx-frame>%(svg)s</div>
    <div class="cx-float cx-float-l"><div class="cx-zoom" data-cx-zoom role="group" aria-label="Zoom" hidden>
      <button type="button" data-cx-zoom-in aria-label="Zoom in">+</button>
      <button type="button" data-cx-zoom-out aria-label="Zoom out">−</button>
      <button type="button" data-cx-zoom-reset>Reset view</button>
    </div></div>
    <div class="cx-float cx-float-r"><aside class="cx-panel" data-cx-panel aria-label="Selected concept or topic" hidden></aside></div>
  </div>
  <p class="cx-hint" data-cx-hint hidden>Drag to pan. Hold Ctrl or Cmd and scroll, or pinch, to zoom. Arrow keys move between concepts, Enter selects, Escape clears.</p>
</section>
<p class="cx-narrow note">The map needs a wider screen. The index below lists every concept, its home and where it is used.</p>
<p class="vh" role="status" aria-live="polite" data-cx-live></p>

<section class="cx-index" id="cx-index" aria-labelledby="cx-index-h">
  <h2 id="cx-index-h">Index of concepts</h2>
  <p class="note">Each topic lists the concepts it explains. Select a concept to see its definition and the topics that use it, each linked to the section that does.</p>
  <div class="cx-index-grid">
    <div class="cx-index-list">%(index)s</div>
    <aside class="cx-index-panel" data-cx-index-panel aria-label="Where the chosen concept is used" hidden></aside>
  </div>
</section>
<script type="application/json" id="cx-data">%(json)s</script>
""" % {"nc": len(concepts), "nt": n_topics, "nr": n_refs, "nu": n_unused, "rank_btns": rank_btns,
       "tier_filter": tier_filter, "tier_hint": tier_hint, "legend": legend, "svg": svg, "index": index,
       "json": embedded(site, concepts)}
