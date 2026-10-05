"""Read a guide's settings file, guide.toml, and derive what the engine needs.

Every value that changes from one guide to another lives in guide.toml, once.
This module holds the defaults, merges the file over them, checks the result,
and builds the patterns the parser, the renderer, the checks and the lint share:
topic IDs, question IDs, links and provenance tags.

guide.toml at the repository root documents every key. A guide can also live
elsewhere: pass its settings file to any command with --guide.
"""

import copy
import re
import sys
from pathlib import Path

if sys.version_info < (3, 11):
    sys.exit("The engine needs Python 3.11 or later, for tomllib. This is %d.%d. "
             "Run it with python3.11 or newer." % sys.version_info[:2])

import tomllib  # noqa: E402

ENGINE = Path(__file__).resolve().parent.parent
REPO = ENGINE.parent

RANKS = ["critical", "high", "medium", "context"]          # highest first. The file format uses these keys.
SIZE_KEYS = ["S", "M", "L", "XL"]

# ---------------------------------------------------------------- defaults
# The same values, with an explanation of each, are in guide.toml at the repository root.

DEFAULTS = {
    "guide": {
        "title": "Your guide",
        "language": "en-GB",
        "spelling": "british",
        "reader": "",
        "description": "",
    },
    "paths": {
        "root": "",
        "topic_map": "curriculum/topic-map.md",
        "glossary": "context/glossary.md",
        "open_questions": "context/open-questions.md",
        "never_publish": "context/never-publish.md",
        "content": "content",
        "home": "content/home.md",
        "questions_page": "content/questions.md",
        "out": "site",
    },
    "tiers": [
        {"id": "base", "name": "Base", "prefix": "B",
         "question": "How does it work, who does what, and why?",
         "definition": "What you need to understand the domain: how it works, who does what, and why."},
        {"id": "practical", "name": "Practical", "prefix": "P",
         "question": "What do people do to act in it, and how do they know it works?",
         "definition": "The practices, frameworks, research and measures you use to act in it."},
        {"id": "modern", "name": "Modern", "prefix": "M",
         "question": "What do today's tools and technology change?",
         "definition": "What today's tools and technology change, in the problem and in the solutions.",
         "updates": True, "fast": True},
    ],
    "case": {
        "part": "In your case",
        "known": "Known",
        "unknown": "Unknown",
        "first": "What to look at first",
        "terms": [],
    },
    "parts": {
        "why": "Why it matters for your goal",
        "short": "The short version",
        "explanation": "Explanation",
        "problem": "Explanation: the problem",
        "solutions": "Explanation: the solutions",
        "positions": "Positions",
        "materials": "Materials",
        "unverified": "Not verified",
        "check": "Check yourself",
        "consequence": "For your goal",
        "bridge": "Bridge",
        "position_fields": ["Why hold it", "The strongest case against", "What would change it"],
    },
    "sizes": {
        "words_per_minute": 220,
        "S": [800, 1500],
        "M": [1500, 2500],
        "L": [2500, 3500],
        "XL": [3500, 4500],
        "xl_allowed": 5,
    },
    "limits": {
        "short_lines": [5, 8],
        "why_sentences": [2, 4],
        "positions": 3,
        "check_questions": 5,
        "sentence_words": 35,
        "sentence_words_action": 30,
        "paragraph_sentences": 6,
    },
    "materials": {
        "per_topic": 5,
        "critical_per_topic": 1,
        "critical_per_critical_topic": 2,
        "critical_in_guide": 30,
        "max_age_months": 18,
        "exercises_free": True,
        "types": ["article", "paper", "book", "video", "talk", "podcast", "documentation",
                  "course", "repository", "tool", "exercise"],
    },
    "ranks": {
        "critical": {"label": "Critical", "topic": "You can't reach your goal without it.",
                     "material": "Read or watch it in full. It gives something the guide can't.",
                     "action": "Read in full", "reader_minutes": "full"},
        "high": {"label": "High", "topic": "Needed to follow the core of the subject.",
                 "material": "Skim it, 10 to 15 minutes.",
                 "action": "Skim, 10 to 15 min", "reader_minutes": 15},
        "medium": {"label": "Medium", "topic": "Useful background. It makes other topics easier.",
                   "material": "Skim it faster, about 5 minutes.",
                   "action": "Skim, about 5 min", "reader_minutes": 5},
        "context": {"label": "Context",
                    "topic": "Orientation and completeness. A context section is one you can skip without losing the thread.",
                    "material": "Open it when you need it.",
                    "action": "Open when needed", "reader_minutes": "optional"},
    },
    "tags": [
        {"form": "public", "title": "From a public page"},
        {"form": "source: {name}{where}", "title": "From a document in the guide's sources"},
        {"form": "private: {name}{where}", "private": True, "title": "Private. From a private source"},
        {"form": "inference", "title": "Reasoning from other facts, not a reported fact"},
        {"form": "unverified", "title": "A single weak source, or a memory. Not a fact"},
    ],
    "privacy": {
        "label": "From a private source",
        "glossary_source": "",
        "page_source": "",
        "source_words": "",
    },
    "map": {
        "read_first": "read first",
        "after": "after",
        "updates": "updates",
        "ages_fast": "facts age fast",
        "pilot": "pilot",
        "reading_order": "Reading order",
        "cluster_prefix": "C",
        "question_prefix": "OQ-",
        "question_groups": "",
    },
    "glossary": {
        "bookkeeping": ["Added"],
        "decision_prefix": "D",
        "bans": True,
    },
    "portal": {
        "accent_hue": 255,
        "storage_prefix": "",
        "footer_note": "",
        "definition_label": "Your definition of this tier",
        "questions_lead": "What this guide couldn't settle. Each question says what would settle it, so the list doubles as your list of things to find out.",
        "tier_map_pending": "A map of how these topics fit together comes later. Until then, the groups below are the map.",
    },
    "lint": {
        "allow_example_links": False,
        "meta_words": ["dossier", "dossiers", "topic worker", "topic workers", "review worker", "portal worker",
                       "context worker", "topic map", "orchestrator"],
        "proper_nouns": [],
        "abbreviations": {},
        "pay_terms": False,
        "ban": [],
        "sense": [
            {"pattern": r"\bthe guide\b", "hint": "Inside topic text, write 'this guide'."},
        ],
    },
}

TIER_KEYS = {"id", "name", "prefix", "question", "definition", "updates", "fast"}
TAG_KEYS = {"form", "private", "title"}
BAN_KEYS = {"pattern", "hint", "match_case", "topics", "near", "unless_near"}

PLACEHOLDERS = {
    "{name}": r"[a-z0-9][a-z0-9-]*",
    "{time}": r"[0-9][0-9:, to]*",
    "{section}": r"§[0-9.]+",
    "{where}": r"(?: [^\]\[\n]{1,40})?",
}


class SettingsError(Exception):
    pass


# ---------------------------------------------------------------- loading

def merge(base, over, where, problems):
    """base updated with over, table by table. A list replaces the default list."""
    out = copy.deepcopy(base)
    for key, value in over.items():
        if key not in base:
            problems.append("%s: unknown key '%s'" % (where, key))
            continue
        if isinstance(base[key], dict) and key not in ("abbreviations",):
            if not isinstance(value, dict):
                problems.append("%s.%s must be a table" % (where, key))
                continue
            # The rank tables and the case table merge key by key too.
            out[key] = merge(base[key], value, "%s.%s" % (where, key), problems)
        else:
            out[key] = value
    return out


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "guide"


def find_settings(argv):
    """The settings file named by --guide, else guide.toml at the repository root."""
    if "--guide" in argv:
        k = argv.index("--guide")
        if k + 1 >= len(argv):
            raise SettingsError("--guide needs the path of a settings file")
        return Path(argv[k + 1]).expanduser().resolve()
    return REPO / "guide.toml"


def load(path=None):
    path = Path(path or REPO / "guide.toml").expanduser().resolve()
    if not path.exists():
        raise SettingsError("No settings file at %s. A guide needs guide.toml; the set-up skill writes it." % path)
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise SettingsError("%s doesn't parse: %s" % (path, exc))
    return Settings(raw, path)


# ---------------------------------------------------------------- the settings

class Tier:
    def __init__(self, d):
        self.id = d["id"]
        self.name = d["name"]
        self.prefix = d["prefix"]
        self.question = d.get("question", "")
        self.definition = d.get("definition", "")
        self.updates = bool(d.get("updates", False))
        self.fast = bool(d.get("fast", False))


class TagSpec:
    def __init__(self, d):
        self.form = d["form"]
        self.private = bool(d.get("private", False))
        self.title = d.get("title", "")
        first = re.split(r"\{", self.form, 1)[0]
        self.kind = first.rstrip(": ").strip() or self.form
        pattern, rest = "", self.form
        while rest:
            m = re.search(r"\{[a-z]+\}", rest)
            if not m:
                pattern += re.escape(rest)
                break
            pattern += re.escape(rest[:m.start()])
            ph = m.group(0)
            if ph not in PLACEHOLDERS:
                raise SettingsError("tags: '%s' has an unknown placeholder %s" % (self.form, ph))
            pattern += PLACEHOLDERS[ph]
            rest = rest[m.end():]
        self.pattern = pattern
        self.regex = re.compile(pattern)


class Settings:
    def __init__(self, raw, path):
        problems = []
        d = merge(DEFAULTS, raw, "guide.toml", problems)
        self.raw = d
        self.path = Path(path)
        root = d["paths"]["root"]
        self.root = (self.path.parent / Path(root).expanduser()).resolve() if root else self.path.parent

        g = d["guide"]
        self.title = g["title"]
        self.language = g["language"]
        self.spelling = g["spelling"]
        self.reader = g["reader"]
        self.description = g["description"]
        if self.spelling not in ("british", "american", "none"):
            problems.append("guide.spelling must be british, american or none")

        # Tiers
        self.tiers = []
        for t in d["tiers"]:
            unknown = set(t) - TIER_KEYS
            if unknown:
                problems.append("tiers: unknown key %s" % ", ".join(sorted(unknown)))
            for key in ("id", "name", "prefix"):
                if not t.get(key):
                    problems.append("tiers: every tier needs %s" % key)
            if t.get("prefix") and not re.fullmatch(r"[A-Z]", t["prefix"]):
                problems.append("tiers: the prefix '%s' must be one capital letter" % t.get("prefix"))
            if t.get("id") and not re.fullmatch(r"[a-z][a-z0-9-]*", t["id"]):
                problems.append("tiers: the id '%s' must be lowercase letters, digits and hyphens" % t.get("id"))
        if not problems:
            self.tiers = [Tier(t) for t in d["tiers"]]
        if not self.tiers and not problems:
            problems.append("tiers: a guide needs at least one tier")
        prefixes = [t.prefix for t in self.tiers]
        if len(set(prefixes)) != len(prefixes):
            problems.append("tiers: two tiers share a prefix")
        self.tier_ids = [t.id for t in self.tiers]
        self.tier_by_id = {t.id: t for t in self.tiers}
        self.tier_by_prefix = {t.prefix: t for t in self.tiers}
        self.tier_by_name = {t.name: t for t in self.tiers}

        # IDs and links
        m = d["map"]
        self.map = m
        self.question_prefix = m["question_prefix"]
        self.cluster_prefix = m["cluster_prefix"]
        letters = "".join(prefixes) or "X"
        self.topic_id_pattern = r"[%s]\d{2}" % letters
        self.question_id_pattern = re.escape(self.question_prefix) + r"\d{2}"
        self.topic_id_re = re.compile(r"^%s$" % self.topic_id_pattern)
        self.question_id_re = re.compile(r"^%s$" % self.question_id_pattern)
        self.any_topic_id_re = re.compile(r"(?<![\w-])%s(?![\w-])" % self.topic_id_pattern)
        self.any_question_id_re = re.compile(r"(?<![\w-])%s(?!\w)" % self.question_id_pattern)
        self.ref_re = re.compile(r"\[\[(?P<id>%s|%s)(?:\|(?P<text>[^\]]+))?\]\]"
                                 % (self.topic_id_pattern, self.question_id_pattern))
        self.cluster_re = re.compile(r"^%s\d{1,2}$" % re.escape(self.cluster_prefix))
        self.folder_re = re.compile(r"^(%s)-" % self.topic_id_pattern, re.I)

        # Parts of a topic
        self.case = d["case"]
        self.parts = d["parts"]
        self.has_case = bool(self.case["part"].strip())
        self.case_blocks = [self.case["known"], self.case["unknown"], self.case["first"]]
        self.position_fields = list(self.parts["position_fields"])
        if len(self.position_fields) != 3:
            problems.append("parts.position_fields must name three fields")

        # Sizes and limits
        s = d["sizes"]
        self.wpm = s["words_per_minute"]
        self.sizes = {k: tuple(s[k]) for k in SIZE_KEYS}
        self.xl_allowed = s["xl_allowed"]
        self.split_above = self.sizes["XL"][1]
        self.limits = d["limits"]
        self.materials = d["materials"]
        self.material_types = list(self.materials["types"])
        if "exercise" not in self.material_types:
            self.material_types.append("exercise")

        # Ranks
        self.ranks = d["ranks"]
        for r in RANKS:
            for key in ("label", "topic", "material", "action", "reader_minutes"):
                if key not in self.ranks.get(r, {}):
                    problems.append("ranks.%s needs %s" % (r, key))

        # Provenance tags
        self.tags = []
        for t in d["tags"]:
            unknown = set(t) - TAG_KEYS
            if unknown:
                problems.append("tags: unknown key %s" % ", ".join(sorted(unknown)))
            try:
                self.tags.append(TagSpec(t))
            except SettingsError as exc:
                problems.append(str(exc))
            except (KeyError, re.error) as exc:
                problems.append("tags: %r" % exc)
        if self.tags:
            self.tag_re = re.compile(r"\[(?P<tag>%s)\](?:\((?P<url>[^)\s]+)\))?"
                                     % "|".join(t.pattern for t in self.tags))
        else:
            self.tag_re = re.compile(r"(?!x)x")
        self.private_kinds = tuple(t.kind for t in self.tags if t.private)
        candidates = set()
        for t in self.tags:
            word = re.split(r"[ :{]", t.kind, 1)[0]
            candidates.add(re.escape(word).replace(r"\-", "-?"))
            head = word.split("-")[0]
            if len(head) >= 4:
                candidates.add(re.escape(head))
        self.tag_candidate_re = re.compile(r"\[(?:%s)[^\]\n]*\]" % "|".join(sorted(candidates)), re.I) \
            if candidates else re.compile(r"(?!x)x")

        # Privacy
        p = d["privacy"]
        self.private_label = p["label"]
        self.glossary_source_re = self._regex(p["glossary_source"], "privacy.glossary_source", problems)
        self.page_source_re = self._regex(p["page_source"], "privacy.page_source", problems)
        self.source_words_re = self._regex(p["source_words"], "privacy.source_words", problems)

        # Glossary
        self.glossary = d["glossary"]
        dp = re.escape(self.glossary["decision_prefix"])
        # A decision reference left on a page: "(D7)", "(D7, D12)", or a bare number of two digits or more.
        self.decision_re = re.compile(r"\(\s*%s\d{1,4}(?:,\s*%s\d{1,4})*\s*\)|\b%s\d{2,4}\b" % (dp, dp, dp)) \
            if dp else None

        # Portal
        pt = d["portal"]
        self.portal = pt
        self.storage_prefix = pt["storage_prefix"] or slug(self.title)
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", self.storage_prefix):
            problems.append("portal.storage_prefix must be lowercase letters, digits and hyphens")
        if not isinstance(pt["accent_hue"], (int, float)) or not 0 <= pt["accent_hue"] <= 360:
            problems.append("portal.accent_hue must be a number from 0 to 360")

        # Lint
        self.lint = d["lint"]
        for kind in ("ban", "sense"):
            for b in self.lint[kind]:
                unknown = set(b) - BAN_KEYS
                if unknown or "pattern" not in b:
                    problems.append("lint.%s: each entry needs a pattern, and knows only %s"
                                    % (kind, ", ".join(sorted(BAN_KEYS))))
                    continue
                try:
                    re.compile(b["pattern"])
                except re.error as exc:
                    problems.append("lint.%s: '%s' doesn't compile: %s" % (kind, b["pattern"], exc))

        # Paths
        self.paths = {k: v for k, v in d["paths"].items() if k != "root"}
        if problems:
            raise SettingsError("%s has problems:\n  %s" % (self.path, "\n  ".join(problems)))

    @staticmethod
    def _regex(text, where, problems):
        if not text:
            return None
        try:
            return re.compile(text, re.I)
        except re.error as exc:
            problems.append("%s doesn't compile: %s" % (where, exc))
            return None

    # ---- paths

    def file(self, key):
        """An absolute path for a key of [paths]."""
        return (self.root / Path(self.paths[key]).expanduser()).resolve()

    @property
    def content(self):
        return self.file("content")

    def intro(self, tier_id):
        return self.content / tier_id / "intro.md"

    def out_dir(self):
        out = Path(self.paths["out"]).expanduser()
        return out if out.is_absolute() else (self.root / out).resolve()

    # ---- tags

    def tag_kind(self, tag):
        for t in self.tags:
            if t.regex.fullmatch(tag):
                return t.kind
        return tag

    def tag_spec(self, tag):
        for t in self.tags:
            if t.regex.fullmatch(tag):
                return t
        return None

    def is_private_tag(self, tag):
        spec = self.tag_spec(tag)
        return bool(spec and spec.private)

    def has_private_tag(self, text):
        """True when text cites a private source. A tag inside backticks is code, not a citation."""
        text = re.sub(r"`[^`\n]*`", " ", text)
        return any(self.is_private_tag(m.group("tag")) for m in self.tag_re.finditer(text))

    # ---- tiers and topics

    def tier_of_id(self, tid):
        t = self.tier_by_prefix.get(tid[:1])
        return t.id if t else None

    def tier_label(self, tier_id):
        t = self.tier_by_id.get(tier_id)
        return t.name if t else tier_id

    def rank_label(self, rank):
        return self.ranks.get(rank, {}).get("label", "No rank")

    def size_band(self, size):
        lo_hi = self.sizes.get(size)
        if not lo_hi:
            return ""
        text = "%s to %s words" % (format(lo_hi[0], ","), format(lo_hi[1], ","))
        return text + (", an exception" if size == "XL" else "")

    def size_midpoint(self, size):
        lo_hi = self.sizes.get(size)
        return (lo_hi[0] + lo_hi[1]) / 2 if lo_hi else 0

    def header_keys(self):
        """Header keys: (required for every topic, required in an updates tier, list-valued)."""
        return {
            "id": (True, False, False),
            "title": (True, False, False),
            "tier": (True, False, False),
            "rank": (True, False, False),
            "size": (True, False, False),
            "depth": (True, False, False),
            "cluster": (True, False, False),
            "read first": (True, False, True),
            "checked": (True, False, False),
            "updates": (False, True, True),
            "covers": (False, True, False),
            "check again": (False, False, False),
        }

    def part_list(self):
        """The parts of a topic, in order: (key, heading in lowercase, required)."""
        out = [
            ("why", self.parts["why"].lower(), True),
            ("short", self.parts["short"].lower(), True),
            ("explanation", self.parts["explanation"].lower(), True),
        ]
        if self.has_case:
            out.append(("case", self.case["part"].lower(), True))
        out += [
            ("positions", self.parts["positions"].lower(), False),
            ("materials", self.parts["materials"].lower(), True),
            ("unverified", self.parts["unverified"].lower(), True),
            ("check", self.parts["check"].lower(), False),
        ]
        return out

    def halves(self):
        return {self.parts["problem"].lower(): "problem", self.parts["solutions"].lower(): "solutions"}

    def leadins(self):
        return {self.parts["consequence"].lower(): "consequence", self.parts["bridge"].lower(): "bridge"}

    # ---- for the browser

    def js_config(self):
        return {"key": self.storage_prefix, "lang": self.language, "title": self.title,
                "tiers": [t.prefix.lower() for t in self.tiers],
                "ranks": {r: self.rank_label(r) for r in RANKS}}
