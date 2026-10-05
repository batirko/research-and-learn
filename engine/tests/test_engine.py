"""Tests for the engine, the lint and the scan. They build the test guide in
engine/tests/fixture/, then break copies of it on purpose.

    python3 -m unittest discover -s engine/tests -v

Python 3.11 or later, standard library only.
"""

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent
REPO = ENGINE.parent
FIXTURE = HERE / "fixture"
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(REPO / "tools"))

import build  # noqa: E402
import lint  # noqa: E402
import scan  # noqa: E402
from core import terms  # noqa: E402
from core.settings import SettingsError, load  # noqa: E402
from core.topicfile import parse_topic  # noqa: E402


def quiet(fn, *args):
    """Run fn, keep what it prints, and return (result, output)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        result = fn(*args)
    return result, out.getvalue()


class Copy:
    """A throwaway copy of the test guide, to break on purpose."""

    def __enter__(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / "guide"
        shutil.copytree(FIXTURE, self.root)
        return self

    def __exit__(self, *exc):
        shutil.rmtree(self.tmp)

    def path(self, rel):
        return self.root / rel

    def edit(self, rel, old, new):
        p = self.path(rel)
        text = p.read_text(encoding="utf-8")
        assert old in text, "%r is not in %s" % (old, rel)
        p.write_text(text.replace(old, new, 1), encoding="utf-8")

    def build(self):
        return quiet(build.main, ["--guide", str(self.path("guide.toml")), "--out", str(self.tmp / "site")])

    def lint(self, *paths):
        return quiet(lint.main, ["--guide", str(self.path("guide.toml"))] + [str(self.path(p)) for p in paths])


B01 = "content/base/b01-how-a-colony-works"
B01_MD = B01 + "/topic.md"


class TheTestGuide(unittest.TestCase):
    def test_builds_and_passes_every_check(self):
        with Copy() as c:
            code, out = c.build()
            self.assertEqual(code, 0, out)
            self.assertEqual(out.count("[pass]"), 9, out)
            self.assertNotIn("[FAIL]", out)
            for page in ("index.html", "base.html", "b01.html", "b02.html", "glossary.html", "visuals.html",
                         "questions.html", "search.html", "notes.html", "assets/search-index.js"):
                self.assertTrue((c.tmp / "site" / page).exists(), page)

    def test_lints_clean(self):
        with Copy() as c:
            code, out = c.lint()
            self.assertEqual(code, 0, out)
            self.assertIn("0 errors, 0 warnings", out)

    def test_the_accent_hue_reaches_the_site(self):
        with Copy() as c:
            c.build()
            self.assertIn("--hue: 60;", (c.tmp / "site/assets/tokens.css").read_text())

    def test_private_text_stays_out_of_search(self):
        with Copy() as c:
            c.build()
            index = (c.tmp / "site/assets/search-index.js").read_text()
            self.assertNotIn("single brood box", index)
            self.assertIn("What the mentor keeps over winter", index)   # the label is public


class TheFormatCheck(unittest.TestCase):
    def parse(self, c):
        return parse_topic(c.path(B01), load(c.path("guide.toml")))

    def messages(self, t):
        return " ".join(e["message"] for e in t["errors"])

    def test_a_private_tag_outside_a_private_block_is_an_error(self):
        with Copy() as c:
            c.edit(B01_MD, "[source: association-handbook p. 9]", "[private: mentor-call 1:00]")
            self.assertIn("sits outside a ':::private' block", self.messages(self.parse(c)))

    def test_a_section_cannot_outrank_its_topic(self):
        with Copy() as c:
            c.edit(B01_MD, "rank: critical", "rank: medium")
            self.assertIn("ranks above its topic", self.messages(self.parse(c)))

    def test_a_missing_part_is_an_error(self):
        with Copy() as c:
            c.edit(B01_MD, "# Not verified", "# Unchecked")
            msgs = self.messages(self.parse(c))
            self.assertIn("Unknown part '# Unchecked'", msgs)
            self.assertIn("'# Not verified' is missing", msgs)

    def test_the_case_part_follows_the_settings(self):
        with Copy() as c:
            c.edit("guide.toml", 'part = "In your apiary"', 'part = ""')
            self.assertIn("Unknown part '# In your apiary'", self.messages(self.parse(c)))

    def test_a_visual_with_its_own_colours_is_an_error(self):
        with Copy() as c:
            c.edit(B01 + "/fig-brood-timeline.svg", 'class="v-rule"', 'stroke="#ff0000"')
            self.assertIn("colours only through the v- classes", self.messages(self.parse(c)))

    def test_a_broken_topic_fails_the_build(self):
        with Copy() as c:
            c.edit(B01_MD, "# Materials", "# Things to read")
            code, out = c.build()
            self.assertEqual(code, 1)
            self.assertIn("ERROR", out)


class TheChecks(unittest.TestCase):
    def test_the_guard_fails_on_a_never_publish_term(self):
        with Copy() as c:
            c.edit(B01_MD, "A hive copies the hollow", "Keep a spare key nearby. A hive copies the hollow")
            code, out = c.build()
            self.assertEqual(code, 1)
            self.assertIn("[FAIL] Guard", out)

    def test_a_link_to_a_missing_anchor_fails_check_3(self):
        with Copy() as c:
            c.edit("content/questions.md", "### OQ-02.", "### Question two.")
            code, out = c.build()
            self.assertEqual(code, 1)
            self.assertIn("[FAIL] 3.", out)

    def test_a_glossary_home_outside_the_map_fails_check_7(self):
        with Copy() as c:
            c.edit("context/glossary.md", "B01 is the home.", "B09 is the home.")
            code, out = c.build()
            self.assertEqual(code, 1)
            self.assertIn("[FAIL] 7.", out)


class TheLint(unittest.TestCase):
    def findings(self, c):
        code, out = c.lint(B01)
        return code, out

    def test_a_banned_glossary_word_is_an_error(self):
        with Copy() as c:
            c.edit(B01_MD, "A young worker cleans cells", "A young worker cleans baby bees")
            code, out = self.findings(c)
            self.assertEqual(code, 1)
            self.assertIn("glossary-ban", out)

    def test_an_italic_glossary_word_is_a_warning(self):
        with Copy() as c:
            c.edit(B01_MD, "A young worker cleans cells", "A young worker cleans capped cells")
            code, out = self.findings(c)
            self.assertEqual(code, 0)
            self.assertIn("glossary-sense", out)

    def test_a_dash_is_an_error(self):
        with Copy() as c:
            c.edit(B01_MD, "A young worker cleans cells", "A young worker \u2014 the newest \u2014 cleans cells")
            code, out = self.findings(c)
            self.assertEqual(code, 1)
            self.assertIn("dash", out)

    def test_an_untagged_claim_about_the_case_is_a_warning(self):
        with Copy() as c:
            c.edit(B01_MD, "Before people built hives", "Hillside keeps its hives in a row. Before people built hives")
            code, out = self.findings(c)
            self.assertIn("case-untagged", out)

    def test_the_spelling_follows_the_settings(self):
        with Copy() as c:
            c.edit(B01_MD, "A young worker cleans cells", "A young worker cleans colored cells")
            self.assertIn("spelling", self.findings(c)[1])
            c.edit("guide.toml", 'spelling = "british"', 'spelling = "american"')
            self.assertNotIn("spelling", self.findings(c)[1])

    def test_the_reader_name_is_a_warning(self):
        with Copy() as c:
            c.edit(B01_MD, "A young worker cleans cells", "Sam sees a young worker clean cells")
            self.assertIn("reader-name", self.findings(c)[1])

    def test_a_never_publish_term_is_an_error(self):
        with Copy() as c:
            c.edit(B01_MD, "A young worker cleans cells", "The gate code is on the shed. A young worker cleans cells")
            code, out = self.findings(c)
            self.assertEqual(code, 1)
            self.assertIn("never-publish", out)


class TheSettings(unittest.TestCase):
    def test_an_unknown_key_is_refused(self):
        with Copy() as c:
            c.edit("guide.toml", "[guide]", "[guide]\ncolour = \"blue\"")
            with self.assertRaises(SettingsError):
                load(c.path("guide.toml"))

    def test_two_tiers_cannot_share_a_prefix(self):
        with Copy() as c:
            c.edit("guide.toml", 'prefix = "P"', 'prefix = "B"')
            with self.assertRaises(SettingsError):
                load(c.path("guide.toml"))

    def test_the_repository_template_loads(self):
        S = load(REPO / "guide.toml")
        self.assertEqual([t.prefix for t in S.tiers], ["B", "P", "M"])
        self.assertEqual(S.storage_prefix, "your-guide")


class OtherSettings(unittest.TestCase):
    """Settings the test guide leaves at their defaults."""

    def test_a_tag_with_a_required_time_stamp(self):
        with Copy() as c:
            c.edit("guide.toml", "[case]", '[[tags]]\nform = "call {time}"\nprivate = true\n\n[[tags]]\nform = "public"\n\n[case]')
            S = load(c.path("guide.toml"))
            self.assertTrue(S.is_private_tag("call 12:30"))
            self.assertIsNone(S.tag_re.fullmatch("[call]"))
            self.assertEqual(S.tag_kind("call 1:05 to 2:10"), "call")

    def test_question_groups_limit_which_questions_count(self):
        from core.topicmap import parse_questions
        with Copy() as c:
            c.edit("context/open-questions.md", "## About the colonies", "## Priority 1: about the colonies")
            c.edit("guide.toml", "[case]", '[map]\nquestion_groups = "Priority"\n\n[case]')
            qs = parse_questions(load(c.path("guide.toml")))
            self.assertEqual(sorted(qs), ["OQ-01"])
            self.assertEqual(qs["OQ-01"]["group"], "Priority 1: about the colonies")

    def test_a_guide_can_live_outside_the_workspace(self):
        with Copy() as c:
            moved = c.tmp / "elsewhere.toml"
            text = c.path("guide.toml").read_text().replace("[guide]", '[paths]\nroot = "guide"\n\n[guide]', 1)
            moved.write_text(text)
            code, out = quiet(build.main, ["--guide", str(moved), "--out", str(c.tmp / "site2")])
            self.assertEqual(code, 0, out)


class TheTermLists(unittest.TestCase):
    def test_words_match_whole_and_without_case(self):
        t = terms.Term("Hive")
        self.assertTrue(any(t.finditer("one hive here")))
        self.assertFalse(any(t.finditer("archive")))

    def test_a_regular_expression_can_match_case(self):
        t = terms.Term("re:(?-i:\\bOSR\\b)")
        self.assertTrue(any(t.finditer("OSR in May")))
        self.assertFalse(any(t.finditer("osr in May")))

    def test_sections_set_the_level(self):
        found, problems = terms.parse_term_list("# a comment\n[block]\nqueen\n[warn]\ndrone\n")
        self.assertEqual(problems, [])
        self.assertEqual([(t.raw, t.level) for t in found], [("queen", "block"), ("drone", "warn")])

    def test_the_scan_honours_the_allow_list(self):
        found, _ = terms.parse_term_list("[block]\nqueen\n")
        items = [("notes.md", "notes.md", "the queen lays")]
        self.assertEqual(quiet(scan.scan, items, found, set(), False)[0], (1, 0))
        self.assertEqual(quiet(scan.scan, items, found, {("notes.md", "queen")}, False)[0], (0, 0))

    def test_the_scan_finds_a_secret(self):
        items = [("config.txt", "config.txt", "key = AKIA" + "ABCDEFGHIJKLMNOP")]
        self.assertEqual(quiet(scan.scan, items, [], set(), True)[0][0], 1)


if __name__ == "__main__":
    unittest.main()
