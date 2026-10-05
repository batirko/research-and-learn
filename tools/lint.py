#!/usr/bin/env python3
"""Lint the writing of a guide's topics.

    python3 tools/lint.py                       every topic in the content folder
    python3 tools/lint.py content/practical/p01-inspecting-a-hive
    python3 tools/lint.py content/ --strict     warnings fail the run too
    python3 tools/lint.py notes/draft.md        any other .md file: prose checks only
    python3 tools/lint.py --rules               every rule and its severity

Exit code 0: no errors. 1: at least one error (or a warning, with --strict).
2: bad usage, or settings that don't load.

The format check, engine/topic.py, checks a topic's structure. This script
reuses it, so a structure error appears once, as the rule "structure". It adds
the checks of writing: dashes, words the glossary bans, first person, tags, the
never-publish list, materials and size. Every limit comes from guide.toml.

A finding can be silenced where it is a false positive. Put a comment on the
same line or on the line above. The build drops comments.

    <!-- lint-ignore: simple-easy-quick -->
    <!-- lint-ignore -->                  (every rule on that line)

Python 3.11 or later, standard library only.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))

from core import glossary as G  # noqa: E402
from core import terms as TERMS  # noqa: E402
from core import topicfile as T  # noqa: E402
from core import topicmap  # noqa: E402
from core.settings import SettingsError, find_settings, load  # noqa: E402

E, W = "error", "warning"

# ---------------------------------------------------------------- rules
# id: (severity, what it catches)

RULES = {
    # Absolute rules: errors.
    "dash": (E, "Em dash, en dash or double hyphen in prose. Quotes, code, URLs and tags are exempt."),
    "bad-tag": (E, "A bracketed provenance tag the settings don't define. A malformed private tag hides a private fact from the private check."),
    "placeholder": (E, "TODO, TBD, FIXME or a similar placeholder left in the text."),
    "example-link": (E, "A link to example.com, example.org or example.net."),
    "emoji": (E, "An emoji."),
    "first-person": (E, "'we', 'I' or 'our' in guide text. The guide has no first person."),
    "simple-easy-quick": (E, "Calls something simple, easy or quick."),
    "glossary-ban": (E, "A word the glossary bans in every sense, from its 'Don't use' column or lint.ban."),
    "never-publish": (E, "Something on the never-publish list. It never enters a topic."),
    "materials-ceiling": (E, "More materials than materials.per_topic."),
    "link-empty": (E, "A Markdown link with no target."),
    "critical-total": (E, "More critical materials across the topics than materials.critical_in_guide."),
    "critical-cluster": (E, "More critical materials in a cluster than its quota in the topic map."),
    "xl-total": (E, "More XL topics than sizes.xl_allowed."),
    "duplicate-id": (E, "Two topic folders carry the same ID."),
    "structure": (E, "A finding of the format check, carried over once. Run engine/topic.py for detail."),
    # Heuristics: warnings.
    "quote-unbalanced": (W, "A quotation mark with no partner in its paragraph. Quoted text is exempt from the prose rules only when the quotes pair up."),
    "dash-spaced": (W, "A spaced hyphen between words reads as a dash."),
    "range-hyphen": (W, "A numeric range written with a hyphen. Write 'to'."),
    "glossary-sense": (W, "A word the glossary bans in one sense, from an italic word in its 'Don't use' column or lint.sense."),
    "first-person-soft": (W, "'us', 'me', 'my' or 'mine' in guide text."),
    "bare-should": (W, "'should' with no 'must', 'can' or 'a good default is'."),
    "filler": (W, "A filler adverb."),
    "inflated": (W, "An inflated verb or adjective."),
    "slop-phrase": (W, "A throat-clearing opener, a claim of rare insight, or a stock phrase."),
    "contrast-frame": (W, "'It's not X, it's Y.' State Y."),
    "spelling": (W, "A spelling from the other side of the Atlantic than guide.spelling asks for."),
    "sentence-long": (W, "A sentence far over the length limit."),
    "paragraph-long": (W, "A paragraph of more sentences than limits.paragraph_sentences."),
    "why-length": (W, "'Why it matters' outside limits.why_sentences."),
    "heading-case": (W, "A heading in Title Case. Use sentence case."),
    "heading-vague": (W, "A heading that names a topic and says nothing."),
    "date-format": (W, "A date in prose that isn't written '4 October 2026'."),
    "case-untagged": (W, "A paragraph that names the case (case.terms) and carries no provenance tag or open-question link."),
    "case-guess": (W, "A hedged claim about the case with no [inference], [unverified] or open-question link."),
    "abbreviation": (W, "An abbreviation from lint.abbreviations used before it is spelled out."),
    "private-source": (W, "Names a private source outside a private block (privacy.source_words)."),
    "reader-name": (W, "Names the reader (guide.reader). Guide text says 'you'."),
    "private-label": (W, "A private block label that is long or holds a number or a quote. A label names the subject and never the fact."),
    "private-no-tag": (W, "A private block with no provenance tag inside it."),
    "meta-leak": (W, "Process language in guide text (lint.meta_words)."),
    "link-text": (W, "Link text such as 'here' or 'this link'."),
    "link-target": (W, "A link that isn't https. Topics link with [[ID]]."),
    "bare-url": (W, "A URL in the text with no link text."),
    "link-tracking": (W, "A tracking parameter in a link."),
    "material-date": (W, "A material in a tier whose facts age fast, dated with a year and no month."),
    "material-old": (W, "A material in a fast tier older than materials.max_age_months, whose 'what you get' gives no reason for its age."),
    "material-duplicate": (W, "Two materials with the same link."),
    "material-exercise": (W, "An exercise that isn't free, when materials.exercises_free is on."),
    "material-length": (W, "'what you get' or 'passed over' longer than two sentences."),
    "map-mismatch": (W, "The header differs from the topic map: title, rank, size or cluster."),
    "size": (W, "Words outside the size band. An error above the XL ceiling: that is two topics."),
}

# ---------------------------------------------------------------- patterns

INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
# A quotation opens after a non-word character and closes before one, so an inch mark (5") or a
# mixed pair (curly open, straight close) can't shift the pairing and expose quoted text.
QUOTE_RE = re.compile("(?<!\\w)[\"“](?=[^\\s\"”])[^\"“”]*?(?<=[^\\s\"“])[\"”](?!\\w)")
STRAY_QUOTE_RE = re.compile("(?<!\\d)[\"“”]")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
MDLINK_RE = re.compile(r"\[([^\]\n]*)\]\(([^)\n]*)\)")
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’-]*")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LIST_RE = re.compile(r"^(\s*)(?:[-*]|\d+\.)\s+")
FIELD_LINE_RE = re.compile(r"^-\s+([a-z][a-z ]*?)\s*:\s?")
VFIELD_RE = re.compile(r"^(?:title|job|alt|credit):\s*")
RANK_TAIL_RE = re.compile(r"\s*\{(?:critical|high|medium|context)\}\s*$", re.I)
TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")
COMMENT_RE = re.compile(r"<!--(.*?)-->", re.S)
IGNORE_RE = re.compile(r"^\s*lint-ignore(?:\s*:\s*(?P<rules>[a-z0-9, -]+?))?\s*$")
ABBR_RE = re.compile(r"\b(?:e\.g|i\.e|vs|cf|approx|Inc|Ltd|Dr|Mr|Mrs|Ms|St|U\.S)\.", re.I)
SENT_SPLIT_RE = re.compile(r"[.!?][\"')\]]*\s+(?=[\"'(\[]?[A-Z0-9])")
TOPIC_LINK_RE = re.compile(r"\[\[[^\]]*\]\]")
BOLD_RE = re.compile(r"\*\*[^*\n]+\*\*")

# A material older than the age limit passes when its "what you get" says why it is still listed.
AGE_REASON_RE = re.compile(
    r"\breason for its age\b|\b\d+ months old\b|\bolder than \d+ months\b|\bdates from\b|\bno newer\b|\bstill the\b", re.I)

AIM_SENTENCE = 25
AIM_ACTION_SENTENCE = 20

DASH_RE = re.compile("[‒–—―⸺⸻]|-{2,}")
SPACED_HYPHEN_RE = re.compile(r"(?<=[A-Za-z0-9)\]\"'.,’]) - (?=[A-Za-z0-9(\[\"'‘“])")
RANGE_RE = re.compile(r"\b\d+\s?-\s?\d+\b")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF✅❌❎✨⭐⭕⚠❗❓]")
PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|TBD|FIXME|XXX|PLACEHOLDER|TK)\b|\?\?\?|(?i:lorem ipsum|\[citation needed\]|<insert|\[insert)")
EXAMPLE_LINK_RE = re.compile(r"https?://(?:[\w-]+\.)*example\.(?:com|org|net)\b")
TRACKING_RE = re.compile(r"[?&](?:utm_[a-z]+|fbclid|gclid|mc_cid|ref|ref_src)=", re.I)

# First person. Case matters for "I".
FIRST_PERSON_RE = re.compile(
    r"\b[Ww]e\b|\b[Ww]e['’](?:re|ve|ll|d)\b|\b[Oo]ur\b|\b[Oo]urs\b|\b[Oo]urselves\b"
    r"|(?<![\w/-])(?<!Type )(?<!Phase )(?<!Level )(?<!Part )(?<!Class )(?<!Tier )(?<!Section )(?<!Chapter )I(?![\w/-])")
FIRST_PERSON_SOFT_RE = re.compile(r"(?<![-\w])us(?![-\w])|\b[Mm]y\b|\b[Mm]e\b|\b[Mm]ine\b")

SIMPLE_RE = re.compile(r"\b(?:simpl(?:e|er|est|y)|easy|easier|easiest|easily|quick|quicker|quickest|quickly)\b", re.I)
SHOULD_RE = re.compile(r"\bshould(?:n['’]t| not)?\b", re.I)
FILLER_RE = re.compile(
    r"\b(?:really|truly|fundamentally|basically|essentially|genuinely|honestly|obviously|literally|certainly|definitely)\b", re.I)
INFLATED_RE = re.compile(
    r"\b(?:leverag(?:e|es|ed|ing)|utili[sz](?:e|es|ed|ing)|empower(?:s|ed|ing)?|streamlin(?:e|es|ed|ing)"
    r"|delv(?:e|es|ed|ing)|seamless(?:ly)?|holistic(?:ally)?|synerg(?:y|ies)|game[- ]chang(?:er|ers|ing)"
    r"|cutting[- ]edge|best[- ]in[- ]class|paradigm shift|robust|transformative|supercharg(?:e|es|ed|ing))\b", re.I)
SLOP_RE = re.compile(
    r"\bhere['’]s the thing\b|\bit['’]?s worth (?:noting|mentioning)\b|\bit is worth (?:noting|mentioning)\b"
    r"|\bworth noting that\b|\bit['’]s important to (?:note|understand|remember)\b|\bit is important to (?:note|understand|remember)\b"
    r"|\bwhat most people miss\b|\bthe truth is\b|\bthe reality is\b|\blet['’]s be (?:clear|honest)\b|\bat the end of the day\b"
    r"|\bneedless to say\b|\ba testament to\b|\bat its core\b|\bthe key (?:takeaway|insight) is\b"
    r"|\bplays? an? (?:crucial|key|vital|pivotal) role\b|\bin today['’]s\b|\bwhen it comes to\b", re.I)
CONTRAST_RE = re.compile(
    r"\b(?:isn['’]t|is not|aren['’]t|are not|wasn['’]t|not just|not only|not merely)\b[^.!?\n]{1,70}?"
    r"[;,]\s*(?:it['’]s|it is|they['’]re|they are|but|rather|instead)\b", re.I)

# Spelling. British forms on the left of each pair, American on the right. Stems end where
# the "s" or "z" of an -ise or -ize word would sit.
IZE_STEMS = (
    "organi authori standardi normali optimi prioriti summari recogni reali minimi maximi customi categori centrali "
    "generali visuali operationali utili capitali finali formali initiali synchroni seriali moneti moderni harmoni "
    "materiali personali digiti itemi mobili stabili apologi emphasi critici legali locali globali virtuali containeri "
    "commoditi democrati ideali familiari revolutioni incentivi saniti randomi parameteri tokeni speciali characteri"
).split()
ENDINGS = "(?:e|es|ed|ing|ation|ations|er|ers)"
WORD_PAIRS = [
    (r"colours?|coloured|colouring|colourful", r"colors?|colored|coloring|colorful", "colour", "color"),
    (r"behaviours?|behavioural|behaviourally", r"behaviors?|behavioral|behaviorally", "behaviour", "behavior"),
    (r"favours?|favoured|favouring|favourite|favourites", r"favors?|favored|favoring|favorite|favorites", "favour", "favor"),
    (r"honours?|honoured|honouring", r"honors?|honored|honoring", "honour", "honor"),
    (r"neighbours?|neighbouring|neighbourhood", r"neighbors?|neighboring|neighborhood", "neighbour", "neighbor"),
    (r"labour|flavours?|humour|rumours?|harbours?|endeavours?", r"labor|flavors?|humor|rumors?|harbors?|endeavors?", "-our", "-or"),
    (r"centres?|centred|centring", r"centers?|centered|centering", "centre", "center"),
    (r"fibres?|theatres?|metres?|litres?", r"fibers?|theaters?|meters?|liters?", "-re", "-er"),
    (r"catalogues?|catalogued|cataloguing", r"catalogs?|cataloged|cataloging", "catalogue", "catalog"),
    (r"defence|offence", r"defense|offense", "-ce", "-se"),
    (r"greys?", r"grays?", "grey", "gray"),
    (r"sceptic\w*", r"skeptic\w*", "sceptic", "skeptic"),
    (r"fulfil(?:s|ment)?", r"fulfill(?:s|ment)?", "fulfil", "fulfill"),
    (r"enrol(?:s|ment)?", r"enroll(?:s|ment)?", "enrol", "enroll"),
    (r"(?:model|label|cancel|travel|signal|level|channel|fuel|total|panel|tunnel)l(?:ed|ing)",
     r"(?:model|label|cancel|travel|signal|level|channel|fuel|total|panel|tunnel)(?:ed|ing)", "double l", "single l"),
]
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|(?<![\d-])\d{4}-(?:0[1-9]|1[0-2])(?![\d-])")
US_DATE_RE = re.compile(
    r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?"
    r"|Nov(?:ember)?|Dec(?:ember)?)\.? \d{1,2}(?:st|nd|rd|th)?,? \d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b")

# A sentence that says something is unknown, hypothetical or defined makes no claim about the case.
NO_CLAIM_RE = re.compile(
    r"\bunknown\b|\bunclear\b|\bunconfirmed\b|\bwhether\b|\bopen questions?\b|\bnobody (?:outside [\w ]{1,30} )?(?:knows|has)\b"
    r"|\bnot (?:yet )?(?:known|stated|confirmed|public)\b|\bisn['’]t (?:known|stated|confirmed|public|on the record)\b"
    r"|^\s*(?:If|Suppose)\b", re.I)
DEFINITION_RE = re.compile(r"^\s*\*\*[^*]+\*\*(?:,[^.,]{0,40},)?\s+(?:is|means|are)\b")   # "**Swarm** is ...": a term defined
HEDGE_RE = re.compile(r"\b(?:probably|presumably|likely|perhaps|maybe|supposedly|appears? to|seems? to)\b", re.I)
SOFT_TAG_KINDS = ("inference", "unverified")
CASE_PARTS = {"why", "explanation", "case", "positions"}

LINK_TEXT_BAD = {"here", "this", "link", "this link", "click here", "more", "read more", "source", "page", "article", "site", "website"}
VAGUE_HEADINGS = {"overview", "introduction", "intro", "background", "summary", "conclusion", "conclusions", "details",
                  "context", "basics", "notes", "other", "miscellaneous", "definitions", "definition", "terminology", "general"}
CITATION_FIELDS = {"by", "part"}
META_FIELDS = {"link", "date", "checked", "time", "access", "type", "vendor"}


# ---------------------------------------------------------------- the rules the settings shape

class Shaped:
    """Patterns built from the settings and the guide's own files, once per run."""

    def __init__(self, S):
        self.S = S
        self.spelling = []
        pairs = WORD_PAIRS + [(r"(?:%s)is%s" % ("|".join(IZE_STEMS), ENDINGS), r"(?:%s)iz%s" % ("|".join(IZE_STEMS), ENDINGS),
                               "-ise", "-ize"),
                              (r"(?:analys|paralys|catalys)(?:e|es|ed|ing|er|ers)", r"(?:analyz|paralyz|catalyz)(?:e|es|ed|ing|er|ers)",
                               "-yse", "-yze")]
        if S.spelling in ("british", "american"):
            for brit, amer, bhint, ahint in pairs:
                wrong, hint = (amer, bhint) if S.spelling == "british" else (brit, ahint)
                self.spelling.append((re.compile(r"\b(?:%s)\b" % wrong, re.I), hint))

        self.bans, self.senses = [], []
        for b in S.lint["ban"]:
            self.bans.append(self._entry(b))
        for b in S.lint["sense"]:
            self.senses.append(self._entry(b))
        if S.glossary["bans"]:
            for word, sense, use, homes in G.bans(G.parse(S)):
                stem = re.escape(word).replace(r"\ ", "[- ]").replace(r"\-", "[- ]?")
                tail = r"(?:s|es)?" if word[-1:].isalpha() else ""
                entry = {"regex": re.compile(r"\b%s%s\b" % (stem, tail), re.I), "hint": "Use '%s'." % use,
                         "topics": set(homes), "near": None, "unless_near": None}
                (self.senses if sense else self.bans).append(entry)

        self.case_re = None
        if S.case["terms"]:
            alts = []
            for t in S.case["terms"]:
                alts.append(t[3:] if t.startswith("re:") else r"\b%s\b" % re.escape(t))
            self.case_re = re.compile("|".join("(?:%s)" % a for a in alts))
        self.reader_re = re.compile(r"\b%s\b" % re.escape(S.reader)) if S.reader else None
        words = S.lint["meta_words"]
        self.meta_re = re.compile(r"\b(?:%s)\b" % "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True)), re.I) if words else None
        self.abbr = [(re.compile(r"\b%ss?\b" % re.escape(k)), re.compile(r"\b%ss?\b" % re.escape(v), re.I), k, v)
                     for k, v in S.lint["abbreviations"].items()]
        self.proper = set(S.lint["proper_nouns"])
        self.pointer_re = re.compile(r"\[\[%s[^\]]*\]\][^.]{0,60}\b(?:home|explains?|describes?|covers?|defines?|sets? out|lists?)\b"
                                     r"|\b(?:home|explains?|describes?|covers?|defines?|see)\b[^.]{0,40}\[\[%s"
                                     % (S.topic_id_pattern, S.topic_id_pattern))
        self.oq_link_re = re.compile(r"\[\[%s" % S.question_id_pattern)
        self.oq_heading_re = re.compile(r"%s\b" % S.question_id_pattern)
        self.never, problems = [], []
        path = S.file("never_publish")
        if path.exists():
            self.never, problems = TERMS.parse_markdown_list(path.read_text(encoding="utf-8"))
        for p in problems:
            print("lint: %s: %s" % (S.paths["never_publish"], p), file=sys.stderr)

    def _entry(self, b):
        flags = 0 if b.get("match_case") else re.I
        return {"regex": re.compile(b["pattern"], flags), "hint": b.get("hint", ""),
                "topics": set(b.get("topics", [])),
                "near": re.compile(b["near"], flags) if b.get("near") else None,
                "unless_near": re.compile(b["unless_near"], flags) if b.get("unless_near") else None}


# ---------------------------------------------------------------- text helpers

def blank(s):
    """Replace every character but newlines with a space. Keeps columns and lines."""
    return re.sub(r"[^\n]", " ", s)


def strip_comments(raw):
    """Blank HTML comments, and collect lint-ignore directives by line."""
    ignores = {}

    def repl(m):
        first = raw.count("\n", 0, m.start()) + 1
        last = raw.count("\n", 0, m.end()) + 1
        im = IGNORE_RE.match(m.group(1))
        if im:
            rules = {r.strip() for r in (im.group("rules") or "*").split(",") if r.strip()}
            for ln in {first, last}:
                ignores.setdefault(ln, set()).update(rules)
        return blank(m.group(0))

    return COMMENT_RE.sub(repl, raw), ignores


def views(text, S):
    """Return (base, prose). base hides code, tags, links and URLs. prose also hides quotes."""
    t = INLINE_CODE_RE.sub(lambda m: blank(m.group(0)), text)
    t = S.tag_re.sub(lambda m: blank(m.group(0)), t)

    def ref_repl(m):
        shown = m.group("text") or ""
        return " " * (len(m.group(0)) - len(shown) - 2) + shown + "  "

    t = S.ref_re.sub(ref_repl, t)
    t = MDLINK_RE.sub(lambda m: " " + m.group(1) + " " + blank("(" + m.group(2) + ")"), t)
    t = URL_RE.sub(lambda m: blank(m.group(0)), t)
    base = t.replace("*", " ")
    prose = QUOTE_RE.sub(lambda m: blank(m.group(0)), base)
    return base, prose


def sentence_around(text, idx):
    """The sentence that holds position idx, cut at full stops, question marks and blank lines."""
    a = max(text.rfind(c, 0, idx) for c in ".!?\n") + 1
    ends = [e for e in (text.find(c, idx) for c in ".!?\n") if e >= 0]
    return text[a:min(ends) if ends else len(text)]


def starts_sentence(text, idx):
    j = idx - 1
    while j >= 0 and text[j] in " \t\n*_([\"'“‘":
        j -= 1
    return j < 0 or text[j] in ".!?:;|#>"


def proper_noun(text, m):
    """A capitalised word in mid-sentence is a name: 'Field Guide'."""
    return m.group(0)[:1].isupper() and not starts_sentence(text, m.start())


def split_sentences(base):
    """Yield (start index, text) for each sentence of a masked paragraph."""
    t = ABBR_RE.sub(lambda m: m.group(0).replace(".", "\x00"), base)
    start = 0
    for m in SENT_SPLIT_RE.finditer(t):
        end = m.start() + 1
        yield start, t[start:end]
        start = m.end()
    yield start, t[start:]


def count_words(s):
    return len(WORD_RE.findall(s))


# ---------------------------------------------------------------- scanning

@dataclass
class Unit:
    """A paragraph, list item, table, heading, field or label, with its context."""
    kind: str
    line: int
    lines: list
    part: object
    h2: object
    private: bool
    priv: object = None
    field: str = ""
    level: int = 0
    mat: object = None
    vis: bool = False
    exempt: bool = False
    oq: bool = False  # under a "### OQ-01" heading: the open question is itself the tag

    @property
    def text(self):
        return "\n".join(self.lines)


def part_key(title, S):
    low = title.lower().strip()
    if low in S.halves():
        return "explanation"
    for key, heading, _ in S.part_list():
        if low == heading:
            return key
    return None


def read_header(lines):
    """Return (last header line number, header dict, title Unit or None)."""
    if not lines or lines[0].strip() != "---":
        return 0, {}, None
    header, title_unit = {}, None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1, header, title_unit
        if ":" in lines[i]:
            key, value = lines[i].split(":", 1)
            key = T.norm_key(key)
            header[key] = value.strip()
            if key == "title" and value.strip():
                title_unit = Unit("heading", i + 1, [" " * (lines[i].index(":") + 1) + value], "header", None, False, level=0)
    return len(lines), header, title_unit


def scan(lines, header_end, title_unit, S, shaped):
    """Split the body into units, tracking parts, sections, private blocks and visuals."""
    units, privs = [], []
    if title_unit:
        units.append(title_unit)
    part = h2 = mat = cur_priv = visual = cur = None
    in_oq = in_code = False
    stack = []

    def snap(kind, n, text, **kw):
        return Unit(kind, n, [text], part, h2, cur_priv is not None, priv=cur_priv, mat=mat, vis=(visual == "caption"), oq=in_oq, **kw)

    def flush():
        nonlocal cur
        if cur is not None:
            units.append(cur)
            cur = None

    for n in range(header_end + 1, len(lines) + 1):
        line = lines[n - 1]
        s = line.strip()
        if in_code:
            if s.startswith("```"):
                in_code = False
            continue
        if s.startswith("```"):
            flush()
            in_code = True
            continue
        mo = T.FENCE_OPEN_RE.match(line)
        if mo and not T.FENCE_CLOSE_RE.match(line):
            flush()
            name, arg = mo.group("name"), mo.group("arg")
            stack.append(name)
            if name == "private":
                privs.append({"line": n, "label": arg, "tags": 0})
                cur_priv = len(privs) - 1
                if arg:
                    units.append(Unit("label", n, [" " * line.index(arg) + arg], part, h2, True, priv=cur_priv, mat=mat))
            elif name == "visual":
                visual = "fields"
            continue
        if T.FENCE_CLOSE_RE.match(line):
            flush()
            if stack:
                closed = stack.pop()
                if closed == "private":
                    cur_priv = None
                elif closed == "visual":
                    visual = None
            continue
        if not s or (len(s) >= 3 and not s.strip("-")):
            flush()
            if visual == "fields":
                visual = "caption"
            continue
        if visual == "fields":
            if VFIELD_RE.match(s):
                flush()
                off = line.index(":") + 1
                units.append(snap("vfield", n, " " * off + line[off:], field=s.split(":", 1)[0]))
                continue
            visual = "caption"
        hm = HEADING_RE.match(line)
        if hm:
            flush()
            level, title = len(hm.group(1)), hm.group(2)
            if level <= 3:
                in_oq = level == 3 and bool(shaped.oq_heading_re.match(title))
            if level == 1:
                part, h2, mat = part_key(title, S), None, None
            elif level == 2:
                h2 = RANK_TAIL_RE.sub("", title).strip().lower()
                if part == "materials":
                    mat = (mat + 1) if mat is not None else 0
            text = " " * line.index(title) + RANK_TAIL_RE.sub("", title) if title else line
            units.append(snap("heading", n, text, level=level))
            continue
        if s.startswith("|"):
            row = re.sub(r"[-:|]", " ", line) if TABLE_SEP_RE.match(line) else line
            if cur is not None and cur.kind == "table":
                cur.lines.append(row)
            else:
                flush()
                cur = snap("table", n, row)
            continue
        if s.startswith(">"):
            if cur is not None and cur.kind == "quote":
                cur.lines.append(line)
            else:
                flush()
                cur = snap("quote", n, line, exempt=True)
            continue
        if part == "materials" and h2 is not None:
            fm = FIELD_LINE_RE.match(line)
            if fm:
                flush()
                cur = snap("field", n, " " * fm.end() + line[fm.end():], field=T.norm_key(fm.group(1)))
                continue
            if cur is not None and cur.kind == "field" and line.startswith("  "):
                cur.lines.append(line)
                continue
        lm = LIST_RE.match(line)
        if lm:
            flush()
            cur = snap("item", n, " " * lm.end() + line[lm.end():])
            continue
        if cur is not None and cur.kind in ("paragraph", "item", "field"):
            cur.lines.append(line)
        else:
            flush()
            cur = snap("paragraph", n, line)
    flush()
    return units, privs


def unit_mode(u):
    """prose: every check. citation: a title or name, dashes only. meta: not prose."""
    if u.part == "materials":
        if u.kind == "heading" and u.level == 2:
            return "citation"
        if u.kind == "field":
            if u.field in META_FIELDS:
                return "meta"
            if u.field in CITATION_FIELDS:
                return "citation"
    if u.kind == "vfield" and u.field == "credit":
        return "citation"
    return "prose"


# ---------------------------------------------------------------- findings

class Findings:
    def __init__(self, lines, ignores):
        self.lines, self.ignores = lines, ignores
        self.items, self.suppressed, self._seen = [], 0, set()

    def _ignored(self, rule, line):
        for ln in (line, line - 1):
            rules = self.ignores.get(ln)
            if rules and ("*" in rules or rule in rules):
                return True
        return False

    def add(self, rule, line, col, message, severity=None):
        key = (rule, line, col, message)
        if key in self._seen:
            return
        self._seen.add(key)
        if self._ignored(rule, line):
            self.suppressed += 1
            return
        src = self.lines[line - 1] if 0 < line <= len(self.lines) else ""
        self.items.append({"rule": rule, "severity": severity or RULES[rule][0], "line": line, "col": col,
                           "message": message, "excerpt": excerpt(src, col)})


def excerpt(src, col, width=100):
    if not col:
        return ""   # a finding about the whole topic has no place in the text
    s = src.rstrip()
    start = max(0, col - 1 - 40) if len(s) > width and col else 0
    out = s[start:start + width].strip()
    return ("..." if start else "") + out + ("..." if start + width < len(s) else "")


def where(u, idx):
    """Line and column of index idx in a unit's text."""
    text = u.text
    return u.line + text.count("\n", 0, idx), idx - (text.rfind("\n", 0, idx) + 1) + 1


# ---------------------------------------------------------------- the checks

class Linter:
    def __init__(self, path, standalone, args, S, shaped):
        self.path, self.standalone, self.args, self.S, self.X = path, standalone, args, S, shaped
        raw = path.read_text(encoding="utf-8")
        text, ignores = strip_comments(raw)
        self.lines = text.split("\n")
        header_end, self.header, title_unit = read_header(self.lines)
        self.units, self.privs = scan(self.lines, header_end, title_unit, S, shaped)
        self.F = Findings(self.lines, ignores)
        self.why_sentences, self.why_line = 0, None
        self.over_aim = 0
        self.abbr_seen = {}

    def run(self):
        for u in self.units:
            self.unit(u)
        self.doc_checks()
        return self.F

    def unit(self, u):
        text = u.text
        if u.priv is not None:
            self.privs[u.priv]["tags"] += len(self.S.tag_re.findall(text))
        self.raw_checks(u, text)
        mode = unit_mode(u)
        if mode == "meta":
            return
        base, prose = views(text, self.S)
        if u.kind == "quote":
            self.privacy(u, base)
            return
        if mode == "citation":
            self.dashes(u, prose, severity=W)
            return
        self.dashes(u, prose)
        self.quotes(u, prose)
        self.words(u, prose)
        self.privacy(u, base)
        self.sentences(u, base)
        if u.kind == "heading":
            self.headings(u, prose)
        if u.kind in ("paragraph", "item"):
            self.case_claims(u, prose)
        if u.kind == "label":
            self.private_label(u)

    # ---- raw-text checks: tags, placeholders, links, emoji, the never-publish list

    def raw_checks(self, u, text):
        F, S = self.F, self.S
        nocode = INLINE_CODE_RE.sub(lambda m: blank(m.group(0)), text)
        for m in PLACEHOLDER_RE.finditer(nocode):
            line, col = where(u, m.start())
            F.add("placeholder", line, col, "Placeholder text '%s'." % m.group(0))
        if not S.lint["allow_example_links"]:
            for m in EXAMPLE_LINK_RE.finditer(text):
                line, col = where(u, m.start())
                F.add("example-link", line, col, "Link to an example domain. Use the real address.")
        for m in EMOJI_RE.finditer(text):
            line, col = where(u, m.start())
            F.add("emoji", line, col, "Emoji. The guide uses none.")
        for t, m in TERMS.find(self.X.never, text):
            line, col = where(u, m.start())
            F.add("never-publish", line, col, "Matches '%s' on the never-publish list. It never enters a topic." % t.raw)
        for m in S.tag_candidate_re.finditer(nocode):
            nxt = nocode[m.end():m.end() + 1]
            inner = m.group(0)[1:-1]
            if nxt == "(" and not S.tag_re.fullmatch(m.group(0)):
                continue   # Markdown link text, not a tag
            tm = S.tag_re.match(nocode, m.start())
            if not tm or not tm.group(0).startswith(m.group(0)):
                line, col = where(u, m.start())
                forms = ", ".join("[%s]" % t.form for t in S.tags)
                F.add("bad-tag", line, col, "'[%s]' is not a provenance tag the settings define. The forms are: %s." % (inner, forms))
        if unit_mode(u) == "meta" and u.field != "link":
            return
        for m in MDLINK_RE.finditer(nocode):
            line, col = where(u, m.start())
            label, target = m.group(1).strip(), m.group(2).strip()
            if not target:
                F.add("link-empty", line, col, "Link '%s' has no target." % label)
                continue
            if label.lower() in LINK_TEXT_BAD:
                F.add("link-text", line, col, "Link text '%s' says nothing. Name what the link leads to." % label)
            if not re.match(r"https://", target):
                F.add("link-target", line, col, "Link target '%s' isn't https. Link topics with [[ID]]." % target[:40])
            if TRACKING_RE.search(target):
                F.add("link-tracking", line, col, "Tracking parameter in the link. Use the stable address.")
        stripped = MDLINK_RE.sub(lambda m: blank(m.group(0)), S.tag_re.sub(lambda m: blank(m.group(0)), nocode))
        if u.field != "link":
            for m in URL_RE.finditer(stripped):
                line, col = where(u, m.start())
                F.add("bare-url", line, col, "Bare URL. Write [link text](%s...)." % m.group(0)[:30])
        if u.field == "link" and TRACKING_RE.search(text):
            m = TRACKING_RE.search(text)
            line, col = where(u, m.start())
            F.add("link-tracking", line, col, "Tracking parameter in the link. Use the stable address.")

    # ---- dashes

    def dashes(self, u, prose, severity=None):
        F = self.F
        for m in DASH_RE.finditer(prose):
            line, col = where(u, m.start())
            what = "double hyphen" if m.group(0).startswith("-") else "em or en dash"
            F.add("dash", line, col, "%s. Use a full stop, comma, colon or parentheses." % what.capitalize(), severity=severity)
        if u.kind == "table":
            return
        for m in SPACED_HYPHEN_RE.finditer(prose):
            line, col = where(u, m.start() + 1)
            F.add("dash-spaced", line, col, "Spaced hyphen reads as a dash. Use a comma, colon or full stop.")
        for m in RANGE_RE.finditer(prose):
            if ISO_DATE_RE.match(prose, m.start()) or re.match(r"\d{4}-\d{2}\b", m.group(0)):
                continue
            line, col = where(u, m.start())
            F.add("range-hyphen", line, col, "Write the range '%s' with 'to'." % re.sub(r"\s?-\s?", " to ", m.group(0)))

    # ---- quotes

    def quotes(self, u, prose):
        """After pairing, a quotation mark that remains is stray. Text near it is not exempt."""
        for m in STRAY_QUOTE_RE.finditer(prose):
            line, col = where(u, m.start())
            self.F.add("quote-unbalanced", line, col, "Quotation mark with no partner. Quoted text is exempt from the prose rules only when the marks pair up.")

    # ---- words

    def words(self, u, prose):
        F, S, X = self.F, self.S, self.X
        text = prose
        # A topic link's own words are a title or a label, not prose. The glossary rules skip link
        # labels and the bold terms a topic defines. Quoted text is already blank in the prose view.
        skip = [m.span() for m in TOPIC_LINK_RE.finditer(u.text)] + [m.span() for m in BOLD_RE.finditer(u.text)]
        gtext = text
        if len(u.text) == len(text):
            chars = list(text)
            for a, b in skip:
                for i in range(a, b):
                    if chars[i] != "\n":
                        chars[i] = " "
            gtext = "".join(chars)

        def hits(regex, rule, fmt, guard=None, text=text):
            for m in regex.finditer(text):
                if guard and guard(m):
                    continue
                line, col = where(u, m.start())
                F.add(rule, line, col, fmt % m.group(0))

        hits(FIRST_PERSON_RE, "first-person", "First person '%s'. The guide has no 'we' or 'I'. Say 'this guide', or name who acts.")
        hits(FIRST_PERSON_SOFT_RE, "first-person-soft", "'%s' in guide text. The reader is 'you'.")
        hits(SIMPLE_RE, "simple-easy-quick", "'%s'. Never call anything simple, easy or quick.", guard=lambda m: proper_noun(text, m))
        hits(SHOULD_RE, "bare-should", "'%s' is ambiguous. Write 'must', 'can', 'might' or 'a good default is'.")
        hits(FILLER_RE, "filler", "Filler adverb '%s'. Cut it.")
        hits(INFLATED_RE, "inflated", "Inflated word '%s'. Use a plain one.")
        hits(SLOP_RE, "slop-phrase", "Stock phrase '%s'. Say the point.")
        hits(CONTRAST_RE, "contrast-frame", "Contrast frame ('%s'). State what it is.")
        if X.meta_re:
            hits(X.meta_re, "meta-leak", "'%s' is process language. Topic text speaks to the reader about the subject.")
        if X.reader_re:
            hits(X.reader_re, "reader-name", "'%s'. Guide text says 'you'.")
        topic_id = self.header.get("id")
        for b in X.bans:
            hits(b["regex"], "glossary-ban", "'%s' is banned by the glossary. " + b["hint"].replace("%", "%%"), text=gtext)
        for b in X.senses:
            if topic_id in b["topics"]:
                continue
            guard = None
            if b["near"]:
                guard = lambda m, rx=b["near"]: not rx.search(sentence_around(gtext, m.start()))
            elif b["unless_near"]:
                guard = lambda m, rx=b["unless_near"]: bool(rx.search(sentence_around(gtext, m.start())))
            hits(b["regex"], "glossary-sense", "'%s': " + b["hint"].replace("%", "%%"), guard=guard, text=gtext)
        for rx, hint in X.spelling:
            for m in rx.finditer(text):
                if proper_noun(text, m) or m.group(0).lower() in {p.lower() for p in X.proper}:
                    continue
                line, col = where(u, m.start())
                F.add("spelling", line, col, "'%s': this guide spells it the %s way (%s)." % (m.group(0), S.spelling.capitalize(), hint))
        for m in ISO_DATE_RE.finditer(text):
            line, col = where(u, m.start())
            F.add("date-format", line, col, "Date '%s' in prose. Write '4 October 2026'." % m.group(0))
        for m in US_DATE_RE.finditer(text):
            line, col = where(u, m.start())
            F.add("date-format", line, col, "Date '%s'. Write '4 October 2026'." % m.group(0))
        for short_re, long_re, short, _ in X.abbr:
            seen = self.abbr_seen.setdefault(short, [None, None])
            m = short_re.search(text)
            if m and seen[0] is None:
                seen[0] = where(u, m.start())
            m = long_re.search(text)
            if m and seen[1] is None:
                seen[1] = where(u, m.start())

    # ---- sentences and paragraphs

    def sentences(self, u, base):
        if u.kind in ("heading", "table", "label") or (u.kind == "vfield" and u.field != "alt"):
            return
        if u.part == "materials" and u.kind == "field" and u.field not in ("what you get", "passed over", "steps"):
            return
        F, S = self.F, self.S
        action = u.h2 == S.case["first"].lower()
        limit = S.limits["sentence_words_action"] if action else self.args.long or S.limits["sentence_words"]
        sents = [(s, t) for s, t in split_sentences(base) if count_words(t) > 0]
        for start, sent in sents:
            n = count_words(sent)
            if AIM_SENTENCE < n <= limit:
                self.over_aim += 1
            if n > limit:
                lead = len(sent) - len(sent.lstrip())
                line, col = where(u, start + lead)
                F.add("sentence-long", line, col, "Sentence of %d words. The standard aims under %d." % (n, AIM_ACTION_SENTENCE if action else AIM_SENTENCE))
        if u.kind in ("paragraph", "item") and not u.vis and len(sents) > S.limits["paragraph_sentences"]:
            F.add("paragraph-long", u.line, 1, "%d sentences in one paragraph. The limit is %d." % (len(sents), S.limits["paragraph_sentences"]))
        if u.part == "why" and not u.private and u.kind in ("paragraph", "item"):
            self.why_sentences += len(sents)
            if self.why_line is None:
                self.why_line = u.line
        if u.part == "materials" and u.kind == "field":
            if u.field in ("what you get", "passed over") and len(sents) > 2:
                F.add("material-length", u.line, 1, "'%s' runs %d sentences. The standard allows 2." % (u.field, len(sents)))

    # ---- headings

    def headings(self, u, prose):
        if u.level in (0, 1) or u.part == "materials":
            return
        F = self.F
        title = prose.strip()
        tokens = re.findall(r"[A-Za-z][A-Za-z'’-]*", title)
        caps = [t for t in tokens[1:] if t[0].isupper() and not t.isupper() and len(t) > 3 and t not in self.X.proper]
        if len(caps) >= 3:
            F.add("heading-case", u.line, 1, "Heading in Title Case ('%s'). Use sentence case." % title[:60])
        if u.part in ("explanation", "positions") and u.level in (2, 3):
            if title.lower().strip(" .:") in VAGUE_HEADINGS or (u.level == 2 and u.part == "explanation" and len(tokens) <= 2):
                F.add("heading-vague", u.line, 1, "Heading '%s' says nothing. Say the point the section makes." % title[:60])

    # ---- claims about the case

    def case_claims(self, u, prose):
        """A paragraph or list item that names the case needs a provenance tag, or a link to an open question."""
        S, X = self.S, self.X
        if X.case_re is None or not (self.standalone or u.part in CASE_PARTS):
            return
        if u.h2 in (S.case["first"].lower(), S.case["unknown"].lower()) or u.exempt or u.oq:
            return
        if u.text.lstrip().lower().startswith("**%s.**" % S.position_fields[2].lower()):
            return
        text = u.text
        tags = [m.group("tag") for m in S.tag_re.finditer(text)]
        has_tag = bool(tags)
        has_oq = bool(X.oq_link_re.search(text))
        has_soft = any(S.tag_kind(t) in SOFT_TAG_KINDS for t in tags)
        for start, sent in split_sentences(prose):
            m = X.case_re.search(sent)
            lead = start
            while lead > 0 and text[lead - 1] == "*":   # the sentence splitter blanked the bold marks
                lead -= 1
            raw = text[lead:start + len(sent)]
            if not m or NO_CLAIM_RE.search(sent) or X.pointer_re.search(raw) or DEFINITION_RE.match(raw):
                continue
            if not has_tag and not has_oq:
                line, col = where(u, start + m.start())
                self.F.add("case-untagged", line, col, "Names '%s', and the paragraph carries no provenance tag. Tag every fact about the case, or link the open question." % m.group(0))
                return
            hm = HEDGE_RE.search(sent)
            if hm and not (has_soft or has_oq):
                line, col = where(u, start + hm.start())
                self.F.add("case-guess", line, col, "A hedged claim about the case ('%s'). Mark it [inference] or [unverified], or link the open question." % hm.group(0))

    # ---- privacy

    def privacy(self, u, base):
        F, S = self.F, self.S
        if S.source_words_re and not u.private and u.kind != "quote":
            for start, sent in split_sentences(base):
                m = S.source_words_re.search(sent)
                if m:
                    line, col = where(u, start + m.start())
                    F.add("private-source", line, col, "'%s' outside a private block. A fact from a private source belongs in ':::private'." % m.group(0))

    def private_label(self, u):
        label = u.text.strip()
        if len(label.split()) > 12 or re.search(r"\d|\"|“", label):
            self.F.add("private-label", u.line, 1, "Private label '%s'. It shows while closed: name the subject, never the fact." % label[:50])

    # ---- whole-document checks

    def doc_checks(self):
        F, S = self.F, self.S
        lo, hi = S.limits["why_sentences"]
        if self.why_line is not None and not lo <= self.why_sentences <= hi:
            F.add("why-length", self.why_line, 1, "'%s' has %d public sentences. The standard asks for %d to %d."
                  % (S.parts["why"], self.why_sentences, lo, hi))
        for short, (first_short, first_long) in self.abbr_seen.items():
            if first_short and (not first_long or first_short < first_long):
                F.add("abbreviation", first_short[0], first_short[1], "'%s' before '%s' is spelled out. Spell it out at first use."
                      % (short, S.lint["abbreviations"][short]))
        for p in self.privs:
            if p["tags"] == 0:
                F.add("private-no-tag", p["line"], 1, "A private block with no provenance tag. Each private fact carries its tag.")


# ---------------------------------------------------------------- topic-level checks

def topic_checks(lint, parsed, tmap, args):
    """Checks that need the parsed structure: size, materials, the header against the map."""
    F, h, S = lint.F, lint.header, lint.S
    own = {"size", "materials-ceiling"}
    if not args.no_structure:
        for kind, sev in (("errors", E), ("warnings", W)):
            for f in parsed.get(kind, []):
                if f.get("code") in own:
                    continue   # reported below, by this script
                F.add("structure", f.get("line") or 1, 1 if (f.get("line") or 0) > 1 else 0, f["message"], severity=sev)
    mats = parsed.get("materials", [])
    if len(mats) > S.materials["per_topic"]:
        F.add("materials-ceiling", 1, 0, "%d materials. The ceiling is %d (materials.per_topic)." % (len(mats), S.materials["per_topic"]))
    words, size = parsed.get("words", 0), h.get("size")
    if size in S.sizes:
        lo, hi = S.sizes[size]
        if words > S.split_above:
            F.add("size", 1, 0, "%d words. A topic over %s words is two topics: propose the split." % (words, format(S.split_above, ",")), severity=E)
        elif not lo <= words <= hi:
            F.add("size", 1, 0, "%d words is outside size %s (%d to %d)." % (words, size, lo, hi))
    tier = S.tier_by_id.get(h.get("tier", ""))
    cm = re.match(r"(\d{4})-(\d{2})", h.get("checked", ""))
    seen_links = {}
    for m in mats:
        f, line = m["fields"], m["line"]
        link = f.get("link", "")
        if link:
            if link in seen_links:
                F.add("material-duplicate", line, 1, "The same link as the material at line %d." % seen_links[link])
            seen_links[link] = line
        if f.get("type") == "exercise" and S.materials["exercises_free"] and f.get("access", "free") != "free":
            F.add("material-exercise", line, 1, "An exercise runs with free tools. Its access is '%s'." % f.get("access"))
        if tier is not None and tier.fast and f.get("date"):
            dm = re.match(r"^(\d{4})(?:-(\d{2}))?", f["date"])
            if dm:
                if not dm.group(2) and f.get("type") != "book":
                    F.add("material-date", line, 1, "In this tier, a material carries a year and a month (2026-09). This one has '%s'." % f["date"])
                if cm:
                    age = (int(cm.group(1)) * 12 + int(cm.group(2))) - (int(dm.group(1)) * 12 + int(dm.group(2) or 12))
                    if age > S.materials["max_age_months"] and not AGE_REASON_RE.search(f.get("what you get", "")):
                        F.add("material-old", line, 1, "Dated %s, %d months before the check date. Say in 'what you get' why it is still the one to read."
                              % (f["date"], age))
    tid = h.get("id")
    want = tmap["topics"].get(tid)
    if want:
        if h.get("title") and h["title"] != want["title"]:
            F.add("map-mismatch", 1, 0, "Title differs from the topic map: '%s'." % want["title"])
        for key in ("rank", "size", "cluster"):
            if want.get(key) and h.get(key) and h[key] != want[key]:
                F.add("map-mismatch", 1, 0, "%s is '%s'. The topic map says '%s'." % (key, h[key], want[key]))
    return mats


# ---------------------------------------------------------------- running

def find_targets(paths):
    """Yield (path to a topic file or page, standalone flag)."""
    for p in paths:
        p = Path(p)
        if p.is_file():
            yield p, p.name != T.TOPIC_FILE
        elif (p / T.TOPIC_FILE).is_file():
            yield p / T.TOPIC_FILE, False
        elif p.is_dir():
            for f in sorted(p.rglob(T.TOPIC_FILE)):
                yield f, False
        else:
            print("lint: %s is not a file or folder" % p, file=sys.stderr)
            raise SystemExit(2)


def lint_one(path, standalone, tmap, args, S, shaped, ids):
    lint = Linter(path, standalone, args, S, shaped)
    F = lint.run()
    result = {"path": path, "standalone": standalone, "id": lint.header.get("id", "?"), "words": 0, "critical": 0,
              "cluster": lint.header.get("cluster"), "size": lint.header.get("size")}
    if not standalone:
        parsed = T.parse_topic(path.parent, S, ids)
        result["words"] = parsed.get("words", 0)
        mats = topic_checks(lint, parsed, tmap, args)
        result["critical"] = sum(1 for m in mats if m.get("rank") == "critical")
    result["findings"] = F.items
    result["over_aim"] = lint.over_aim
    result["suppressed"] = F.suppressed
    return result


def cross_checks(results, quotas, S):
    """Findings about several topics together. Reported once, for all topics."""
    out = []
    ids = {}
    for r in results:
        if r["id"] != "?":
            ids.setdefault(r["id"], []).append(r["path"])
    for tid, paths in sorted(ids.items()):
        if len(paths) > 1:
            out.append(("duplicate-id", "Topic ID %s appears in %d folders." % (tid, len(paths))))
    total = sum(r["critical"] for r in results)
    if total > S.materials["critical_in_guide"]:
        out.append(("critical-total", "%d critical materials. The guide allows %d (materials.critical_in_guide)." % (total, S.materials["critical_in_guide"])))
    by_cluster = {}
    for r in results:
        if r["cluster"]:
            by_cluster[r["cluster"]] = by_cluster.get(r["cluster"], 0) + r["critical"]
    for cl, n in sorted(by_cluster.items()):
        if cl in quotas and n > quotas[cl]:
            out.append(("critical-cluster", "Cluster %s has %d critical materials. Its quota is %d." % (cl, n, quotas[cl])))
    xl = [r["id"] for r in results if r.get("size") == "XL"]
    if len(xl) > S.xl_allowed:
        out.append(("xl-total", "%d XL topics (%s). The guide allows %d (sizes.xl_allowed)." % (len(xl), ", ".join(xl), S.xl_allowed)))
    return [{"rule": rule, "severity": RULES[rule][0], "message": msg} for rule, msg in out]


def show(path):
    try:
        return str(Path(path).resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def main(argv):
    ap = argparse.ArgumentParser(description="Lint the writing of a guide's topics.")
    ap.add_argument("paths", nargs="*", help="topic folders, topic.md files, folders to search, or other .md files (default: the content folder)")
    ap.add_argument("--guide", help="the guide's settings file (default: guide.toml)")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    ap.add_argument("--errors-only", "-q", action="store_true", help="print errors only")
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    ap.add_argument("--rules", action="store_true", help="list the rules and exit")
    ap.add_argument("--only", help="comma-separated rule IDs to report")
    ap.add_argument("--skip", help="comma-separated rule IDs to leave out")
    ap.add_argument("--long", type=int, default=0, help="sentence length that raises 'sentence-long' (default: limits.sentence_words)")
    ap.add_argument("--no-structure", action="store_true", help="leave out findings carried over from the format check")
    args = ap.parse_args(argv)

    if args.rules:
        for sev in (E, W):
            print("%s:" % sev)
            for rid, (s, desc) in RULES.items():
                if s == sev:
                    print("  %-20s %s" % (rid, desc))
        return 0
    unknown = [r for r in (args.only or "").split(",") + (args.skip or "").split(",") if r and r not in RULES]
    if unknown:
        print("lint: unknown rule %s. Run with --rules." % ", ".join(unknown), file=sys.stderr)
        return 2
    try:
        S = load(find_settings(["--guide", args.guide] if args.guide else []))
    except SettingsError as exc:
        print("lint: %s" % exc, file=sys.stderr)
        return 2

    paths = args.paths or [str(S.content)]
    targets = list(find_targets(paths))
    if not targets:
        print("No topics found under %s." % ", ".join(paths))
        return 0 if not args.paths else 2

    shaped = Shaped(S)
    tmap = topicmap.parse_topic_map(S)
    ids = T.known_ids(S)
    results = [lint_one(p, standalone, tmap, args, S, shaped, ids) for p, standalone in targets]
    only = set(filter(None, (args.only or "").split(",")))
    skip = set(filter(None, (args.skip or "").split(",")))
    hidden = 0
    for r in results:
        kept = [f for f in r["findings"] if (not only or f["rule"] in only) and f["rule"] not in skip]
        r["findings"] = [f for f in kept if not (args.errors_only and f["severity"] != E)]
        r["findings"].sort(key=lambda f: (f["line"], f["col"]))
        hidden += len(kept) - len(r["findings"])
    cross = [c for c in cross_checks([r for r in results if not r["standalone"]], tmap["quotas"], S)
             if (not only or c["rule"] in only) and c["rule"] not in skip]

    n_err = sum(1 for r in results for f in r["findings"] if f["severity"] == E) + sum(1 for c in cross if c["severity"] == E)
    n_warn = sum(1 for r in results for f in r["findings"] if f["severity"] == W)
    n_supp = sum(r["suppressed"] for r in results)

    if args.json:
        print(json.dumps({
            "topics": [{"path": show(r["path"]), "id": r["id"], "words": r["words"], "suppressed": r["suppressed"],
                        "findings": r["findings"]} for r in results],
            "cross": cross, "errors": n_err, "warnings": n_warn, "hidden": hidden, "suppressed": n_supp}, indent=2, ensure_ascii=False))
    else:
        aim = S.limits["sentence_words"] if not args.long else args.long
        for r in results:
            print("%s  (%s%s)" % (show(r["path"]), r["id"], ", %s words" % format(r["words"], ",") if r["words"] else ""))
            if not r["findings"]:
                print("  clean")
            if r.get("over_aim") and not args.errors_only:
                print("  note: %d sentences run %d to %d words. The standard aims under %d." % (r["over_aim"], AIM_SENTENCE + 1, aim, AIM_SENTENCE))
            for f in r["findings"]:
                tag = "ERROR  " if f["severity"] == E else "warning"
                loc = "%d:%d" % (f["line"], f["col"]) if f["col"] else "topic"
                print("  %7s %s %-18s %s" % (loc, tag, f["rule"], f["message"]))
                if f["excerpt"]:
                    print("            > %s" % f["excerpt"])
        for c in cross:
            print("ALL TOPICS  %s %-18s %s" % ("ERROR  " if c["severity"] == E else "warning", c["rule"], c["message"]))
        print("\n%d file%s: %d error%s, %d warning%s%s" % (
            len(results), "" if len(results) == 1 else "s", n_err, "" if n_err == 1 else "s",
            n_warn, "" if n_warn == 1 else "s",
            ", %d silenced by lint-ignore" % n_supp if n_supp else "") + (" (%d warnings hidden by --errors-only)" % hidden if hidden else ""))
    return 1 if n_err or (args.strict and n_warn) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
