# Briefs

A brief is a worker's instructions. The orchestrator writes one per worker from a template here, and one run picture per run. The run picture holds what every worker in the run shares, and every brief points at it.

A brief gives context, not a design. It names the goal and why it matters, the limits that are fixed, the reading, the files the worker owns, the model and the budget. It leaves the approach to the worker. A brief that lists steps caps the worker at the orchestrator's first idea.

## How to use a template

1. Make a folder for the run, such as `orchestration/briefs/run-03/`.
2. Copy `run-picture.md` into it as `picture.md`, and fill it first.
3. Copy a template for each worker, named by kind and scope: `topic-p02.md`, `facts-run-03.md`.
4. Replace everything in `{braces}`. Delete a line that doesn't apply.
5. Always fill the model, the budget, the files the worker owns and the path of the run picture.
6. Start the worker with a prompt that points at its brief. In the lean mode, that's the subagent's prompt. In the full mode, the owner opens a session with it.

Put what all the workers share in the run picture, not in each brief. A brief keeps only what is this worker's own.

## The templates

| Template | For | Filled example |
| --- | --- | --- |
| `run-picture.md` | What every brief in one run shares | `example-run-picture.md` |
| `topic.md` | Researching and writing the topics of one cluster, or one topic | `example-topic.md` |
| `review.md` | An independent review of finished topics, or of the whole guide at integration | `example-review.md` |
| `facts-check.md` | Comparing every tagged claim with its source, for a batch of topics or pages | `example-facts-check.md` |
| `fix.md` | Applying a check's findings to topics | `example-fix.md` |
| `context.md` | Checking and extending the context notes | `example-context.md` |
| `portal.md` | Changing the portal's design or the engine | `example-portal.md` |
| `integration-writer.md` | The tier maps, the home page text and the open-questions page | `example-integration-writer.md` |

A helper gets no template. Its brief is a few lines: the goal, the files it writes, its model and its budget.

## The phases and their briefs

- **Pilot:** a facts check of the context notes, when the guide has a case. Then a topic worker, a review worker and a fix worker per pilot topic. After the owner's review, an integration writer drafts the tier maps.
- **Waves:** topic workers, then a facts check per batch, or review workers, then fix workers. A context worker when a handoff says the context notes don't hold.
- **Integration:** an integration writer; a review worker whose scope is the whole guide; a facts check of the new pages; a fix worker. A portal worker only when the engine needs a change.

## The examples

The examples are filled for the engine's test guide in `engine/tests/fixture/`: a first season keeping bees, for a reader called Sam. They show the shape of a filled brief. Their runs, dates and findings are invented, and the test guide's size bands are smaller than the defaults. Copy the shape, and write your own content.
