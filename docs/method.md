# The method

How a guide gets planned, written, checked and built in this workspace. This page holds the whole method in brief. The five standards in `docs/standards/` hold the detail, and `docs/concept.md` says what the workspace is for.

Here, "you" is the owner: the person who runs the workspace, and often the reader too. Workers read this page as well.

Numbers on this page are settings. Each one names its key in `guide.toml` and gives the default, so a guide that changes a value changes it in one place.

## Who does what

**You** answer the set-up interview, confirm the plan at kickoff and review the pilot. After that, you read.

**The orchestrator** is the agent session that runs the build. It doesn't write topics. It starts workers, writes their briefs, keeps the shared files true and runs git. It brings you a question only when a wrong guess would waste a worker's run. `orchestration/playbook.md` is its manual.

**Workers** each do one job and stop.

| Worker | Its job | Model |
| --- | --- | --- |
| Topic worker | Researches and writes the topics of one cluster | The strongest |
| Review worker | Reads finished topics as the reader would, then checks them against the standards | The strongest |
| Portal worker | Designs the portal and changes the engine | The strongest |
| Context worker | Checks and extends what is known about the case | The strongest |
| Facts check | Compares every tagged claim with its source | A smaller model |
| Fix worker | Applies a check's findings to a topic | The strongest |
| Integration writer | Writes the tier maps, the home page text and the open-questions page, in one voice | The strongest |
| Helper | Finds candidate sources, checks links, runs the lint | A smaller model |

A **cluster** is a set of topics that one topic worker researches together, because they share sources.

Workers coordinate through files:

- **A brief** gives a worker its goal, its limits, its reading and a picture of what the other workers are doing. It gives context and leaves the design to the worker.
- **A handoff** is the file a worker leaves when it finishes: what exists, what it couldn't verify, and what it proposes.
- **The board**, `orchestration/board.md`, holds every topic's status.
- **The decision log**, `docs/decisions.md`, holds every settled question with its reason and what would reverse it.
- **The worker pack**, `orchestration/worker-pack.md`, is the standing reading for every worker.

Two rules keep parallel workers apart. Each worker writes only the files its brief names, and proposes changes to anything else in its handoff. Only the orchestrator runs git, because workers share the workspace and a git command in one can wipe another's files.

**The two modes.** In the lean mode, the default, workers are subagents of the orchestrator. Independent reviews go to the pilot and to the topics that rest most on facts about the case. In the full mode, each worker is its own session and every topic gets a review.

## The phases

| Phase | What happens | What you do | What it leaves |
| --- | --- | --- | --- |
| Set-up | The set-up skill interviews you: the reader, the goal, the date and hours, the subject, the case, your sources, the tiers | Answer, and put your sources in `context/sources/` | `docs/request.md`, `context/reader.md`, the settings |
| Scaffold | The scaffold skill researches the case, writes the context notes and the open questions, and proposes a topic map that fits your hours | Nothing | `context/`, `curriculum/topic-map.md` |
| Kickoff | The orchestrator shows its assumptions and the map | Confirm or change them | The first entries in the decision log |
| Pilot | One topic per tier, written and checked, in a portal that shows them | Read them. Say what to change about depth, length, ranks, materials, visuals and design | Settled standards, a filled worker pack |
| Waves | Critical topics first, then high, then medium. The portal is rebuilt as each topic finishes | Start reading. Stop the build when you have enough | Topics, dossiers, reviews |
| Integration | Tier maps, the home page text, the glossary, the open-questions page, and checks across the whole guide | Nothing | The finished portal |
| Reading | You read, mark and note. Fixes go out in batches | Read | Your notes, in the browser |

You're needed three times: at set-up, at kickoff and at the pilot review.

**The pilot comes before the fan-out.** Your preferences on depth, length and visuals show only when you read a finished topic. So no wave starts before you've read the pilot and answered. A change to a standard then lands once, before the other topics depend on it.

## Tiers

**A tier** is a first-level split of the guide. Set-up defines the tiers in your own words, and the definitions don't change after that. Each topic lives in one tier.

Each tier is a `[[tiers]]` table in the settings. It holds an ID, a name, a one-letter prefix for topic IDs, the tier's question and your definition. The defaults are Base, Practical and Modern.

- **To place a topic,** use the definitions. When a topic fits two tiers, put it where most of its content sits and link to it from the other.
- **A tier that updates the others** (`updates = true`, by default Modern) holds topics that say what today's tools change. Each one names the topics it updates and says whether it covers the problem, the solutions or both.
- **A tier whose facts age fast** (`fast = true`, by default Modern) dates its facts and its materials more closely.

## Ranks

Topics, sections and materials carry one of four ranks. The keys are fixed, because the file format uses them. The words are yours, in `[ranks.*]`; the table gives the defaults in brief.

| Rank | A topic or section | A material, and what the reader does with it |
| --- | --- | --- |
| **Critical** | The reader can't reach the goal without it | Reads or watches it in full. It gives something the guide can't |
| **High** | Needed to follow the core of the subject | Skims it, 10 to 15 minutes |
| **Medium** | Useful background that helps with other topics | Skims it faster, about 5 minutes |
| **Context** | Orientation and completeness | Opens it when needed |

The topic map sets each topic's rank. No section ranks above its topic. We recommend that critical topics stay near a third of the guide: when everything is critical, the rank stops telling the reader where to start.

Critical materials are capped. A topic has at most `materials.critical_per_topic` (1), or `materials.critical_per_critical_topic` (2) when the topic itself is critical. The guide has at most `materials.critical_in_guide` (30), shared out as a quota per cluster. Each one states what it gives that the guide doesn't, and how long it takes.

## A topic

**A topic** is one page of the guide. It has nine parts, in this order:

1. **The header:** tier, rank, size, depth, the topics to read first, and the date the facts were checked. The build adds the reading time.
2. **Why it matters for your goal,** with evidence.
3. **The short version:** a few lines the reader can keep in their head, 5 to 8 by default (`limits.short_lines`).
4. **The explanation,** from the ground up, in ranked sections. Each concept closes with what it means for the goal.
5. **The case part:** what is known about the case, with tags; what is unknown, as open questions; what to look at first. Only when the guide has a case.
6. **Positions,** where practitioners disagree and the reader will have to take a side.
7. **Materials:** at least one, ranked.
8. **Not verified:** what the writer couldn't confirm. Always present, even when empty.
9. **Check yourself:** up to `limits.check_questions` (5) questions. Optional.

**Depth has three levels.** At level 1, the reader can explain the concept in two sentences. At level 2, they can name the alternatives and why someone picks one. At level 3, they can say what a choice costs, where it breaks, and what would change their mind. A topic's rank sets the depth it reaches.

**Size comes in bands,** set in `[sizes]`. By default, S is 800 to 1,500 words, M is 1,500 to 2,500, and L is 2,500 to 3,500. XL, 3,500 to 4,500, is an exception the orchestrator grants in a brief, at most `sizes.xl_allowed` (5) in the guide. A topic that needs more is two topics.

`docs/standards/topic-page.md` has the full standard. `engine/format.md` is the file format.

## Visuals

**A visual** is a diagram, chart or figure, with a one-sentence job statement. It exists only when it passes four checks:

1. **It has a job.** One sentence, written before drawing, says what the reader gets from it that the text gives slower or not at all.
2. **A first-time reader is better off with it.** Restating the text in boxes fails.
3. **The subject has a shape:** topology, actors over time, branches, changing state, quantity, or position in two dimensions.
4. **It can be drawn truthfully.** Unknown parts are drawn differently. A drawing of a guess reads as knowledge.

Many topics have no visual. The portal's visual index shows each one with its job, so a reviewer can apply the test. `docs/standards/visuals.md` has the detail.

## Evidence

- **Every source is opened by the session that cites it.** A link from memory or a search snippet doesn't count.
- **Every fact about the case carries a provenance tag** that says where it came from: `[public]`, `[source: name]`, `[private: name]`, `[inference]` or `[unverified]` by default. `context/README.md` explains them, and `[[tags]]` in the settings can add more.
- **Evidence and interpretation stay apart.** The context notes are a first reading, made before anyone knew the case well. When research contradicts them, the evidence wins, and the worker says so.
- **Several explanations get weighed together.** When your sources give several explanations for the same thing, a topic weighs all of them. It doesn't pick one before the evidence does.
- **Unknowns become open questions,** each with an ID such as OQ-03, its likely answers and what would settle it. They become a page the reader takes into the case.
- **Nobody guesses about the case.** "Your association probably lends extractors" is a defect. "Whether your association lends extractors is unknown; ask the secretary before you buy one" is fine.
- **Your sources are frozen.** Nobody edits them. When a worker finds an error in one, the correction goes into the worker pack, so every later worker sees it.

`docs/standards/sources.md` covers finding, checking and ranking sources.

## Privacy

Three layers keep private facts where they belong.

1. **A private block** holds a fact from a private source. The portal shows it collapsed, and search leaves it out. Its label and the titles of any visuals inside it are public text, because a closed block shows them.
2. **The never-publish list,** `context/never-publish.md`, names what must never reach the portal, even collapsed. The build fails if one appears.
3. **A copy to share** leaves out every private block: `python3 engine/build.py --share`. The private-term scan then checks it against a list you keep outside the workspace, before the copy goes to anyone.

No script catches a private fact restated in other words. So the writer and the reviewer each search the public text for one. A collapsed block only hides text from a glance. Anyone who has the files can open every block, including anyone you send the portal to.

## Words

- **One word per concept,** across the whole guide. `context/glossary.md` holds the list, and the lint flags the words it bans.
- **One home per concept.** When several topics touch a concept, the topic map names the topic that explains it: the concept's home. The others link to it and add only what is theirs.
- **Plain writing:** one idea per sentence, active voice, exact words for certainty, and a slop pass before every handoff. `docs/standards/writing.md` has the rules.

## When documents disagree

The higher one wins:

1. `docs/request.md`: your own words.
2. `docs/decisions.md`: what you've confirmed since.
3. `docs/standards/`, with the values in `guide.toml`.
4. `curriculum/topic-map.md`.
5. `orchestration/worker-pack.md`.
6. The worker's brief.

A worker that finds a conflict follows the higher document and says so in its handoff. The orchestrator settles it, and a change gets an entry in the decision log.

## Rules from experience

Each of these cost a run to learn.

1. **Writers fill a size band to its ceiling.** So briefs say: aim at the middle. A fix to a topic at its ceiling cuts before it adds.
2. **Writers judge critical materials one cluster at a time and pick too few.** So integration includes one pass that compares the strongest materials across the whole guide.
3. **Context notes written before research hold errors.** One check found 17 wrong or overstated claims among 176. So the facts check runs on every topic that rests on the case, and checking effort goes where a wrong fact costs most.
4. **A subagent can't start subagents of its own.** In the lean mode, a topic worker does its own research.
5. **A session that can't reach the web writes from memory.** So a researcher fetches one page it needs before it starts, and stops if the fetch fails.
6. **An unattended run stops at the first permission prompt, and a usage limit can stop five workers at once.** So the orchestrator commits at every quiet point, and says at kickoff whether the session can work alone.
7. **A cost projection made before any topic is written can be far off.** So the orchestrator logs each run's cost and compares it with the projection, and the plan changes before the budget runs out.

## Where the detail lives

| File | Read it when |
| --- | --- |
| `docs/request.md` | You need the original request, the goal, or the assumptions confirmed at kickoff |
| `docs/decisions.md` | You're about to reopen something that looks settled |
| `docs/standards/topic-page.md` | You write or review a topic |
| `docs/standards/sources.md` | You pick, check, rank or cite a source |
| `docs/standards/visuals.md` | You consider a visual |
| `docs/standards/writing.md` | You write a sentence the reader will see |
| `docs/standards/portal.md` | You change the portal, or check one before sharing it |
| `engine/format.md` | You write a topic file, a tier map, the home page text or the open-questions page |
| `context/README.md` | You need a fact about the reader or the case |
| `curriculum/topic-map.md` | You need to know what a topic sets out to answer, and which topic is a concept's home |
| `orchestration/worker-pack.md` | You're a worker |
| `orchestration/playbook.md` | You're the orchestrator |
