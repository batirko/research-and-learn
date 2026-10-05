# The portal's design

`assets/tokens.css` holds the values, and this page says why they are what they are. A guide owner changes the accent through `portal.accent_hue` in `guide.toml`. Everything else here holds for every guide.

## What the design is for

A reader goes through a long guide in a few weeks, mostly on a laptop, against a date. Two questions drive every page: what to read next, and how much it matters. So the design serves long reading first and rank second, and everything else stays quiet.

## Type

| Role | Family | Why |
| --- | --- | --- |
| Body | Charter, then Iowan Old Style, Cambria, Noto Serif, Georgia | A sturdy reading serif with a large x-height, calm over long stretches |
| Headings and interface | Avenir Next, then Segoe UI, Noto Sans, Ubuntu, Cantarell, Arial | A humanist sans that contrasts clearly with the body |
| Mono | SF Mono, then Menlo, Cascadia Mono, Consolas, DejaVu Sans Mono | IDs, provenance tags, times |

Every family lists fonts that ship with macOS, Windows and common Linux desktops, so nothing loads from the network.

- Body text is 17 pixels with a line height of 1.6 and a measure of 68 characters.
- Headings are bold, roman and in sentence case.
- Dark mode drops the body weight a little, to offset light text on dark paper.

## Colour

- **The paper is white.** Internal reading pages use a white background, never a cream or paper tint.
- **The greys are neutral.** Panels, rules and secondary text have no hue at all, so a warm accent never tints the page.
- **One accent.** It carries links, the focus ring, the critical rank and the one point of each visual, and it stays under about 5% of any screen. Its hue comes from the settings; its lightness and chroma are fixed, so the contrast holds at any hue.
- **Dark mode** uses neutral dark greys. The accent keeps its hue and gains lightness.
- **The favicon** is the wordmark's square in the accent colour. The build inlines it in every page as a data URI, so it follows `portal.accent_hue` and loads from nowhere.

Contrast, as WCAG ratios, computed on 2026-10-05:

| Token | On white | On dark paper |
| --- | --- | --- |
| `--color-ink` | 17.7 | 16.0 |
| `--color-muted` | 8.5 | 9.9 |
| `--color-neutral` | 5.1 | 6.6 |
| `--color-accent` | 6.9 at hue 255, at least 5.7 at any hue | 8.3 at hue 255, at least 7.8 at any hue |

## Rank

Rank is the portal's main signal, so it uses one hue at four weights. A reader can tell the ranks apart in greyscale and in print.

| Rank | Mark |
| --- | --- |
| Critical | Solid accent, light text |
| High | Accent outline, accent text |
| Medium | Grey outline, grey text |
| Context | Dashed light outline, light grey text |

A context section also gets a dashed left rule and lighter text, so a reader sees at a glance what they can skip. A button in the contents hides every context section, and the choice persists.

## Private facts

A private block never uses the accent. It is neutral: a hatched left rule, a grey panel, and a label that reads "Private" with the block's own label after it. It starts closed.

The colour doesn't protect anything; the closing does. That's why every private fact sits in a block.

- A closed block that holds a visual shows the visual's number and title, so a reader sees a figure is inside. The title is public by the format's rule.
- "Open all private facts" sits under a page's title when the page has a private block. The portal doesn't remember it: every page opens with its private facts closed, because the closing exists for the shared screen.
- Search finds a block by its label and its visuals' titles only.
- A copy built to share replaces each block with a closed stub in the same grey: the "Private" mark, the label, the visuals' titles, and "Left out of this copy". It can't be opened, because nothing is inside.

## Provenance tags

Tags are small mono text in brackets, in a grey. Private tags are darker, so they stand out in an opened block. `[inference]` and `[unverified]` get a dotted underline, because they mark the guide's own reasoning or a weak source.

## Visuals

Visuals use the classes in `assets/visuals.css`, which read the same tokens, so every visual follows the theme without colours of its own. Grey areas carry the structure, the accent carries the one point, and a dashed outline carries what nobody knows. `format.md` lists the classes.

## Structure

Every topic in the topic map has a page. A written topic shows its text. A planned topic shows its entry in the map, marked "Not written yet", so no link breaks and the owner can review the plan where they read.

- **The masthead** holds the tiers, then the indexes, a search box and the theme switch.
- **The home page** opens with its own text at reading width, then the reading order, the tiers and the time totals at full width. The numbers never sit in the text, so they can't drift.
- **A tier's page** opens with the owner's definition of the tier, then its map, then its topics by group, with rank filters.
- **A topic's page** is a long document. On a wide screen it has three columns: the tier's topics, the text at 68 characters, and the contents. Narrower screens drop the topics first, then fold the contents into a closed box under the title.
- **The open-questions page** is a document at reading width. A link to a question lands on its band, washed in the accent.

## Notes

A reader can bookmark a section or a selected sentence, add a note or a to-do to it, and add to-dos tied to no page. Everything stays in the browser. The notes page lists it all by page, with filters, and can download a copy and load one back. A note whose sentence changed in a rebuild stays on the notes page with a flag.

## Print

A page prints what the reader sees, in the light theme, whatever theme is on screen.

- Navigation, contents and buttons don't print.
- A closed private block prints its summary and "Closed, so not printed". A note under the title counts what the copy leaves out, because a printout can leave the room.
- Headings stay with what follows, and visuals, materials and glossary rows don't split across pages.
- A material's link prints after its title.

## Motion

Almost none. Opening and closing a private block is the only motion, and it stops under `prefers-reduced-motion`.
