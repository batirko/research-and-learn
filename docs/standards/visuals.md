# Standard: visuals

When a topic gets a diagram, chart or figure, and when it doesn't. A **visual** is one such drawing with its **job statement**: one sentence on what the reader gets from it.

Here, "you" is the worker who considers a visual or checks one.

## The rule

A visual earns its place in one of two ways.

- **It adds information** that the text doesn't carry.
- **It explains** something the text does carry, so that a first-time reader understands it faster and more surely.

Nobody owes a topic a visual. Many topics have none. A visual that repeats the text costs the reader time and gives nothing back.

## The test

A visual exists only when it passes all four checks.

**1. It has a job.**
Write the job statement before you draw. It says what the reader understands with this visual that the text next to it gives slower, less surely, or not at all. The statement stays with the visual, and the portal shows it.

**2. A first-time reader is better off with it.**
Read the section as someone new to the subject, once with the visual and once without. If understanding arrives as fast and as surely without it, the visual is redundant.

Restating the text in boxes fails this check. A drawing of a mechanism can pass even when a numbered list could carry the same facts. In the drawing, the reader sees the order, the actors and what passes between them at once.

**3. The subject has a shape.**
At least one of these is true:

- **Topology:** what connects to what, what sits inside what.
- **Actors over time:** a sequence where the order matters, and what passes from one actor to the next.
- **Branches, loops or parallel paths.**
- **State that changes:** before and after, or a life cycle.
- **Quantity:** a distribution, a trend, a curve whose shape is the point.
- **Position in two dimensions:** a map where placement carries the meaning.

**4. It can be drawn truthfully.**
Every box and arrow rests on a fact. If the facts are missing, there is no visual. A drawing of a guess reads as knowledge, and this matters most for the case, where much is unknown.

## Likely to pass

- A timeline of how long a queen, a worker and a drone take to develop, side by side. The race between them is the point.
- A colony's population over a year, as a curve. The shape carries the meaning.
- A decision with branches: what a beekeeper does on finding queen cells, by what else they find.
- A cross-section of a hive: what sits inside what, and where the queen can and can't go.

## Likely to fail

- A list in boxes.
- Icons in a row.
- Pillars, layers or pyramids that restate the headings.
- A wall of product logos.
- A table redrawn as cards.
- A header illustration.
- A drawing that repeats the table above it.

## Unknowns in a visual

When a visual mixes known and unknown parts, draw the unknown parts differently, and say in the caption what the difference means. `engine/format.md` has the classes for it. Never fill a gap with the common answer from elsewhere.

## A visual that shows a claim

When a visual places someone's claim, draw the whole claim. Examples: the months a calendar gives a task, or the area a local rule covers. Read the source to the end of its sentence, and to the end of the list. One phrase lifted from a longer statement draws a smaller claim than the source makes.

## Visuals inside a private block

A visual whose content rests on private facts sits inside a private block. Its title stays public, because the portal shows it on the closed block. So the title names the subject and never states a private fact.

## Borrowed visuals

Some sources hold the best drawing of an idea.

- **Point to it.** "See figure 3 in the linked paper" costs nothing and is always allowed.
- **Embed it** only when its licence allows that, and credit it.
- **Redraw it** in the guide's own form when the idea is factual and the original can't be embedded. Credit the source of the idea in the `credit` field.
- Never hotlink an image, and never copy one without a licence.

## Interactive visuals

Interaction is allowed when it shows something a still image can't, such as stepping through a sequence. A still image is the default. An animation that only decorates fails check 2. Interaction is the portal worker's to build, so propose it in your handoff.

## Making it

- A vector drawing in the page, never a screenshot or an image of text.
- Labels are real text.
- One idea per visual.
- The caption says what to notice. It doesn't describe what is drawn.
- Colours come from the portal's classes, so the visual reads in both themes.

`engine/format.md`, section "Visuals", has the file rules: the fields, the size of the drawing, the classes and the IDs.

## How a reviewer checks

1. Read the job statement, look at the visual, and apply check 2. A visual that fails comes out.
2. Apply check 4: find the fact behind every box and arrow. A shape without a fact is drawn as unknown, or it comes out.
3. In a visual inside a private block, read the title as public text.
4. Ask the opposite question once per topic: is there a passage that's hard to follow, where a visual would do the explaining? If so, propose one, with its job statement.

The portal's visual index lists every visual with its job, so a reviewer can apply the test across the whole guide in one sitting.
