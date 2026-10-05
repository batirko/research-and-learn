# research-and-learn

You get a guide to a subject you must understand by a date: written for you, ranked by what matters, and readable offline. You build it with your coding agent. It interviews you, researches the subject, proposes a ranked map of topics that fits your hours, then runs subagents that research, write, check and build the guide one topic at a time. You start reading while the rest is still being written.

This is a Claude Code workspace: a folder you copy and work inside. There's nothing to install and no server to run.

It was extracted from a 45-topic guide built for one reader on a deadline: about 120,000 words, from the request to 45 topics in the portal in two days of agent sessions. None of that guide's content is in this repository; every file here is written anew for any subject.

## When it fits

Use it when three things hold:

- **You need understanding, not a summary.** You'll have to follow conversations, make decisions and defend them.
- **You have a goal.** You can name what you must be able to do after reading.
- **You have a time budget.** A date, and the hours a day you can read.

It fits best where general knowledge meets a specific situation: a new job in an unfamiliar field, taking over a product or a codebase, an exam, a move to another country. The guide teaches the general subject and keeps what is known about your situation apart, with its sources.

## What you get

A static HTML portal that opens from disk and works with the network off.

- **Topics that carry the knowledge.** Each topic explains its subject from the ground up, then offers a few ranked materials for depth. Before the source guide, its reader had a study plan of 201 sources and had opened 2 of them. People read explanations.
- **Rank and time everywhere.** Every topic, section and material is critical, high, medium or context, and shows how long it takes. The home page gives a reading order, critical topics first.
- **Private facts stay private.** A fact from a private source sits in a closed block that search never shows.
- **Reference pages.** A glossary, every visual with its purpose, the open questions, and all materials by rank.
- **Your notes.** Read marks, bookmarks, notes and to-dos, kept in your browser.
- **Light and dark themes, phone width and print.**

## How a guide gets built

| Phase | What happens | What you do |
| --- | --- | --- |
| Set-up | The agent interviews you: the reader, the goal, the date and hours, the subject, your situation, your sources | Answer, and drop your sources into `context/sources/` |
| Scaffold | The agent researches your situation and proposes a topic map that fits your hours | Nothing |
| Kickoff | The agent shows its assumptions and the map | Confirm or change them |
| Pilot | One topic per tier, written, checked and built | Read them. Say what to change |
| Waves | Critical topics first, then high, then medium. The portal rebuilds as each finishes | Start reading. Stop the build when you have enough |
| Integration | Tier maps, the home page, the glossary, the open questions, checks across the guide | Nothing |
| Reading | You read, mark and take notes. Fixes go out in batches | Read |

You're needed three times: the set-up interview, the kickoff and the pilot. The pilot comes before the fan-out because your taste in depth, length and visuals shows only when you see a page. In the source build, all three pilot writers filled their size band to the ceiling, and the reader cut the bands after reading them.

## What it costs

Tokens, mostly. In the source build, a topic cost about 320,000 to 400,000 tokens to reach the portal with a batch facts check, and about 480,000 to 650,000 with an independent review. At that rate, a 15-topic guide costs about 5 to 6 million tokens, before the scaffold and integration. The orchestrator logs each run's cost against its projection, so the plan changes before the budget runs out.

## Start

You need [Claude Code](https://claude.com/claude-code) and Python 3.11 or later. Nothing else installs.

```bash
git clone https://github.com/batirko/research-and-learn.git my-guide
```

Open the folder in Claude Code and say what you need to learn, and by when. The set-up skill takes it from there.

To build the portal at any point, run this from the folder, then open `site/index.html`:

```bash
python3 engine/build.py
```

If your `python3` is older than 3.11, call `python3.11` instead.

## What's inside

| Path | What it holds |
| --- | --- |
| `AGENTS.md` | The operating guide for any agent working in the folder |
| `guide.toml` | Your guide's settings: title, tiers, part headings, sizes, limits, tags, accent colour |
| `docs/` | The method on one page, the standards, your request and the decision log |
| `context/` | What is known about you, your goal and your situation, with your frozen sources |
| `curriculum/topic-map.md` | What gets built and why |
| `orchestration/` | The orchestrator's playbook, the worker briefs, the board and the handoffs |
| `content/` | The topics, by tier |
| `engine/` | The build, its eight checks, the format check, the styles and the scripts |
| `tools/` | The lint and the private-term scan |
| `.claude/skills/` | Set-up, scaffold, and a pass that removes AI-sounding prose |

Everything under `context/`, `curriculum/`, `content/` and `orchestration/` starts as a template with instructions. The set-up and the scaffold fill them, and your copy becomes your project. To upgrade, copy `engine/` and `tools/` from a newer release: nothing you write lives there. If a portal worker changed the engine for your guide, the decision log says what, so the change can be made again after the upgrade.

## The parts worth taking even if you build guides another way

**The explanation carries the knowledge.** Materials are for depth, and a long list is a failure of selection. Critical materials are capped per topic and per guide, and each says what it gives that the guide can't.

**Rank everything.** Topics, sections and materials share one four-level scale. A reader who knows a section is context can skip it without guilt.

**Evidence and interpretation stay apart.** Every fact about your situation carries a tag that says where it came from. An unknown becomes an open question with its likely answers, never a guess written as fact.

**A visual earns its place.** It needs a one-sentence job, written before drawing, and a subject with a shape. Most topics have none.

**One word and one home per concept.** The glossary bans the synonyms, and the topic map names the one topic that explains each shared idea.

**The pilot before the fan-out.** Three topics, read by you, before forty more get written to the wrong length.

## Before you share a portal

A built portal holds the text of every private block, closed but present. Before you send it to anyone, scan it against a list of the names and phrases that must not leave your machine:

```bash
python3 tools/scan.py files site/ --terms ~/path/to/your-private-terms.txt
```

The list lives outside the folder, so the list itself never gets shared. `engine/core/terms.py` describes its format.

## Credits

The slop pass in `.claude/skills/no-ai-slop/` is [no-ai-slop](https://github.com/petergyang/no-ai-slop) by Peter Yang, under the MIT licence.

## Licence

[MIT](LICENSE).
