# The engine

The engine turns a guide's text files into the portal: a static HTML site that opens from disk and works with the network off. It also checks the result. It reads every value that changes between guides from `guide.toml`, so nothing here names a guide.

Nothing you write lives in `engine/` or `tools/`. To upgrade a workspace, copy both folders from a newer release.

## Commands

The engine needs Python 3.11 or later and nothing outside the standard library. If `python3` is older on your machine, call `python3.11` instead.

| To | Run |
| --- | --- |
| Build the portal and run the checks | `python3 engine/build.py` |
| Check one topic against the format | `python3 engine/topic.py content/<tier>/<id>-<slug>` |
| Check a page without parts | `python3 engine/topic.py content/questions.md` |
| Lint the writing | `python3 tools/lint.py` (every topic) or `python3 tools/lint.py <topic folder>` |
| List the lint's rules | `python3 tools/lint.py --rules` |
| Scan a built portal for private terms | `python3 tools/scan.py files site/ --terms <your list>` |
| Run the engine's tests | `python3 -m unittest discover -s engine/tests` |

Every command takes `--guide <settings file>` to work on a guide whose `guide.toml` lives elsewhere. `build.py` also takes `--out <folder>`.

`build.py` rebuilds the whole site into `site/`, prints each topic's word count with its errors and warnings, then runs the checks. It exits with code 1 when a topic has a format error or a check fails. To open the portal, open `site/index.html` in a browser.

## What the build reads

The paths come from `[paths]` in `guide.toml`. These are the defaults.

| Source | What the portal gets from it |
| --- | --- |
| `guide.toml` | Every setting: the title, the tiers, the part headings, the sizes, the limits, the ranks' words, the tags, the accent hue |
| `curriculum/topic-map.md` | Every topic, its tier, group, rank, size and cluster, in order. The reading order. The plan shown for a topic not written yet |
| `content/<tier>/<id>-<slug>/topic.md` | Each written topic, in the format of `engine/format.md` |
| `content/<tier>/intro.md` | The map at the top of a tier's page, when it exists |
| `content/home.md` | The home page text, when it exists |
| `content/questions.md` | The open-questions page, when it exists |
| `context/open-questions.md` | Each question's ID and title only. A question's body can hold private facts without tags, so the build never reads it |
| `context/glossary.md` | The glossary page |
| `context/never-publish.md` | What the guard looks for in the built site |

A missing source doesn't stop the build. An empty workspace builds a portal with its tiers and no topics.

## What it writes

| Page | What it holds |
| --- | --- |
| `index.html` | The home page text, then where to start, the tiers and the time totals |
| `<tier>.html` | A tier: its definition, its map, its topics by group, with rank filters |
| `<id>.html` | One page per topic in the map. A written topic shows its text; a planned one shows its plan |
| `topics.html` | Every topic in one table |
| `materials.html` | Every material from the written topics, by rank |
| `questions.html` | The open questions, each with an anchor and the topics that cite it |
| `glossary.html` | Every term, with its home topic and the words it replaces |
| `visuals.html` | Every visual, with its job statement, linked to its section |
| `search.html` | Search over the public text |
| `notes.html` | The reader's bookmarks, notes and to-dos |
| `assets/` | The stylesheets, the scripts and the search index |

## The eight checks

They run after every build, on what the build wrote. `docs/standards/portal.md` says why each exists.

1. **Nothing loads from the network.** No page, stylesheet or script reaches an outside address.
2. **Every topic appears in its tier with its rank.** Each topic folder has a page, filed under its tier, with the rank its header and the map give it.
3. **No internal link is broken.** That covers every page, every entry in the search index, and an anchor for every open question.
4. **Both themes are defined, and the page has a background.** How they look is checked by eye.
5. **Every private tag sits in a closed private block, and search holds nothing a private block holds.** The check probes the search index with the opening words of every private paragraph.
6. **The home page's totals match the pages.**
7. **The glossary page is complete and clean.** Every term shows, every home topic exists, and no bookkeeping or private source shows in the open. The home page and the open-questions page get the same scan for private sources.
8. **The visual index is complete.** Every visual shows once, and a private one shows its title only.

**The guard** runs last: nothing on the never-publish list may appear anywhere in the site.

When a check fails, its line names the page and the problem. Fix the source and rebuild. Never edit a page in `site/`: the next build deletes it.

## In the browser

The portal keeps everything a reader does in the browser's own storage: read marks, bookmarks, notes, to-dos, the theme and the hidden context sections. Nothing leaves the browser. Every key starts with `portal.storage_prefix`, so two guides opened from disk don't mix. The notes page can download a copy as a file and load it back, which is how notes move to another browser.

Search runs from `assets/search-index.js`, which only the search page loads. It holds the public text: of a private block, only its label and the titles of its visuals.

## Files here

| Path | What it is |
| --- | --- |
| `build.py` | The build: renders every page, then runs the checks |
| `topic.py` | The format check, for one topic or one page without parts |
| `format.md` | The topic file format: the contract with topic writers |
| `design.md` | The design decisions behind the look |
| `core/settings.py` | Reads `guide.toml`, holds the defaults, builds the shared patterns |
| `core/topicfile.py` | Reads and checks one topic folder |
| `core/pages.py` | Reads the pages without parts, and finds where each question opens |
| `core/topicmap.py` | Reads the topic map and the open questions' titles |
| `core/glossary.py` | Reads the glossary for its page and for the lint |
| `core/render.py` | Renders the Markdown subset, topic links and provenance tags |
| `core/site.py` | Renders every page and the search index |
| `core/checks.py` | The eight checks and the guard |
| `core/terms.py` | Term lists: the never-publish list and the private-term scan share it |
| `assets/` | `tokens.css`, `visuals.css`, `site.css`, `site.js`, `notes.js` |
| `tests/` | The tests, and the test guide they build |
