#!/usr/bin/env python3
"""Scan files or git history for private terms and for secrets.

Before you share something, this script checks it for anything on your
private-term list: the names, phrases and IDs that would identify a private
source. It can also check for secrets, such as API keys and private keys.

    python3 tools/scan.py files                 every file git tracks or would track
    python3 tools/scan.py files site/           the files under a folder, such as a built site
    python3 tools/scan.py staged                the files staged for the next commit
    python3 tools/scan.py history               every commit: messages, authors, refs and every file version
    python3 tools/scan.py message FILE          one commit message

Options:
    --terms FILE    The private-term list. Without it, the script reads the
                    PRIVATE_TERMS environment variable, then `git config guard.terms`.
    --allow FILE    Hits allowed on purpose. Default: allow.txt next to the term list.
    --secrets       Also scan for secrets.
    --no-terms      Skip the term list. Use it with --secrets, where no list exists,
                    such as in continuous integration.

The term list lives outside the repository, so the list itself never gets shared.
Its format: lines after "[block]" fail the scan, lines after "[warn]" are printed
for you to judge. One term per line, matched without regard to case, with a word
boundary at each end that is a letter or a digit. A line that starts with "re:"
is a Python regular expression. engine/core/terms.py has the details.

The allow list holds one line per hit you publish on purpose:
    <path inside the repository><TAB><the term exactly as the list writes it>

Exit code 0: no blocking hit. 1: at least one blocking hit or secret.
2: the term list is missing or unreadable, or the command is wrong.

Standard library only. Python 3.9 or later, so a git hook can run it anywhere.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "engine"))

from core import terms as T  # noqa: E402

# Secrets: patterns precise enough to block a commit without crying wolf.
SECRETS = [
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{50,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("OpenAI API key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}\b|\bsk-proj-[A-Za-z0-9_-]{40,}")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Stripe live key", re.compile(r"\b[rs]k_live_[0-9A-Za-z]{20,}\b")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----")),
    ("JSON web token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
]
# A secret assigned to a name, such as API_KEY = "...". The value must look random.
ASSIGNED = re.compile(
    r"(?i)\b(?:api[_-]?key|secret(?:[_-]?key)?|access[_-]?token|auth[_-]?token|password|passwd|session[_-]?key)"
    r"\s*[:=]\s*[\"']?(?P<value>[A-Za-z0-9/+_=.-]{20,})")


def looks_random(value):
    classes = sum(bool(re.search(p, value)) for p in (r"[a-z]", r"[A-Z]", r"[0-9]"))
    return classes >= 2 and not re.fullmatch(r"[a-z_.-]+", value)


def git(*args, check=True):
    r = subprocess.run(["git"] + list(args), capture_output=True)
    if check and r.returncode != 0:
        raise SystemExit("scan: git %s failed: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace").strip()))
    return r.stdout


def decode(data):
    if b"\x00" in data[:8192]:
        return None   # binary
    return data.decode("utf-8", "replace")


# ---------------------------------------------------------------- what to scan

def working_files(paths):
    """(where, path, text) for files on disk. text is None for a binary file."""
    if not paths:
        inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True)
        if inside.returncode == 0:
            names = git("ls-files", "-co", "--exclude-standard", "-z").decode("utf-8").split("\x00")
            for name in sorted(n for n in names if n):
                p = Path(name)
                if p.is_file():
                    yield name, name, decode(p.read_bytes())
            return
        paths = ["."]
    for root in paths:
        root = Path(root)
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)
        for p in files:
            yield str(p), str(p), decode(p.read_bytes())


def staged_files():
    names = git("diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR").decode("utf-8").split("\x00")
    for name in sorted(n for n in names if n):
        yield name, name, decode(git("show", ":" + name))


def history_items():
    """Everything git keeps: commit messages and identities, ref names, and every
    version of every file that any commit holds."""
    if not git("rev-list", "--all", check=False).strip():
        return
    log = git("log", "--all", "--format=%H%x1f%an <%ae>%x1f%cn <%ce>%x1f%B%x1e").decode("utf-8", "replace")
    for rec in log.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        sha, author, committer, body = (rec.split("\x1f") + ["", "", "", ""])[:4]
        yield "commit %s identity" % sha[:10], None, author + "\n" + committer
        yield "commit %s message" % sha[:10], None, body
    for ref in git("for-each-ref", "--format=%(refname)").decode("utf-8").split("\n"):
        if ref:
            yield "ref", None, ref
    seen = {}
    for line in git("rev-list", "--all", "--objects").decode("utf-8", "replace").split("\n"):
        if " " in line:
            sha, path = line.split(" ", 1)
            seen.setdefault(sha, path)
    if not seen:
        return
    shas = list(seen)
    check = subprocess.run(["git", "cat-file", "--batch-check=%(objectname) %(objecttype)"],
                           input="\n".join(shas).encode(), capture_output=True).stdout.decode()
    blobs = [l.split()[0] for l in check.split("\n") if l.endswith(" blob")]
    for sha in blobs:
        path = seen[sha]
        yield "%s @%s" % (path, sha[:10]), path, decode(git("cat-file", "-p", sha))


# ---------------------------------------------------------------- scanning

def load_allow(path):
    allowed = set()
    if path and Path(path).is_file():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "\t" in line:
                p, term = line.split("\t", 1)
                allowed.add((p.strip(), term.strip()))
    return allowed


def excerpt(text, m):
    a = max(0, m.start() - 30)
    b = min(len(text), m.end() + 30)
    return re.sub(r"\s+", " ", text[a:b]).strip()


def scan(items, terms, allowed, secrets):
    blocks = warns = 0
    for where, path, text in items:
        # A file's path is scanned too: a name can identify a source as well as a text can.
        checks = []
        if path:
            checks.append(("%s (its name)" % where, path, False))
        if text is not None:
            checks.append((where, text, True))
        for label, corpus, numbered in checks:
            for t, m in T.find(terms, corpus):
                if path and (path, t.raw) in allowed:
                    continue
                loc = "%s:%d" % (label, T.line_of(corpus, m.start())) if numbered else label
                print("  [%s] %s  %s  > %s" % (t.level, loc, t.raw, excerpt(corpus, m)))
                if t.level == T.BLOCK:
                    blocks += 1
                else:
                    warns += 1
        if secrets and text is not None:
            for label, rx in SECRETS:
                for m in rx.finditer(text):
                    print("  [secret] %s:%d  %s" % (where, T.line_of(text, m.start()), label))
                    blocks += 1
            for m in ASSIGNED.finditer(text):
                if looks_random(m.group("value")):
                    print("  [secret] %s:%d  a value assigned to a secret's name" % (where, T.line_of(text, m.start())))
                    blocks += 1
    return blocks, warns


def find_term_list(arg):
    if arg:
        return arg
    if os.environ.get("PRIVATE_TERMS"):
        return os.environ["PRIVATE_TERMS"]
    r = subprocess.run(["git", "config", "--get", "guard.terms"], capture_output=True)
    if r.returncode == 0 and r.stdout.strip():
        return os.path.expanduser(r.stdout.decode().strip())
    return None


def main(argv):
    args, opts, k = [], {}, 0
    while k < len(argv):
        a = argv[k]
        if a in ("--terms", "--allow"):
            if k + 1 >= len(argv):
                print("scan: %s needs a file" % a, file=sys.stderr)
                return 2
            opts[a] = argv[k + 1]
            k += 2
            continue
        if a in ("--secrets", "--no-terms"):
            opts[a] = True
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            args.append(a)
        k += 1
    if not args or args[0] not in ("files", "staged", "history", "message"):
        print(__doc__)
        return 2
    mode, rest = args[0], args[1:]

    terms, allowed = [], set()
    if not opts.get("--no-terms"):
        path = find_term_list(opts.get("--terms"))
        if not path:
            print("scan: no private-term list. Pass --terms FILE, set PRIVATE_TERMS, or run "
                  "`git config guard.terms <file>`. The scan fails without the list.", file=sys.stderr)
            return 2
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            print("scan: the private-term list is missing: %s. The scan fails without it." % path, file=sys.stderr)
            return 2
        terms, problems = T.parse_term_list(Path(path).read_text(encoding="utf-8"))
        for p in problems:
            print("scan: %s: %s" % (path, p), file=sys.stderr)
        if problems:
            return 2
        if not terms:
            print("scan: the private-term list at %s holds no terms." % path, file=sys.stderr)
            return 2
        allowed = load_allow(opts.get("--allow") or os.path.join(os.path.dirname(path), "allow.txt"))
    elif not opts.get("--secrets"):
        print("scan: --no-terms leaves nothing to scan. Add --secrets.", file=sys.stderr)
        return 2

    if mode == "files":
        items = working_files(rest)
    elif mode == "staged":
        items = staged_files()
    elif mode == "history":
        items = history_items()
    else:
        if not rest:
            print("scan: message needs a file", file=sys.stderr)
            return 2
        text = Path(rest[0]).read_text(encoding="utf-8", errors="replace")
        text = "\n".join(l for l in text.splitlines() if not l.startswith("#"))
        items = [("commit message", None, text)]

    what = ("private terms" if terms else "") + (" and secrets" if terms and opts.get("--secrets") else
                                                 "secrets" if opts.get("--secrets") else "")
    print("Scanning %s for %s." % ({"files": "files", "staged": "staged files", "history": "git history",
                                     "message": "the commit message"}[mode], what))
    blocks, warns = scan(items, terms, allowed, opts.get("--secrets"))
    if blocks:
        print("scan: %d blocking hit%s. Fix them before you share this." % (blocks, "" if blocks == 1 else "s"))
        return 1
    print("scan: no blocking hit%s." % ((", %d warning%s to judge" % (warns, "" if warns == 1 else "s")) if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
