"""The eight checks that run after every build, and the never-publish guard.

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

The guard: nothing on the never-publish list appears anywhere in the site.

engine/README.md explains each check and what to do when it fails.
"""

import json
import re
from html.parser import HTMLParser

from . import terms as T
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
