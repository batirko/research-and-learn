"""The checks that run after every build, and the never-publish guard.

1. Nothing in the site loads from the network.
2. Every topic in the content folder appears, in its tier, with its rank.
3. No internal link is broken, in the pages or in the search index, and the
   open-questions page has an anchor for every question.
4. Light and dark themes are both defined, and the body has a background.
5. Every private tag sits in a collapsed private block, no block starts open,
   and search holds nothing a private block holds.
6. The totals on the home page match the pages.
7. The glossary page shows every term, every home topic exists, and it shows no
   bookkeeping and no private source in the open. The home page and the
   open-questions page show no private source in the open either.
8. The visual index shows every visual once, and a private one by its title only.
9. The concept map, when the guide has a concept file: every concept's home is a
   written topic, every anchor exists, each topic a pass has read has as many
   concepts as limits.concepts_per_topic allows, no concept is used by its own home,
   a concept named in the glossary has the glossary's home, and the page and the
   topic pages show every concept and every use once.

The guard: nothing on the never-publish list appears anywhere in the site.

engine/README.md explains each check and what to do when it fails.
"""

import html
import json
import re
from collections import Counter
from html.parser import HTMLParser

from . import terms as T
from .settings import RANKS
from .topicfile import all_block_lists, block_text, walk_blocks

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class PageScan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ids = set()
        self.links = []
        self.loads = []
        self.private_tags_unmarked = 0
        self.private_tags = 0
        self.body = {}
        self.totals = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "body":
            self.body = {k[5:]: v for k, v in a.items() if k.startswith("data-")}
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "link" and a.get("href"):
            self.loads.append(a["href"])
        if tag in ("script", "img", "iframe", "source", "video", "audio", "embed", "object") and (a.get("src") or a.get("data")):
            self.loads.append(a.get("src") or a.get("data"))
        if a.get("data-total"):
            self.totals[a["data-total"]] = int(a.get("data-minutes", "0"))
        classes = (a.get("class") or "").split()
        if "tag-private" in classes:
            self.private_tags += 1
            if not any(t == "details" and "private" in c for t, c in self.stack):
                self.private_tags_unmarked += 1
        if tag not in VOID:
            self.stack.append((tag, classes))

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def scan(path):
    s = PageScan()
    s.feed(path.read_text(encoding="utf-8"))
    return s


def is_remote(url):
    return re.match(r"^(?:https?:)?//", url) is not None


def words_of(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def load_index(out_dir):
    path = out_dir / "assets" / "search-index.js"
    if not path.exists():
        return None, ""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"window\.GUIDE_SEARCH = (\{.*\});\s*$", text, re.S)
    return (json.loads(m.group(1).replace("<\\/", "</")) if m else None), text


def private_paragraphs(site):
    """(where, line, paragraph) for every paragraph inside a private block: in the written
    topics, the tier introductions, the home page text and the open-questions page."""
    lists = []
    for tid, t in sorted(site.topics.items()):
        if t["written"]:
            lists += [(tid, blocks) for blocks in all_block_lists(t["parsed"])]
    for key, pg in sorted(site.page_files.items()):
        lists.append((key, pg["blocks"]))
    for where, blocks in lists:
        for b in walk_blocks(blocks):
            if b.get("private"):
                for para in re.split(r"\n\s*\n", block_text(b)):
                    yield where, b.get("line"), para


def index_leaks(site, index_text):
    """Private paragraphs whose opening words appear in the search index."""
    S = site.S
    found = words_of(index_text)
    leaks = []
    for m in S.tag_re.finditer(index_text):
        if S.is_private_tag(m.group("tag")):
            leaks.append("a private tag")
            break
    for where, line, para in private_paragraphs(site):
        para = S.ref_re.sub(" ", S.tag_re.sub(" ", para))
        para = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
        probe = words_of(para).split()[:8]
        if len(probe) == 8 and " ".join(probe) in found:
            leaks.append("%s line %s" % (where, line))
    return leaks


def count_private_blocks(blocks):
    return len([b for b in walk_blocks(blocks) if b["type"] == "private"])


def public_main(text):
    """The visible text of a page's <main>, without private blocks, code and attributes."""
    text = re.sub(r'<details class="private"[^>]*>.*?</details>', " ", text, flags=re.S)
    text = re.sub(r"<code>.*?</code>", " ", text, flags=re.S)
    main = text[text.find("<main"):text.find("</main>")]
    return re.sub(r"<[^>]*>", " ", main)


def never_publish_terms(S):
    """The never-publish list, or None when the guide has none. Problems are reported as terms
    can't be trusted half-read."""
    path = S.file("never_publish")
    if not path.exists():
        return None, []
    return T.parse_markdown_list(path.read_text(encoding="utf-8"))


def run(out_dir, site):
    S = site.S
    results = []
    pages = {p.name: scan(p) for p in sorted(out_dir.glob("*.html"))}
    index, index_text = load_index(out_dir)

    # 1. Offline
    remote = []
    for name, s in pages.items():
        remote += ["%s loads %s" % (name, u) for u in s.loads if is_remote(u)]
    for css in (out_dir / "assets").glob("*.css"):
        text = css.read_text(encoding="utf-8")
        for m in re.finditer(r"@import|url\(\s*['\"]?(?:https?:)?//", text):
            remote.append("%s: %s" % (css.name, m.group(0)))
    for js in (out_dir / "assets").glob("*.js"):
        text = js.read_text(encoding="utf-8")
        if js.name == "search-index.js":
            continue   # data: the public text holds links that no page loads
        if re.search(r"\bfetch\(|XMLHttpRequest|WebSocket|EventSource|sendBeacon|https?://", text):
            remote.append("%s might reach the network" % js.name)
    results.append(("1. Nothing loads from the network", not remote, "; ".join(remote[:5])))

    # 2. Every topic in the content folder appears in its tier with its rank
    problems = []
    files = sorted(S.content.glob("*/*/topic.md")) if S.content.exists() else []
    files = [f for f in files if f.parent.parent.name in S.tier_ids]
    for f in files:
        tier_dir = f.parent.parent.name
        m = S.folder_re.match(f.parent.name)
        if not m:
            problems.append("%s has no topic ID in its name" % f.parent.name)
            continue
        tid = m.group(1).upper()
        s = pages.get(tid.lower() + ".html")
        t = site.topics.get(tid)
        if s is None or t is None:
            problems.append("%s has no page" % tid)
            continue
        if s.body.get("status") != "written":
            problems.append("%s shows as planned" % tid)
        if s.body.get("tier") != tier_dir:
            problems.append("%s is in %s but shows under %s" % (tid, tier_dir, s.body.get("tier")))
        header_rank = (t["parsed"] or {}).get("header", {}).get("rank")
        if s.body.get("rank") != header_rank:
            problems.append("%s shows rank %s, its header says %s" % (tid, s.body.get("rank"), header_rank))
        map_rank = (t["map"] or {}).get("rank")
        if map_rank and header_rank != map_rank:
            problems.append("%s: header rank %s differs from the topic map's %s" % (tid, header_rank, map_rank))
        tier_page = pages.get(tier_dir + ".html")
        if tier_page and (tid.lower() + ".html") not in tier_page.links:
            problems.append("%s is missing from the %s page" % (tid, tier_dir))
    results.append(("2. Every topic appears in its tier with its rank", not problems,
                    "; ".join(problems) if problems else "%d topic%s checked" % (len(files), "" if len(files) == 1 else "s")))

    # 3. No broken internal link
    broken = []
    for name, s in pages.items():
        for href in s.links:
            if is_remote(href) or href.startswith(("mailto:", "javascript:")):
                continue
            target, _, frag = href.partition("#")
            target = target or name
            tp = pages.get(target)
            if tp is None:
                if not (out_dir / target).exists():
                    broken.append("%s -> %s" % (name, href))
                continue
            if frag and frag not in tp.ids:
                broken.append("%s -> %s" % (name, href))
    if index is None:
        broken.append("assets/search-index.js is missing or unreadable")
    else:
        for e in index["entries"]:
            t = index["topics"].get(e[0])
            tp = pages.get(t[1]) if t else None
            if tp is None or (e[1] and e[1] not in tp.ids):
                broken.append("search index -> %s#%s" % (t[1] if t else e[0], e[1]))
    qpage = pages.get("questions.html")
    if qpage is not None and site.page_files.get("questions"):
        for qid in sorted(site.questions):
            if qid.lower() not in qpage.ids:
                broken.append("questions.html has no anchor for %s" % qid)
    results.append(("3. No broken internal link", not broken,
                    "; ".join(sorted(set(broken))[:8]) if broken else "%d pages" % len(pages)))

    # 4. Both themes defined
    tokens = (out_dir / "assets" / "tokens.css").read_text(encoding="utf-8")
    themed = ("prefers-color-scheme: dark" in tokens and ':root[data-theme="dark"]' in tokens
              and "--color-paper" in tokens)
    site_css = (out_dir / "assets" / "site.css").read_text(encoding="utf-8")
    body_bg = re.search(r"\bbody\s*\{[^}]*background:\s*var\(--color-paper\)", site_css) is not None
    results.append(("4. Light and dark themes are defined, and body has a background", themed and body_bg,
                    "rendering is checked by eye"))

    # 5. Private facts marked, or, in a shared copy, left out
    if site.share:
        results.append(check_shared(out_dir, site, pages, index_text))
    else:
        results.append(check_private(out_dir, site, pages, index_text))

    results += checks_6_to_8(out_dir, site, pages)
    if site.concepts is not None:
        results.append(check_concepts(out_dir, site, pages, index_text))
    results.append(guard(out_dir, S))
    return results


def check_shared(out_dir, site, pages, index_text):
    """A shared copy holds no private block, no private tag, and nowhere the opening words
    of a private paragraph: not in a page, not in the search index."""
    S = site.S
    found = []
    texts = {}
    for name in pages:
        raw = (out_dir / name).read_text(encoding="utf-8")
        if '<details class="private"' in raw:
            found.append("%s holds a private block" % name)
        if pages[name].private_tags:
            found.append("%s shows %d private tags" % (name, pages[name].private_tags))
        texts[name] = words_of(re.sub(r"<[^>]+>", " ", raw))
    texts["search index"] = words_of(index_text)
    probes = [(where, line, para) for where, line, para in private_paragraphs(site)]
    for sec in site.glossary:
        for r in sec["rows"]:
            probes += [("glossary", r["line"], x) for x in r["private"]]
        for note in sec["notes"]:
            probes += [("glossary", None, x) for x in note["private"]]
    for tid, t in site.topics.items():
        if not t["written"] and t["map"] is not None:
            for _, text in t["map"]["fields"]:
                # The planned page leaves out each paragraph, list or table that cites a private
                # source. The line that carries the tag is in it, so that line is the probe.
                for line in text.split("\n"):
                    if S.has_private_tag(re.sub(r"`(\[[^`\]]+\])`", r"\1", line)):
                        probes.append(("the map's entry for %s" % tid, None, line))
    for where, line, para in probes:
        para = S.ref_re.sub(" ", S.tag_re.sub(" ", para))
        para = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", para)
        probe = " ".join(words_of(para).split()[:8])
        if len(probe.split()) == 8:
            hits = [name for name, text in texts.items() if probe in text]
            if hits:
                found.append("a private paragraph (%s%s) shows in %s" % (where, " line %s" % line if line else "", ", ".join(hits[:3])))
    left_out = sum((out_dir / n).read_text(encoding="utf-8").count('class="private private-stub private-omitted"') for n in pages)
    return ("5. A shared copy: no private block, no private tag, and no private paragraph anywhere in the site", not found,
            "; ".join(found[:6]) if found else "%d private paragraphs probed; %d private blocks left out" % (len(probes), left_out))


def check_private(out_dir, site, pages, index_text):
    S = site.S
    unmarked = ["%s (%d)" % (name, s.private_tags_unmarked) for name, s in pages.items() if s.private_tags_unmarked]
    total_private = sum(s.private_tags for s in pages.values())
    leaks = index_leaks(site, index_text)
    unmarked += ["search index holds %s" % x for x in leaks]
    for name in pages:
        if re.search(r'<details class="private"[^>]*\sopen\b', (out_dir / name).read_text(encoding="utf-8")):
            unmarked.append("%s has a private block that starts open" % name)
    covered = []
    for key, name in (("home", "index.html"), ("questions", "questions.html")):
        pg = site.page_files.get(key)
        if not pg or name not in pages:
            continue
        want = count_private_blocks(pg["blocks"])
        got = (out_dir / name).read_text(encoding="utf-8").count('<details class="private"')
        if got != want:
            unmarked.append("%s has %d private blocks, %s shows %d" % (pg["path"], want, name, got))
        covered.append("%s %d" % (name, want))
    return ("5. Every private tag sits in a collapsed private block, and search leaves private blocks out", not unmarked,
            "; ".join(unmarked) if unmarked else "%d private tags, all inside private blocks; none in the search index%s" % (
                total_private, ("; private blocks on " + ", ".join(covered)) if covered else ""))


def checks_6_to_8(out_dir, site, pages):
    S = site.S
    results = []

    # 6. Totals on the home page match the pages
    home = pages.get("index.html")
    mism = []
    if home:
        topic_pages = [s for s in pages.values() if s.body.get("page") == "topic" and s.body.get("tier") in S.tier_ids
                       and site.topics.get(s.body.get("id"), {}).get("map") is not None]

        def total(pred):
            return sum(int(s.body.get("minutes", 0)) for s in topic_pages if pred(s.body))
        expect = {"all-all": total(lambda b: True), "all-written": total(lambda b: b.get("status") == "written")}
        for tier in S.tier_ids:
            expect["tier-%s-all" % tier] = total(lambda b, t=tier: b.get("tier") == t)
            expect["tier-%s-written" % tier] = total(lambda b, t=tier: b.get("tier") == t and b.get("status") == "written")
        for rank in ("critical", "high", "medium", "context"):
            if "rank-%s-all" % rank in home.totals:
                expect["rank-%s-all" % rank] = total(lambda b, r=rank: b.get("rank") == r)
        mats = {}
        for t in site.topics.values():
            if t["written"] and t["map"] is not None:
                for m in t["parsed"]["materials"]:
                    mats[m["rank"]] = mats.get(m["rank"], 0) + (m["minutes"] or 0)
        for rank in ("critical", "high", "medium", "context"):
            expect["mat-%s" % rank] = mats.get(rank, 0)
        for key, value in expect.items():
            if home.totals.get(key) != value:
                mism.append("%s: home says %s, pages add up to %s" % (key, home.totals.get(key), value))
    results.append(("6. Home page totals match the pages", home is not None and not mism,
                    "; ".join(mism) if mism else "%d totals compared" % (len(home.totals) if home else 0)))

    # 7. Glossary page, and private sources in the open on the pages written as text
    gl_problems = []
    gpath = out_dir / "glossary.html"
    if not gpath.exists():
        gl_problems.append("glossary.html is missing")
    else:
        text = gpath.read_text(encoding="utf-8")
        rows = sum(len(sec["rows"]) for sec in site.glossary)
        shown = len(re.findall(r'<div class="gl-row"', text))
        if shown != rows:
            gl_problems.append("%d terms in the glossary, %d rows on the page" % (rows, shown))
        for sec in site.glossary:
            for r in sec["rows"]:
                for h in r["homes"]:
                    if h not in site.topics:
                        gl_problems.append("%s names home %s, which isn't in the topic map" % (r["anchor"], h))
        main = public_main(text)
        bookkeeping = []
        if S.decision_re:
            bookkeeping.append(S.decision_re.pattern)
        for word in S.glossary["bookkeeping"]:
            bookkeeping.append(r"\b%s (?:from|in|on|by|at|20\d\d)\b" % re.escape(word))
        if bookkeeping:
            for m in re.finditer("|".join(bookkeeping), main):
                gl_problems.append("bookkeeping on the page: %s" % m.group(0))
        if S.glossary_source_re:
            for m in S.glossary_source_re.finditer(main):
                gl_problems.append("a private source outside a private block: %s" % m.group(0))
    text_pages = []
    for key, name in (("home", "index.html"), ("questions", "questions.html")):
        if site.page_files.get(key) and (out_dir / name).exists():
            text_pages.append(name)
            if S.page_source_re:
                main = public_main((out_dir / name).read_text(encoding="utf-8"))
                for m in S.page_source_re.finditer(main):
                    gl_problems.append("%s names a private source outside a private block: %s" % (name, m.group(0)))
    results.append(("7. Glossary: every term shown, every home topic exists, no bookkeeping or private source in the open%s" % (
                        "; the same for " + " and ".join(text_pages) if text_pages else ""),
                    not gl_problems, "; ".join(gl_problems[:6]) if gl_problems else
                    "%d terms in %d sections" % (sum(len(s["rows"]) for s in site.glossary), len(site.glossary))))

    # 8. Visual index
    vx_problems = []
    vpath = out_dir / "visuals.html"
    expected = 0
    for t in site.topics.values():
        if t["written"]:
            expected += len(t["parsed"].get("visuals", []))
    for tier in S.tier_ids:
        intro = S.intro(tier)
        if intro.exists():
            expected += len(re.findall(r"^:::visual\b", intro.read_text(encoding="utf-8"), re.M))
    n_private = 0
    if not vpath.exists():
        vx_problems.append("visuals.html is missing")
    else:
        text = vpath.read_text(encoding="utf-8")
        arts = re.findall(r'<article class="vx( vx-private)?" id="([^"]+)">(.*?)</article>', text, re.S)
        ids = [a[1] for a in arts]
        if len(arts) != expected:
            vx_problems.append("%d visuals in the topics, %d on the index" % (expected, len(arts)))
        if len(set(ids)) != len(ids):
            vx_problems.append("an entry appears twice")
        for private, vid, inner in arts:
            if private:
                n_private += 1
                if "<svg" in inner or "visual-caption" in inner or "vx-job" in inner:
                    vx_problems.append("%s is private but shows more than its title" % vid)
            elif "<svg" not in inner:
                vx_problems.append("%s has no drawing" % vid)
        # Read privacy from the topic sources, not from what the renderer recorded.
        page_words = words_of(re.sub(r"<[^>]+>", " ", text))
        sources = [(t["id"], v) for t in site.topics.values() if t["written"] for v in t["parsed"].get("visuals", [])]
        for tid, v in sources:
            if v.get("private"):
                for field in ("caption", "job", "alt"):
                    probe = words_of(S.ref_re.sub(" ", S.tag_re.sub(" ", v.get(field, "")))).split()[:8]
                    if len(probe) == 8 and " ".join(probe) in page_words:
                        vx_problems.append("the %s of a private visual in %s is on the index" % (field, tid))
        if n_private != len([1 for _, v in sources if v.get("private")]):
            vx_problems.append("%d private visuals in the topics, %d shown as private" % (
                len([1 for _, v in sources if v.get("private")]), n_private))
    results.append(("8. Visual index: every visual once, a private one by its title only", not vx_problems,
                    "; ".join(vx_problems[:6]) if vx_problems else "%d visuals, %d of them private" % (expected, n_private)))
    return results


def term_key(text):
    return re.sub(r"\s+", " ", re.sub(r"[*_`]", "", text)).strip().lower()


def check_concepts(out_dir, site, pages, index_text):
    """9. The concept map and the section that ends every topic page match the concept file."""
    S, cm = site.S, site.concepts
    problems = list(cm["problems"])
    concepts, read = cm["concepts"], cm["read"]
    low, high = S.limits["concepts_per_topic"]
    glossary_homes = {}
    for sec in site.glossary or []:
        for row in sec["rows"]:
            if row["homes"]:
                glossary_homes[term_key(row["use"])] = (row["use"], row["homes"])

    def written(tid):
        t = site.topics.get(tid)
        return t if t and t["written"] and t["map"] is not None else None

    seen, per_topic, want_refs = set(), Counter(), []
    for c in concepts:
        cid = c["id"]
        if not cid or cid in seen:
            problems.append("concept id %r is empty or appears twice" % cid)
        seen.add(cid)
        if c["rank"] not in RANKS:
            problems.append("%s has rank %r" % (cid, c["rank"]))
        if not c["name"] or not c["definition"]:
            problems.append("%s has no name or no definition" % cid)
        home = written(c["home"])
        if home is None:
            problems.append("%s: its home %s isn't a written topic in the topic map" % (cid, c["home"]))
        else:
            per_topic[c["home"]] += 1
            hp = pages.get(home["href"])
            if hp is None or c["anchor"] not in hp.ids:
                problems.append("%s: no anchor %s on %s" % (cid, c["anchor"], home["href"]))
        for name in [c["name"]] + c["aliases"]:
            g = glossary_homes.get(term_key(name))
            if g and c["home"] not in g[1]:
                problems.append("%s: the glossary says %s is the home of %s" % (cid, " or ".join(g[1]), g[0]))
        targets = set()
        for r in c["refs"]:
            want_refs.append((cid, r["topic"]))
            if r["topic"] == c["home"]:
                problems.append("%s is used by its own home %s" % (cid, c["home"]))
            if r["topic"] in targets:
                problems.append("%s is used by %s twice" % (cid, r["topic"]))
            targets.add(r["topic"])
            t = written(r["topic"])
            if t is None:
                problems.append("%s: a use in %s, which isn't a written topic in the topic map" % (cid, r["topic"]))
            else:
                tp = pages.get(t["href"])
                if tp is None or r["anchor"] not in tp.ids:
                    problems.append("%s: no anchor %s on %s" % (cid, r["anchor"], t["href"]))
            if not r["how"]:
                problems.append("%s: its use in %s has no how line" % (cid, r["topic"]))
    for tid in read:
        if written(tid) is None:
            problems.append("the file says a pass read %s, which isn't a written topic in the topic map" % tid)
    # A topic no pass has read yet may have no concepts. A topic a pass has read needs its share.
    covered = [tid for tid in site.map["order"] if written(tid) and (tid in read or per_topic[tid])]
    for tid in covered:
        if not low <= per_topic[tid] <= high:
            problems.append("%s has %d concepts, and a topic needs %d to %d" % (tid, per_topic[tid], low, high))

    page = out_dir / "concepts.html"
    if not page.exists():
        problems.append("concepts.html is missing")
    else:
        text = page.read_text(encoding="utf-8")
        want_c = Counter(html.escape(c["id"]) for c in concepts if written(c["home"]))
        want_r = Counter((html.escape(a), b) for a, b in want_refs)

        def same(label, pattern, want):
            have = Counter(re.findall(pattern, text))
            if have != want:
                problems.append("%s: %d shown, %d in the file (missing %s, extra %s)" % (
                    label, sum(have.values()), sum(want.values()),
                    sorted((want - have).keys())[:3], sorted((have - want).keys())[:3]))
        same("map leaves", r'<a class="cx-leaf" [^>]*?data-c="([^"]*)"', want_c)
        same("map curves", r'<path class="cx-ref" data-from="([^"]*)" data-to="([^"]*)"',
             Counter({k: v for k, v in want_r.items() if html.unescape(k[0]) in {c["id"] for c in concepts if written(c["home"])}}))
        same("index concepts", r'<li class="cx-concept" id="[^"]*" data-c="([^"]*)"', want_c)
        same("index uses", r'<a class="cx-use" data-for="([^"]*)" data-topic="([^"]*)"',
             Counter({k: v for k, v in want_r.items() if html.unescape(k[0]) in {c["id"] for c in concepts if written(c["home"])}}))
        home_of = {html.escape(c["id"]): c["home"] for c in concepts}
        for sec in re.finditer(r'<article class="cx-topic-sec[^"]*" id="cx-[^"]*" data-cx-topic="([^"]*)"(.*?)</article>', text, re.S):
            for cid in re.findall(r'<li class="cx-concept" id="[^"]*" data-c="([^"]*)"', sec.group(2)):
                if home_of.get(cid) != sec.group(1):
                    problems.append("the index lists %s under %s, which isn't its home" % (cid, sec.group(1)))
        blob = re.search(r'<script type="application/json" id="cx-data">(.*?)</script>', text, re.S)
        try:
            payload = json.loads(blob.group(1))
            if len(payload["concepts"]) != len(concepts) or sum(len(r[7]) for r in payload["concepts"]) != len(want_refs):
                problems.append("the page's data differs from the concept file")
        except (AttributeError, ValueError, KeyError):
            problems.append("the page's data is missing or unreadable")

    # Every covered topic page ends with the folded section, and its tables match the file.
    for tid in covered:
        t = written(tid)
        path = out_dir / t["href"]
        if not path.exists():
            continue
        ptext = path.read_text(encoding="utf-8")
        if ptext.count('id="concepts-on-this-page"') != 1 or 'href="#concepts-on-this-page"' not in ptext:
            problems.append("%s: the concepts section must appear once, with an entry in the contents" % tid)
            continue
        if re.search(r'<details class="cx-fold"[^>]*\sopen\b', ptext):
            problems.append("%s: the concepts section starts open" % tid)
        sec_text = ptext[ptext.index('id="concepts-on-this-page"'):]
        own = {c["id"]: c for c in concepts if c["home"] == tid}
        uses = [(c, r) for c in concepts for r in c["refs"] if r["topic"] == tid]
        rows = re.findall(r'<tr data-cx-row="explained" data-c="([^"]*)"><td>.*?</td><td><a class="cx-tname" href="#([^"]*)">(.*?)</a></td><td>(.*?)</td></tr>', sec_text, re.S)
        if Counter(html.unescape(r[0]) for r in rows) != Counter(own.keys()):
            problems.append("%s: the explained table shows %d concepts, the file has %d" % (tid, len(rows), len(own)))
        for cid, anchor, name, cell in rows:
            c = own.get(html.unescape(cid))
            if c is None:
                continue
            if html.unescape(anchor) != c["anchor"] or html.unescape(name) != c["name"]:
                problems.append("%s: the explained row for %s links to the wrong section" % (tid, c["id"]))
            want = Counter((r["topic"], r["anchor"], r["how"]) for r in c["refs"])
            have = Counter((m.group(1), html.unescape(m.group(2)).split("#", 1)[1], html.unescape(m.group(3)))
                           for m in re.finditer(r'<a class="cx-tuse" data-for="[^"]*" data-topic="([^"]*)" href="([^"]*)" title="([^"]*)"', cell))
            if want != have:
                problems.append("%s: the explained row for %s lists the wrong uses" % (tid, c["id"]))
        urows = re.findall(r'<tr data-cx-row="used" data-c="([^"]*)" data-from="([^"]*)"><td>.*?</td><td>.*?</td><td><a class="cx-tsec" href="#([^"]*)">.*?</a></td><td>(.*?)</td><td><a class="cx-thome" href="([^"]*)">', sec_text, re.S)
        have = Counter((html.unescape(r[0]), html.unescape(r[2]), html.unescape(r[3])) for r in urows)
        if have != Counter((c["id"], r["anchor"], r["how"]) for c, r in uses):
            problems.append("%s: the used table shows %d rows, the file has %d, or a row differs" % (tid, len(urows), len(uses)))
        by_id = {c["id"]: c for c in concepts}
        for r in urows:
            c = by_id.get(html.unescape(r[0]))
            if c and (c["home"] != r[1] or not html.unescape(r[4]).endswith("#" + c["anchor"])):
                problems.append("%s: the used row for %s names the wrong home" % (tid, c["id"]))
        if bool(uses) == ('data-cx-table="none"' in sec_text):
            problems.append("%s: the section says %s, and the file disagrees" % (
                tid, "it uses nothing from other topics" if uses else "it uses concepts from other topics"))
    # Search leaves the section out: it repeats the concept file.
    if index_text and ("cx-ttable" in index_text or "Concepts on this page" in index_text):
        problems.append("the search index holds the concepts section")

    n_refs = len(want_refs)
    return ("9. Concept map: every home written, every anchor found, %d to %d concepts a topic, no use by its own home, "
            "homes agree with the glossary, every concept and use shown once" % (low, high),
            not problems, "; ".join(problems[:6]) if problems else "%d concepts, %d uses, %d topics" % (
                len(concepts), n_refs, len(covered)))


def guard(out_dir, S):
    """What never reaches the portal."""
    terms, list_problems = never_publish_terms(S)
    flagged = list(list_problems)
    if terms:
        for p in sorted(out_dir.rglob("*")):
            if not p.is_file() or p.suffix not in (".html", ".js", ".css", ".svg"):
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            for t, m in T.find(terms, text):
                flagged.append("%s line %d: %s" % (p.relative_to(out_dir), T.line_of(text, m.start()), t.raw))
    if terms is None:
        detail = "no list at %s" % S.paths["never_publish"]
    elif flagged:
        detail = "; ".join(flagged[:6])
    else:
        detail = "%d term%s, none in the site" % (len(terms), "" if len(terms) == 1 else "s")
    return ("Guard: nothing on the never-publish list reaches the site", not flagged, detail)
