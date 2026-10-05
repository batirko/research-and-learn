# Content

The guide's text: the topics, the tier maps, the home page text and the open-questions page. The build reads this folder, `paths.content` in `guide.toml`, and writes the portal from it. `engine/format.md` is the file format for everything here.

## The layout

```
content/
  home.md                          the home page text
  questions.md                     the open-questions page
  base/                            one folder per tier, named by the tier's id
    intro.md                       the tier's map
    b01-how-a-colony-works/        one folder per topic
      topic.md
      fig-brood-timeline.svg       a visual, next to the topic that uses it
  practical/
    p01-inspecting-a-hive/
      topic.md
```

- **A tier's folder** is the tier's `id` from `[[tiers]]` in the settings. The build skips a folder that isn't a tier.
- **A topic's folder** is its ID in lowercase, a hyphen and a short slug of its title. Its ID's letter matches the tier's prefix. The text is always `topic.md`.
- **A visual's `.svg` file** sits in the folder of the topic or tier map that uses it.

## Who writes what, and when

| File | Who writes it | When |
| --- | --- | --- |
| A topic | Its topic worker. A fix worker applies findings to it | In the pilot and the waves |
| `<tier>/intro.md` | The integration writer | A draft right after the pilot, revised at integration |
| `home.md` | The integration writer | At integration |
| `questions.md` | The integration writer | At integration, then whenever an open question changes |

A topic that is in the topic map and has no folder yet still gets a page, built from its entry in the map. So the portal shows the whole plan from the first build.

## The tier maps

`<tier>/intro.md` opens the tier's page: how its topics fit together, in a short text, a table or a visual. Until it exists, the page shows the tier's definition and says a map comes later.

## The home page text

`home.md` says what the guide is, how the ranks work, how to read it, and what private blocks are. The build adds the reading order, the tiers and the totals below it. Until it exists, the home page uses `guide.description` from the settings.

## The open-questions page

`questions.md` is the reader's version of `context/open-questions.md`. Each question opens on its own line, with its ID first. Every question in the context file opens here too: check 3 fails when one is missing. The opening line is public text, so a private fact under a question sits in a private block. `python3 engine/topic.py content/questions.md` lists the questions it finds and any that are missing.

## Checking your file

- A topic: `python3 engine/topic.py content/<tier>/<id>-<slug>`.
- A page without parts: `python3 engine/topic.py content/home.md`, and the same for a tier map or `questions.md`.
- The writing: `python3 tools/lint.py content/`.
- The whole portal: the orchestrator runs `python3 engine/build.py`. Workers don't, because two builds at once collide.
