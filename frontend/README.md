# frontend

Visual explainers, and later the results, for the trust layer. These are plain HTML, CSS and JavaScript files. There is no build step and nothing to install: open a file in a browser. (Decision [0015](../docs/decisions/0015-frontend-plain-html.md).)

| Page | What it shows |
| --- | --- |
| [`big-picture.html`](big-picture.html) | What a Collider-Bench task asks, real data vs simulation, the three tasks, the pipeline, a mistake lab that previews the checker, and where we fit in an LHC analysis |

## Rules

- **One page, one file.** Each `.html` file is self-contained and can also be published as a claude.ai artifact as-is.
- **Artifact format.** Each file starts with `<title>` and `<style>`, with no `<!doctype>`, `<html>` or `<body>` tags; the artifact host adds those.
- **External resources.** Only Google Fonts and pinned CDN scripts (cdnjs). Everything else is inline.
- **Results pages read data, never invent it.** When the checker produces results, `trustlayer.report` will write JSON under `experiments/*/results/`. A results page will read that JSON; numbers are never typed into the HTML.
- **Never put answer-key data on a page meant for the test-subject agent.** These pages are for people. The container never sees this folder.
