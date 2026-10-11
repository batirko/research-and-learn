#!/usr/bin/env python3
"""Show which topics the concept file is up to date for, and record a concept pass.

    python3 engine/concepts.py
    python3 engine/concepts.py --stamp B01 P01
    python3 engine/concepts.py --stamp --all

The concept file (paths.concepts, content/concepts.json by default) keeps a fingerprint of
each topic's text, taken when a concept pass read the topic. With no option, this lists every
written topic: up to date, changed since its pass, or not read yet. The build prints the same
notes, and none of them fails it.

Options:
    --guide FILE   work on another guide, from its settings file (default: guide.toml)
    --stamp IDS    record that a pass has read these topics as they are now. Run it after you
                   checked a topic's concepts and uses against its current text.
    --all          with --stamp: every written topic

Exit code 1 when a topic has changed since its pass or hasn't been read, with no option.
Python 3.11 or later, standard library only.
"""

import json
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
        print("concepts: %s" % exc, file=sys.stderr)
        return 2
    from core import conceptmap
    from core.site import Site

    site = Site(S).load()
    path = S.file("concepts")
    if not path.exists():
        print("concepts: %s doesn't exist yet. engine/format.md, \"The concept file\", describes it." % path, file=sys.stderr)
        return 2
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        print("concepts: %s is not valid JSON: %s" % (path, exc), file=sys.stderr)
        return 2
    written = [tid for tid in site.map["order"] if site.topics.get(tid, {}).get("written")]

    if "--stamp" in argv:
        k = argv.index("--stamp")
        ids = written if "--all" in argv else [a.upper() for a in argv[k + 1:] if not a.startswith("--")]
        if not ids:
            print("concepts: --stamp needs topic IDs, or --all", file=sys.stderr)
            return 2
        read = raw.setdefault("read", {})
        for tid in ids:
            if tid not in written:
                print("concepts: %s isn't a written topic in the topic map" % tid, file=sys.stderr)
                return 2
            read[tid] = conceptmap.topic_fingerprint(site.topics[tid])
            print("  %s stamped" % tid)
        raw["read"] = {tid: read[tid] for tid in sorted(read)}
        path.write_text(json.dumps(raw, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return 0

    read = {str(k): v for k, v in (raw.get("read") or {}).items()}
    behind = 0
    for tid in written:
        if tid not in read:
            state = "not read yet"
        elif conceptmap.topic_fingerprint(site.topics[tid]) != read[tid]:
            state = "changed since its pass"
        else:
            state = "up to date"
        behind += state != "up to date"
        print("  %s  %s" % (tid, state))
    return 1 if behind else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
