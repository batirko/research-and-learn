# research-and-learn: the concept

**Status:** version 1 built on 2026-10-05, except the example guide. This page decides what the project is, what it ships, and how it stays free of the private guide it was extracted from.

## What it is

You get a finished guide to a subject you need to understand by a date, written for you and readable offline. You run it with your coding agent: it interviews you, researches the subject, proposes a ranked map of topics, and then coordinates subagents that research, write, check and build the guide one topic at a time. Each topic explains its subject from the ground up and ends with a short, ranked list of outside materials. Your sources, research, decisions and notes accumulate in the folder, so your copy becomes your project.

It's an agentic workspace: a repository you take a copy of and work inside. There is no package to install and no server to run.

## Where it comes from

It is extracted from one real guide, built for one reader on a deadline. That guide has 45 topics in three tiers and about 120,000 words. It went from the request to 45 topics in the portal in two days of agent sessions.

Every file here is written anew for any subject. None of that guide's content, structure or history is in this repository. "Keeping the source guide out" says how.

## When to use it

Use it when three things hold:

- **You need understanding, not a summary.** You'll have to follow conversations, make decisions and defend them.
- **You have a goal.** You can name what you must be able to do after reading.
- **You have a time budget.** A date, and the hours a day you can read.

It fits best where general knowledge meets a specific situation. Examples: a new job in an unfamiliar field, taking over a product or a codebase, an exam, a move to another country. The specific situation is **the case**. The guide teaches the general subject and keeps what is known about the case apart, with its sources.

## The principle

**The guide's own text carries the knowledge. Everything else points at it or supports it.**

Before the source guide, its reader had a study plan of 201 sources. They had opened 2 when they needed them. People read explanations. So a topic explains its subject in full, and then offers a few ranked materials for depth. A long list is a failure of selection.

## What you get: the portal

The guide is a static HTML site that opens from disk and works with the network off.

- **Three ways in.** The home page says what the guide is, how ranks work and what to read first. It shows a reading order, critical topics first, and the total time by tier and by rank.
- **Tiers as the first level.** Each tier opens with a short map of how its topics fit together.
- **Rank and time everywhere.** Every topic, section and material shows its rank. Every topic and material shows its time. You can filter by rank and hide context sections.
- **One page per topic,** with both parts: the explanation and the materials.
- **Private facts stay private.** A fact from a private source sits in a collapsed block. One control opens all of a page's blocks. Search never shows private text.
- **Reference pages.** A glossary, an index of every visual with its job, the open questions, and all materials by rank.
- **Offline search** over the public text.
- **Read marks, bookmarks, notes and to-dos,** kept in your browser.
- **Light and dark themes, phone width and print.**

## How a guide gets built

| Phase | What happens | What you do |
| --- | --- | --- |
| Set up | The agent interviews you: the reader, the goal, the date and hours, the subject, the case, your sources, the tiers | Answer, and drop your sources into the folder |
| Scaffold | The agent researches the case, writes the context notes and the open questions, and proposes a topic map that fits your hours | Nothing |
| Kickoff | The agent shows its assumptions and the map | Confirm or change them |
| Pilot | One topic per tier, written and checked, and a portal that shows them | Read them. Say what to change about depth, length, ranks, materials, visuals and design |
| Waves | Critical topics first, then high, then medium. The portal is rebuilt as each topic finishes | Start reading. Stop the build when you have enough |
| Integration | Tier maps, the home page, the glossary, the open questions, and checks across the whole guide | Nothing |
| Reading | You read, mark and note. Fixes go out in batches | Read |

You're needed at three points: the set-up interview, the kickoff, and the pilot. The orchestrator brings you any other question only when a wrong guess would waste a worker's run.

**The pilot comes before the fan-out.** Your preferences on depth, length and visuals show up only when you see a page. In the source build, all three pilot writers filled their size band to its ceiling, and the reader cut the bands after reading them. The other 42 topics then followed the new bands.

## The method that ships

These rules are the product. The engine enforces what a script can check, and the briefs carry the rest.

### Tiers

Tiers are the first-level split of the guide. You define them at set-up, in your own words, and the definitions don't change after that. A topic lives in one tier.

The default is three tiers, from the source guide:

| Tier | Holds |
| --- | --- |
| **Base** | What you need to understand the domain: how it works, who does what, and why |
| **Practical** | The practices, frameworks, research and measures you use to act in it |
| **Modern** | What today's tools and technology change, in the problem and in the solutions |

### Four ranks

Topics, sections and materials carry one of four ranks.

| Rank | A topic or section | A material, and what you do with it |
| --- | --- | --- |
| **Critical** | You can't reach your goal without it | Read or watch it in full. It gives something the guide can't |
| **High** | Needed to follow the core of the subject | Skim it, 10 to 15 minutes |
| **Medium** | Useful background that makes other topics easier | Skim it faster, about 5 minutes |
| **Context** | Orientation and completeness | Open it when you need it |

Critical materials are capped: at most one per topic, two in a critical topic, and a total for the guide. Each states what it gives that the guide doesn't, and how long it takes.

### A topic's parts

1. **Header:** tier, rank, size, reading time, depth, the topics to read first, the date facts were checked.
2. **Why it matters for your goal,** with evidence.
3. **The short version:** five to eight lines you can keep in your head.
4. **The explanation:** from the ground up, in ranked sections. Each concept closes with what it means for your goal.
5. **In your case:** what is known about the case, with tags; what is unknown, as open questions; what to look at first. Present only when the guide has a case.
6. **Positions,** where practitioners disagree and you'll have to take a side. Each has the position, the reasoning, the strongest case against, and what would change it.
7. **Materials:** at least one, ranked.
8. **Not verified:** what the writer couldn't confirm. Always present, even when empty.
9. **Check yourself:** up to five questions. Optional.

**Depth has three levels.** At level 1 you can explain the concept in two sentences. At level 2 you can name the alternatives and why someone picks one. At level 3 you can say what a choice costs, where it breaks, and what would change your mind. A topic's rank sets the depth it reaches.

### Visuals earn their place

A visual exists only when it passes four checks.

1. **It has a job.** One sentence, written before drawing, says what the reader gets from it that the text gives slower or not at all.
2. **A first-time reader is better off with it.** Restating the text in boxes fails.
3. **The subject has a shape:** topology, actors over time, branches, changing state, quantity, or position in two dimensions.
4. **It can be drawn truthfully.** Unknown parts are drawn differently. A drawing of a guess reads as knowledge.

Many topics have no visual. The portal's visual index shows each one with its job, so a reviewer can apply the test.

### Evidence

- **Every source is opened by the session that cites it.** A link from memory or a search snippet doesn't count.
- **Every fact about the case carries a provenance tag** that says where it came from. The default tags are `[public]`, `[source: name]` for a document in your sources folder, `[private: name]` for a private source, `[inference]` and `[unverified]`. You can add your own.
- **Evidence and interpretation stay apart.** The context notes are a first reading made before you knew the case well. When research contradicts them, the evidence wins, and the worker says so.
- **Unknowns become open questions,** each with an ID, its likely answers and what would settle it. The open questions become a page you take into your first weeks.
- **Don't guess about the case.** "Your club probably uses five heart-rate zones" is a defect. "Your club's zone system is unknown; the two common ones are X and Y, and this is how to tell them apart" is fine.
- **Your sources are frozen.** Nobody edits them. When a worker finds an error in one, the correction goes into the worker pack, so every later worker sees it.

### Privacy

- A fact from a private source sits in a private block, collapsed, and out of search.
- **A block's title and a figure's title are public text,** because a collapsed block shows them.
- **Some things never reach the portal.** You list them in a never-publish file, and the build fails if one appears.
- **No script catches a private fact restated in other words.** The writer and the reviewer search the public text for it. In the source build, one review found eleven such sentences in one topic.

### Words

- **One word per concept,** across the whole guide. The glossary holds the list, and the lint flags words the glossary bans.
- **One home per concept.** When several topics touch a concept, the map names the topic that explains it. The others link to it.
- **Plain writing:** one idea per sentence, active voice, exact words for certainty, and a slop pass before handoff.

## The agents

One **orchestrator** session runs the build. It doesn't write topics. It starts **workers**, keeps the shared files true and brings you in when a decision is yours.

| Worker | Does | Model |
| --- | --- | --- |
| Topic | Researches and writes the topics of one cluster | The strongest |
| Review | Reads finished topics as you would, then checks them against the standards | The strongest |
| Portal | Designs the portal and changes the engine | The strongest |
| Context | Checks and extends what is known about the case | The strongest |
| Facts check | Compares every tagged claim with the sources | A smaller model |
| Fix | Applies a check's findings to a topic | The strongest |
| Helpers | Find candidate sources, check links, run the lint | A smaller model |

They coordinate through files:

- **A brief** gives a worker its goal, its limits, its reading and the picture of what the other workers are doing. It gives context, not a design.
- **A handoff** is the file a worker leaves when it finishes: what exists, what it couldn't verify, and what it proposes.
- **The board** has every topic's status. **The decision log** has every settled question, with its reason and what would reverse it.
- **Each worker writes only the files its brief names.** Workers share one folder, and only the orchestrator runs git.

**Two modes.** In the lean mode, the default, workers are subagents of the orchestrator, and independent reviews go to the pilot and to topics that rest most on facts about the case. In the full mode, each worker is its own session and every topic gets a review.

**What it costs.** In the source build, a topic cost about 320,000 to 400,000 tokens to reach the portal with a batch facts check, and about 480,000 to 650,000 with an independent review, as the agent tool reported. The logged runs after the pilot add up to about 19 million tokens for 42 topics and integration. At that rate, 15 topics cost about 5 to 6 million tokens, before the scaffold and integration.

## Lessons from the source build, shipped as rules

Each of these cost a run to learn.

1. **Writers fill a size band to its ceiling.** So briefs say: aim at the middle.
2. **Writers judge critical materials one cluster at a time and pick too few.** So integration includes one pass that compares the strongest materials across the whole guide.
3. **A check of the context notes found 17 wrong or overstated claims among 176.** So the facts check runs on every topic that rests on the case, and checking effort goes where a wrong fact costs most.
4. **A subagent can't start its own subagents.** In the lean mode, a topic writer does its own research.
5. **A session that can't reach the web writes from memory.** So a researcher fetches one page it needs before it starts, and stops if the fetch fails.
6. **An unattended run stops at the first permission prompt, and a usage limit can stop five workers at once.** So the orchestrator commits at every quiet point, and says at kickoff whether the session can work alone.
7. **Each run's token cost is logged and compared with the projection,** so the plan changes before the budget runs out.
8. **When the people who own the case name several competing explanations, a topic weighs all of them.** It doesn't pick one before the evidence does.

## What the repository contains

```
research-and-learn/
├── README.md            What you get, how to start, what it costs
├── AGENTS.md            The operating guide for any agent
├── CLAUDE.md            Points at AGENTS.md
├── LICENSE              MIT
├── guide.toml           Your guide's settings
├── docs/
│   ├── method.md        The method on one page
│   ├── request.md       Your request in your own words, with the assumptions (written at set-up)
│   ├── decisions.md     The decision log (starts empty)
│   └── standards/       Topic page, sources, visuals, writing, portal
├── context/             What is known about you, your goal and your case
│   ├── README.md        Provenance tags, and how notes keep evidence apart from interpretation
│   ├── reader.md
│   ├── glossary.md
│   ├── open-questions.md
│   ├── never-publish.md
│   └── sources/         Your frozen sources: notes, transcripts, documents
├── curriculum/
│   └── topic-map.md     What gets built and why: ranks, sizes, clusters, homes, reading order
├── orchestration/
│   ├── playbook.md      How the orchestrator runs the build
│   ├── worker-pack.md   The standing reading for every worker
│   ├── board.md
│   ├── briefs/          Templates for each kind of worker, and one filled example of each
│   └── handoffs/
├── content/             The topics, by tier, with the home page and the open-questions page
├── research/            One dossier per topic: every candidate source and its verdict
├── reviews/
├── reference/           Earlier guides or pages you want this one to follow. Optional
├── engine/              The build, the checks, the format parser, styles and scripts
├── site/                The built portal
├── tools/               The lint and the private-term scan
├── example/             A complete small guide on an unrelated subject
└── .claude/skills/      set-up, scaffold, and the slop pass
```

**The template ships the method and leaves the identity blank.** Everything under `context/`, `curriculum/`, `content/` and `orchestration/` starts as a template with instructions. The set-up and the scaffold fill them.

**To upgrade, copy `engine/` and `tools/` from a newer release.** Nothing you write lives there. A guide's copy otherwise diverges for good, as any workspace does.

## Configuration

`guide.toml` holds every value that changes from one guide to another. Each number lives there once, and the standards refer to it by name.

- The guide's title, language and spelling rule.
- The tiers: ID, name, ID prefix and definition.
- The heading of the case part, or none.
- Size bands, reading speed, and the number of XL exceptions allowed.
- Material limits: per topic, critical per topic, critical in the guide.
- Provenance tags, and which ones are private.
- Portal settings: the accent colour and the storage key prefix.

## The engine

- **Python 3.11 or later, standard library only.** It reads `guide.toml` with `tomllib`.
- **Plain JavaScript,** no libraries. Nothing loads from the network.
- **One command builds the portal:** `python3 engine/build.py`. It fails on a format error or a failed check.
- **Eight checks run after every build:** no network loads, every topic in its tier with its rank, no broken internal link, both themes defined, private text collapsed and out of search, totals that match, a complete glossary, and a complete visual index.
- **A format check per topic** and **a lint** for the writing rules, the material limits, the tags and the glossary.
- **A private-term scan** that reads a list of terms from a file outside the repository and searches files or git history for them. Guide owners use it before they share a built site. This repository uses it on itself.

## Fit with the agentic workspaces index

The index lists a repository when four rules hold. This project meets each one by design.

| Rule | How it holds |
| --- | --- |
| It ships a workspace you use as a project folder | The folder structure, the set-up skill and `AGENTS.md` at the root |
| You operate it through your own agent | The orchestrator and its workers do the work |
| State accumulates | Sources, notes, research, topics, decisions and your reading notes stay in the folder |
| The output is your work | The guide |

The index has no manual entries. Its crawler finds repositories through GitHub search over name, description and topics. So the description says "Claude Code workspace", the topics include `claude-code` and `agentic-workspace`, and `CLAUDE.md` and `AGENTS.md` sit at the root.

## Keeping the source guide out

The source guide holds private material: conversations, personal notes and facts about a specific case. None of it may reach this repository, now or later.

### The rule

**Re-author, never copy.** Nothing moves from the source into this repository by copying a file, cloning, forking, adding a remote, cherry-picking or applying a patch. Every file here is written anew. A session reads the source only to understand a mechanism.

### What could leak, and what stops it

| What could leak | What stops it |
| --- | --- |
| Git history, which holds every private file ever committed | A fresh `git init`. The source is never a remote, a fork or a subtree |
| The built site, which embeds the text of private blocks | Built output is never copied. This repository builds only its example |
| Secrets and hosting IDs | Hosting isn't in version 1. A secret-pattern scan runs before each push |
| Names, dates and phrases written into the engine's code | The engine is rewritten to read `guide.toml`. Every value that named the source becomes a setting, and the shipped value comes from the example |
| Topics, glossary terms and open questions, which reveal the case | No content folder is copied. The example is on an unrelated subject |
| Examples in the method docs that describe the case | The docs are written anew, with examples from the example guide |
| Lessons tied to the source's decision numbers and topics | Each lesson is restated as a general rule |
| A private fact restated in other words | A reviewer reads every file before the repository goes public |
| The list of private terms itself | It lives outside the repository, at `~/.config/research-and-learn/private-terms.txt` |

### The private-term list

The list holds every name and phrase that would identify the source: organisations, products, people and their handles, the reader and their past employers, the subjects of earlier guides, source-specific tags, topic titles, coined glossary terms, hosting names, database IDs, URLs, storage key prefixes and dates of private conversations. It is built from the source's own glossary and context notes before the first file is written here.

A file can allow one term on purpose, such as the author's name in `LICENSE`.

### Gates before the repository goes public

1. **The private-term scan finds nothing,** in the files and in every commit.
2. **The secret scan finds nothing.**
3. **A reviewer that didn't write the files reads every one of them** with one job: find anything that describes the source's case, including paraphrase. It runs on the strongest model, with the source open for comparison.
4. **The repository is pushed as private first.** It goes public after gates 1 to 3 pass and the owner has read the README.

A git hook runs gates 1 and 2 on every commit and push in this repository. The hook reads the term list from its path outside the repository, and fails when the list is missing.

### The genericity test

**The example guide is built by this workspace's own workflow,** in a session that doesn't have the source open. If the workflow can't produce it without the source, the extraction isn't finished. The example then proves the method works on an unrelated subject, and it becomes the engine's test: continuous integration builds it and runs every check.

### After launch

Lessons from real guides come back only as re-authored general rules, through the same gates. No file from a real guide ever enters this repository. `AGENTS.md` states this as a hard rule.

## Version 1

**In:** the method docs and templates; the configurable engine with its checks, format check and lint; read marks and notes kept in the browser; the set-up and scaffold skills; the playbook with both modes; brief templates with filled examples; the example guide; the private-term scan; continuous integration that builds the example; the README; the MIT licence.

**Later:** a hosted copy with a password and notes that sync across devices; interface text in other languages; ports to other agent harnesses beyond `AGENTS.md`.

## Open decisions

1. **The example's subject.** Recommended: preparing for a first marathon. It has a strong Modern tier (wearables, shoe research), quantities a visual can show, a natural case (your race and your schedule) and plenty of first-hand sources.
2. **How much of the origin to tell.** Recommended: "extracted from a 45-topic guide built for one reader on a deadline", with no field, organisation or role.
3. **Notes that sync across devices.** Recommended: after version 1, as an optional module with its own security review.
