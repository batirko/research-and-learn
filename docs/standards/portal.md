# Standard: the portal

What the portal must do, the eight checks that prove it after every build, and how you check a built portal before you share it. **The portal** is the HTML site the build makes from the guide. The design inside these limits is the portal worker's.

Here, "you" is the portal worker, the orchestrator, or the owner before sharing.

## Requirements

**It's local.**

- The portal is a folder of files, written to `paths.out` (`site/` by default). It opens from disk in a browser.
- It works with the network off. No page loads a script, font, stylesheet or image from anywhere else.
- Every path is relative, so the folder can move.

**It follows the tiers.**

- The tiers are the first level of navigation.
- Each tier's page opens with its map: how its topics fit together. Until `content/<tier>/intro.md` exists, the page shows the tier's definition and says a map comes later.

**It shows rank and time everywhere.**

- Every topic, section and material shows its rank.
- Every topic and material shows its time.
- The reader can filter by rank and hide context sections.

**A topic page holds both parts.**

- The explanation and the materials sit on one page.
- A material shows its type, its time, its rank and what the reader gets from it.
- A topic that isn't written yet has a page that shows its entry in the topic map, marked as planned.

**It tells private from public.**

- A fact from a private source sits in a collapsed block, marked as private. A block the build closes for you, such as a private sentence on the glossary page, carries the label `privacy.label`.
- One control opens every private block on a page. Each page starts with them closed.
- A provenance tag shows next to its fact, with its meaning on hover.
- Search never shows what a private block holds.
- Nothing on the never-publish list reaches the portal.

**It starts with a way in.**

- The home page says what the guide is, how the ranks work, how to read it, and what private blocks are. `content/home.md` holds that text.
- It shows a reading order, critical topics first, from the topic map.
- It shows totals: time by tier and by rank, for the guide text and the materials.

**It has reference pages.**

- A glossary page, from `context/glossary.md`.
- A visual index: every visual with its job statement.
- The open-questions page, from `content/questions.md`.
- Every material, by rank.
- Offline search over the public text.

**It reads well.**

- Read marks, bookmarks, notes and to-dos, kept in the reader's browser. `portal.storage_prefix` keeps one guide's storage apart from another's.
- Light and dark themes, a comfortable line length, phone width and print.
- One accent colour, set by `portal.accent_hue`.
- Code, tables and visuals don't break the page width.

## Who changes what

- **The build makes every page.** `python3 engine/build.py` reads the sources and writes the portal. Only the orchestrator builds into `site/`. Nobody edits a built page by hand, because the next build overwrites it.
- **The portal worker changes the engine and the design.** It writes a change in `engine/` and tests it with a build into a folder of its own (`--out`). Its handoff logs the change and its reason. An upgrade replaces `engine/`, so the log is how a change gets made again.
- **The file format changes only through the orchestrator,** because every topic worker depends on it. `engine/format.md` is its one home.
- **Topic workers write text sources only.** A design change then never touches content, and a topic never touches shared HTML.

## The eight checks

The build runs these after every build and fails when one fails. `engine/README.md` explains each check and what to do when it fails.

1. **Nothing loads from the network.** No page loads a remote script, stylesheet, image or frame. No stylesheet imports anything or points `url()` at a remote address. No script but the search index mentions a remote address or a way to reach one, such as `fetch(`.
2. **Every topic appears in its tier with its rank.** Each topic folder in a tier's folder has a page. The page shows the topic as written, in the tier of its folder, with the rank its header gives. That rank matches the topic map's, and the tier's page links to the topic.
3. **No internal link is broken.** Every link between pages, and every link to an anchor, lands, in the pages and in the search index. The open-questions page has an anchor for every open question.
4. **Both themes are defined, and the page has a background.** The stylesheet defines light and dark, for the system setting and for the theme switch, and the body has an explicit background. A person checks by eye whether both themes look right.
5. **Private facts stay private.** Every private tag sits inside a collapsed private block, and no block starts open. The search index holds no private tag and no private paragraph. The home page and the open-questions page show as many private blocks as their source files hold. In a copy built to share, the check is stricter: no page holds a private block or a private tag, and the opening words of no private paragraph appear anywhere in the site.
6. **The home page totals match the pages.** Time by tier, by rank, written against planned, and materials by rank, all add up from the topic pages.
7. **The glossary page is complete and clean.** It shows every term. Every home topic it names exists in the topic map. It shows no bookkeeping: no sentence that starts with a word in `glossary.bookkeeping`, and no decision reference such as (D12). No private source shows outside a private block, when `privacy.glossary_source` names the pattern. The home page and the open-questions page name no private source in the open either, when `privacy.page_source` names it.
8. **The visual index is complete.** It shows every visual from the written topics and the tier maps, once each. A visual from a private block shows its title only: no drawing, caption, job statement or alt text.

**The guard** runs with them. Nothing on the never-publish list appears in any page, script, stylesheet or drawing of the portal. A list item that isn't a valid regular expression fails the guard too, because a list read in part can't be trusted.

A topic with a format error also fails the build. `python3 engine/topic.py <topic folder>` is the format check for one topic.

## Before you share a built portal

The portal is for the reader. A collapsed block only hides text from a glance: anyone who has the files can open every block. So before the portal goes to anyone else, build a copy without the private blocks, and check it.

1. **Build a copy to share,** and read the result:

   ```
   python3 engine/build.py --share
   ```

   It writes the copy to `site-share/` (`paths.share_out`). Each private block becomes a closed stub that keeps only what a closed block shows anyway: its label and its visuals' titles. Every check and the guard pass, and no topic has a format error.
2. **Open it from disk with the network off.** Look at a topic in both themes, at phone width, and in print preview.
3. **Run the private-term scan:**

   ```
   python3 tools/scan.py files site-share/ --terms <your list>
   ```

   The list holds the names and phrases that would identify a private source: people, places, organisations, dates of private conversations. Keep it outside the workspace, because the list names what it protects. A line under `[block]` fails the scan, and a line under `[warn]` is printed for you to judge. `python3 tools/scan.py --help` describes the format. Exit code 0 means no blocking hit.

   A hit in a copy without private blocks means the term sits in public text: a block's label, a visual's title, or a sentence that restates a private fact. Take it out of the source and rebuild.
4. **Read the stubs' labels.** Each left-out block still shows its label. Check that no label states the fact it hides.

The never-publish list and the private-term list do different jobs. The never-publish list sits in the workspace and keeps a fact out of the portal for everyone, the reader included. The private-term list sits outside it and catches what the reader may see but nobody else may.

## How a reviewer checks

1. Build into a folder of your own, `python3 engine/build.py --out <folder>`, and read every line of the output. A note about a skipped folder or a topic missing from the map is a finding.
2. Open the portal from disk with the network off, and walk the requirements above.
3. Open a page with private blocks. Check that each starts closed, that the open-all control works, and that a search for words inside a block finds nothing.
4. Read the visual index and the glossary page as the reader would.
5. After a design change, look at both themes, phone width and print by eye. Check 4 proves only that the themes exist.
