# CLAUDE.md

## What this repo is

This repository is a **test bed for experimenting with Greptile**, an AI
code-review tool that reviews GitHub pull requests. The application itself (a
small FastAPI URL shortener) exists only to give Greptile real, multi-file
code to review.

## Important rules for working here

- **Intentional bugs are expected on feature branches.** Experiment PRs will
  deliberately introduce bugs, smells, or questionable patterns so we can see
  what Greptile catches.
- **Do NOT fix, refactor, or "clean up" planted issues** unless I explicitly
  ask you to. If you notice something that looks like a bug on a feature
  branch, assume it is intentional and leave it alone. You may mention it, but
  do not change it without explicit instruction.
- **`main` is the clean baseline.** It should stay correct and well-formed.
  Intentional problems live only on feature branches, never on `main`.

## Workflow for experiments

- Every experiment PR should be **small and focused** — ideally one planted
  issue (or one tightly-related cluster) per PR so the review signal is clear.
- **Always branch off `main`.** Each experiment gets its own branch; open the
  PR from that branch into `main`.
- Keep `main` green: do not merge experimental/buggy branches unless that is
  the explicit goal of the experiment.

## Project structure

See [`README.md`](./README.md) for the application layout, setup, and API.
