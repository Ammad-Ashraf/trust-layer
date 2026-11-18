# 0015 — Frontend: plain HTML, CSS and JavaScript

- **Status:** decided
- **Date:** 2026-11-18

## Question

Ammad wants a `frontend/` folder with visual explainers now, and visualizations of checker results later. Should we use React or plain HTML, CSS and JavaScript?

## Options

| Option | Good | Bad |
| --- | --- | --- |
| A. Plain HTML/CSS/JS, one self-contained file per page | Opens by double-click; no Node, no build, nothing to break; each file publishes as a claude.ai artifact as-is | Some repetition between pages |
| B. React app (Vite) | Shared components; scales to a big app | Needs Node, a build and dependency updates on the Windows laptop; adds CI work; more than a few explainer and results pages need |

## Decision

A. Decided by Claude (Ammad said "it's up to you"). The pages are explainers and a few results views, not an app. Interactivity and animation work fine in plain JavaScript and canvas, and Phase 1 time goes to the checker. Revisit if the frontend grows past about five pages with shared state.
