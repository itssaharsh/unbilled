# How we used AO (Agent Orchestrator)

Every product commit in this repository was made by an AO session spawned from a committed prompt in `prompts/`. This VS Code Claude Code session wrote the plan, `prompts/`, `evals/PREREGISTRATION.md`, and these docs, and reviewed diffs; it wrote no product code.

## Session table (orchestrator appends a row after each merge)

| # | Session name | Kind / harness | Prompt file | What it built | PR | Acceptance test | AO routed back |
|---|---|---|---|---|---|---|---|
| 1 | unbilled-orch | orchestrator / claude-code (chat) | prompts/00-ORCHESTRATOR.md | contracts scaffold, merges, gates | | `make test` | |

## Evidence captured for the video
- Board screenshots: `docs/screenshots/ao-board-<HHMM>.png` (every ~90 min).
- `ao session ls --all --include-terminated` output at freeze: `docs/ao-sessions.txt`.
- `git branch -r | grep ao/` at freeze: `docs/ao-branches.txt`.
- Reviewer session on the validator PR: see PR comments.

## What AO changed about the build
(Orchestrator fills in: parallelism achieved, conflicts avoided by file ownership, anything lifecycle automation routed back — CI failures, review comments, merge conflicts — only if it actually happened.)
