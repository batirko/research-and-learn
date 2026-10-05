#!/usr/bin/env python3
"""Build the portal from the guide's sources, then check it.

    python3 engine/build.py
    python3 engine/build.py --guide path/to/guide.toml --out path/to/site

Reads guide.toml, the topic map, the open questions (their titles only), the
glossary, every topic folder, the tier introductions, the home page text and
the open-questions page. Writes the site to the folder that paths.out names,
site/ by default. Open its index.html in a browser.

Options:
    --guide FILE   build another guide, from its settings file (default: guide.toml)
    --out DIR      write the site somewhere else
    --share        build a copy to share: every private block is left out, and only
                   its label and its visuals' titles stay. It goes to site-share/
                   (paths.share_out) unless --out says otherwise. Check 5 then makes
                   sure no private text is anywhere in it. Scan it before you send it:
                   python3 tools/scan.py files site-share/ --terms <your list>

Exit code 1 when a topic has format errors or a check fails.
Python 3.11 or later, standard library only.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.settings import SettingsError, find_settings, load  # noqa: E402


def main(argv):
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    try:
        S = load(find_settings(argv))
    except SettingsError as exc:
        print("build: %s" % exc, file=sys.stderr)
        return 2
    from core import checks
    from core.site import Site

    share = "--share" in argv
    out_dir = S.out_dir(share)
    if "--out" in argv:
        k = argv.index("--out")
        if k + 1 >= len(argv):
            print("build: --out needs a folder", file=sys.stderr)
            return 2
        out_dir = Path(argv[k + 1]).expanduser().resolve()

    site = Site(S, share=share).load()
    site.build(out_dir)

    written = [t for t in site.topics.values() if t["written"]]
    print("Built %d pages into %s" % (len(list(out_dir.glob("*.html"))), out_dir))
    print("Topics: %d in the map, %d written" % (len(site.map["order"]), len(written)))
    failed = False
    for t in sorted(written, key=lambda x: x["id"]):
        p = t["parsed"]
        print("  %s  %d words, %d min, %d errors, %d warnings" % (t["id"], p["words"], p["minutes"], len(p["errors"]), len(p["warnings"])))
        for e in p["errors"]:
            print("      ERROR line %s: %s" % (e["line"], e["message"]))
            failed = True
        for w in p["warnings"]:
            print("      warning line %s: %s" % (w["line"], w["message"]))
    for key, pg in sorted(site.page_files.items()):
        name = pg["path"]
        try:
            name = Path(name).relative_to(S.root)
        except ValueError:
            pass
        if pg["errors"] or pg["warnings"]:
            print("  %s  %d errors, %d warnings" % (name, len(pg["errors"]), len(pg["warnings"])))
        for e in pg["errors"]:
            print("      ERROR line %s: %s" % (e["line"], e["message"]))
            failed = True
        for w in pg["warnings"]:
            print("      warning line %s: %s" % (w["line"], w["message"]))
    for prob in site.problems:
        print("  note: %s" % prob)

    results = checks.run(out_dir, site)
    print("Checks:")
    for name, ok, detail in results:
        print("  [%s] %s%s" % ("pass" if ok else "FAIL", name, (": " + detail) if detail else ""))
        failed = failed or not ok
    if share:
        print("A copy to share, without its private blocks. Before you send it, scan it:")
        print("  python3 tools/scan.py files %s --terms <your private-term list>" % out_dir)
    print("Open %s" % (out_dir / "index.html"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
