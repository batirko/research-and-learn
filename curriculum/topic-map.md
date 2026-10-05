# The topic map

What the guide will hold, and why: every topic with its tier, rank, size and cluster, the home of each shared concept, and the reading order. The build reads this file for every topic's ID, title, tier, group, rank, size and cluster. The board, `orchestration/board.md`, tracks each topic's status.

Status: template, not filled yet.

The scaffold proposes the map before any research, and the owner reviews it at kickoff. After that, only the orchestrator changes it, and each change gets an entry in the decision log. A topic worker that finds an entry wrong says so in its handoff: the scope, the rank, a question, or whether it's one topic or two.

> **To fill this file.** The scaffold fills each section below in order and deletes each "To fill" note when its section is done. Then it changes the status line to "Status: proposed by the scaffold on YYYY-MM-DD." At kickoff, the orchestrator adds "Confirmed at kickoff on YYYY-MM-DD." `engine/format.md`, section "The topic map", has the exact shape the build reads, and `engine/tests/fixture/curriculum/topic-map.md` is a small filled map. After every change, run `python3 engine/build.py` to check that the map still builds.

## How to read an entry

Each topic is a `###` heading with its ID and title, such as `### P01 Inspecting a hive`.

- **The line under the title:** rank, size and cluster, then any markers, each after a `|`. The markers are `read first` for a topic to read before all others, `after B01` for its prerequisites, `updates B01, P01` in a tier that updates others, `facts age fast`, and `pilot`. The words come from `[map]` in `guide.toml`.
- **Why:** the evidence that this topic belongs, tied to the goal in `context/reader.md`.
- **Starting questions:** what the topic sets out to answer. They were written before research. A topic worker answers them, or replaces one and says why in its handoff.
- **Seeds:** leads for research. Nobody has checked them. Open each one before you rely on it, and expect to find better ones.
- **Visual:** a first guess at whether a visual would pass `docs/standards/visuals.md`, and what its job would be. The topic worker decides.
- **Prior art:** earlier text worth reusing, from `reference/` or the sources. Optional.

Until a topic is written, the portal gives it a page built from its entry. So an entry is public text. A sentence with a private tag shows there in a closed private block, and nothing on the never-publish list goes in the map.

An example entry, from a guide on a first season keeping bees:

```markdown
### P02 Swarm control
High | M | C2 | after P01

**Why:** Sam's goal includes a first honey harvest, and a colony that swarms leaves with about half its workers [source: club-handbook p. 12].

**Starting questions:**
1. Why does a colony swarm, and which signs come first?
2. What can a beekeeper do once queen cells appear, and what does each choice cost?

**Seeds:** The association's swarm leaflet. A beekeeping course's notes on swarm control.

**Visual:** Likely. A decision with branches: what to do on finding queen cells, by what else the inspection finds.
```

## The shape

> **To fill:** one row per tier, and a total. Count words at the middle of each topic's size band. Hours are words divided by `sizes.words_per_minute` (220), divided by 60. Under the table, add the time the materials take at their limits, and compare the sum with the reading hours in `docs/request.md`. The scaffold skill's "Size the map to the hours" says how to count the materials and what to cut first when the map doesn't fit. Say here what was cut. We recommend that critical topics stay near a third of the guide.

| Tier | Topics | Critical | High | Medium | Context | Words, about | Hours, about |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Base | | | | | | | |
| Practical | | | | | | | |
| Modern | | | | | | | |
| **Total** | | | | | | | |

## Clusters

A cluster is a set of topics that one topic worker researches together, because they share sources. Its quota is the number of critical materials the cluster can propose. The quotas add up to `materials.critical_in_guide` (30) at most.

> **To fill:** one row per cluster, such as `| C1 | B01, B02 | The colony | 2 |`. The build reads the quota from the last column. A cluster ID is `map.cluster_prefix` (C) and a number. Keep each cluster small enough for one worker's run.

| Cluster | Topics | Theme | Quota |
| --- | --- | --- | --- |

## One home per concept

Several topics touch the same concept. Each concept has one home, which explains it. The other topics link to the home and add only what is theirs. Workers can't see each other's drafts, so this table is what keeps two topics from explaining one concept twice.

> **To fill:** one row per concept that two or more topics touch. The concept's row in `context/glossary.md` names the same home.

| Concept | Home | Also touched by |
| --- | --- | --- |

## Reading order

> **To fill:** a numbered list, critical topics first, each after the topics it depends on. Add a high topic when a critical one depends on it. Each line names topic IDs, then a colon and a note, such as `1. B01, P01: how a colony works, then how to look inside one.` The home page shows this list. The other high topics follow it, then the medium ones, so the list doesn't need to name them.

## The pilot

> **To fill:** one topic per tier, and what each one tests. Pick each to test a risk. A topic that rests on facts about the case tests provenance and privacy. A visual of something partly unknown tests the visual rules. A critical topic tests depth, and a topic in a fast tier tests dates. Mark each pilot topic `pilot` on the line under its title.

Pilot topics are written before their prerequisites exist. They stand alone for the pilot and gain their links later.

> **To fill the tiers.** Each `#` heading below is a tier's `name` from `[[tiers]]` in `guide.toml`, in the same order. When set-up changes the tiers, change these headings to match. Under each tier heading, add `##` group headings, and put the topic entries under them. Topic IDs use the tier's prefix and two digits, numbered in order within the tier. Leave nothing else directly under a tier heading. There, a line in italics replaces the tier's question from the settings, and a plain line replaces its definition. The settings then stop being their one home.

# Base

# Practical

# Modern
