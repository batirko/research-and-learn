#!/usr/bin/env python3
"""Check one topic folder, or one page without parts, against the file format.

    python3 engine/topic.py content/base/b04-how-a-colony-works
    python3 engine/topic.py content/base/b04-how-a-colony-works --json
    python3 engine/topic.py content/questions.md

It prints what a script extracts: the header, every section with its rank and
word count, every material, the positions, the visuals and the tags. Then the
errors and warnings. engine/format.md is the format.

Options:
    --guide FILE   the guide's settings file (default: guide.toml)
    --json         print the full structure the build uses

Exit code 1 means the file breaks the format. Warnings don't fail.
Python 3.11 or later, standard library only.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.settings import SettingsError, find_settings, load  # noqa: E402


def main(argv):
    args = [a for k, a in enumerate(argv) if not a.startswith("--") and (k == 0 or argv[k - 1] != "--guide")]
    if not args or "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0 if args else 2
    try:
        S = load(find_settings(argv))
    except SettingsError as exc:
        print("topic: %s" % exc, file=sys.stderr)
        return 2
    from core import pages, topicfile

    target = Path(args[0])
    if target.suffix == ".md" and target.name != topicfile.TOPIC_FILE:
        text, failed = pages.report(target, S)
        print(text)
        return 1 if failed else 0
    if target.name == topicfile.TOPIC_FILE:
        target = target.parent
    t = topicfile.parse_topic(target, S)
    if "--json" in argv:
        print(json.dumps(t, indent=2, ensure_ascii=False, default=str))
    else:
        print(topicfile.summary(t, S))
    return 1 if t.get("errors") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
