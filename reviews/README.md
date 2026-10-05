# Reviews

The findings of every check: a review of one topic, a facts check, and the check of the whole guide at integration. A fix worker applies them. The portal never shows a review.

## Names

- **A review of one topic:** `reviews/<id>-<slug>.md`, with the topic's ID and slug, such as `reviews/p01-inspecting-a-hive.md`.
- **A facts check:** `reviews/facts-<scope>.md`, where the scope names what it checked, such as `reviews/facts-run-02.md` for one run's topics or `reviews/facts-context-notes.md` for the context notes.
- **The check of the whole guide,** at integration: `reviews/integration.md`.

A second review of the same topic adds a dated section to its file.

## What a review holds

1. **The verdict first:** ready, ready after small fixes, or needs rework, in one sentence.
2. **The findings,** one per item, each with:
   - where: the part and section, or the line;
   - what is wrong, with the evidence;
   - how serious: high when a reader would learn something false or see a private fact, medium when a standard is missed, low for wording;
   - the fix, when it is clear.
3. **What the reviewer couldn't check,** such as a page it couldn't open.

Write findings into the file as you find them, not at the end. A stop then loses nothing.

`docs/standards/topic-page.md` and the other standards each end with "How a reviewer checks".
