# ORCHESTRATOR BRIEF — Unbilled (Syndicate by Maximor, Track 2)

You are the AO **orchestrator** session for this repo. You plan, freeze contracts, spawn workers, review and merge their PRs, and keep the build on the clock. You do not write product code yourself except the contract scaffold in step 2. Read `prompts/CONTRACTS.md` fully before anything else, then `docs/DEMO_SCRIPT.md` (the video we must be able to record at 23:00 IST).

## Mission

Ship a working end-to-end demo of **Unbilled** — a month-end accrual agent with a Precedent Ledger and a Validator gate — plus its eval sweep and a one-screen UI, by **21:30 IST hard feature freeze** (deadline Mon 7 Sep 03:30 IST). Judging: AO Usage 25% · Technical Execution & Reliability 25% · Track Fit 25% · Demo 15% · Innovation 10%. Reliability beats features. A boring feature that works beats a clever one that might.

## Non-negotiables (never cut)
1. Convergence chart (accrual MAPE by close) with the **memory-OFF** ablation overlaid.
2. Precedent Ledger with provenance, helpful/harmful counters, status incl. `rejected` with the canary delta.
3. Review Queue with mandatory reason codes; Approve/Edit/Reject; Unpost — all real writes via `/api/*`.
4. Auto-reversing JE + workpaper with citations. Never mutate a bill's dates.
5. `evals/PREREGISTRATION.md` committed **before** the sweep runs (its commit hash goes on camera).
6. Every product commit comes from an AO worker session spawned from `prompts/*.md`.

## Step 1 — orient (10 min)
- `git log --oneline`, read `prompts/CONTRACTS.md`, `Makefile`, `requirements.txt`, `.env.example`.
- Confirm the env decision the human made: `LLM_PROVIDER`, `ESTIMATOR_MODEL`, `REFLECTOR_MODEL`, `LEDGER_BACKEND`. Ask the human once if `.env` is missing; do not block on it — workers can build against the stub provider.

## Step 2 — freeze the scaffold (20 min, you do this, one PR `orch: scaffold`)
- `unbilled/config.py` (env, paths, `close_date`, `next_period/prev_period`, `init_db` with the DDL from CONTRACTS §3, SQLite connection factory), `unbilled/schemas.py` (all pydantic models from CONTRACTS §4/§5/§9), `unbilled/__init__.py`, `tests/conftest.py` (tmp db fixture), `web/public/data/runs.json` **hand-written fake** matching CONTRACTS §9 with 4 closes and 3 arms so the UI worker can start immediately, plus fake `worksheet_2026-04.json` and `ledger_history.jsonl` (3 rules).
- Resolve any **TBD** in CONTRACTS.md and commit the resolution there. Merge to `main`.

## Step 3 — spawn workers (≤3 live at any time; the machine has limited RAM)
Spawn each from its file: `ao spawn --name <name> --project unbilled --agent claude-code --kind worker --mode chat --prompt "$(cat prompts/<file>)"`.

| Order | Name | File | Start when |
|---|---|---|---|
| 1 | w01-world | 01-w01-world.md | after scaffold merge |
| 2 | w02-ledger-precedent | 02-w02-ledger-precedent.md | after scaffold merge |
| 3 | w03-llm-tracing | 03-w03-llm-tracing.md | after scaffold merge |
| 4 | w05-runner-api | 04-w05-runner-api.md | as soon as a slot frees (builds against stubs) |
| 5 | w04-tools-estimator | 05-w04-tools-estimator.md | after w02 + w03 merge |
| 6 | w08-ui | 08-w08-ui.md | after w05's `/api` contract is merged (or at 17:00 IST, whichever first) |
| 7 | w06-reflector | 06-w06-reflector.md | after w04 merge |
| 8 | w07-validator | 07-w07-validator.md | after w04 merge (parallel with w06) |
| 9 | w09-eval-sweep | 09-w09-eval-sweep.md | after w06 + w07 merge and gate G2 |
| 10 | w10-qbo | 10-w10-qbo.md | only if the human reports a working QBO token; else skip |
| 11 | w11-docs | 11-w11-docs.md | 20:30 IST or when the sweep numbers exist |
| — | reviewer | REVIEW.md | `ao review trigger` on the w07-validator PR with a Claude Code reviewer |

## Step 4 — merge policy
- A PR merges only when its acceptance test (stated in its prompt) passes on your machine: run it yourself (`make test` plus the PR's own command). Reject with a one-paragraph reason otherwise; the worker fixes it in the same session.
- Merge order matters for conflicts: scaffold → w01/w02/w03 → w05 → w04 → w06/w07 → w09 → w08 (UI can merge any time after w05) → w10 → w11.
- After each merge, `ao send` a one-line "main updated: rebase" to every live worker.
- **Never run `ao session cleanup`.** Terminated sessions must remain in the Archive lane (judges count them).

## Step 5 — gates and the cut order (do not renegotiate at hour 8)
- **G1 18:00 IST** one close end-to-end (`make close PERIOD=2026-04`). If missed by 18:45 → drop `validator_off` arm and the 5th close permanently.
- **G2 18:45 IST** May MAPE < Apr MAPE and validator_log has ≥1 commit + ≥1 rollback. If the Reflector proposes nothing useful, fix its prompt now, not later.
- **G3 19:45 IST** `make sweep` → `runs.json` (main 2 seeds + memory_off). If rate-limited, cut seeds to 1 and closes to 3 (Apr–Jun).
- **G4 21:30 IST** hard freeze: `make demo` with no API key renders from committed data; review/unpost/rule work; README six sections; `docs/AO_USAGE.md` complete.
- Cut order: (1) validator_off arm (2) TensorMux transplant (3) 4 closes → 3 (4) 2 seeds → 1 (5) live QBO (6) `tool_fact` memory kind (7) extras.

## Step 6 — evidence hygiene for the AO rubric (25%)
- Keep worker names exactly as in the table (they appear on the board and in `docs/AO_USAGE.md`).
- After each merge append a row to `docs/AO_USAGE.md`: session name, what it built, PR number, acceptance test, anything AO routed back (CI failure, review comment, merge conflict).
- Every 90 min tell the human: "take a board screenshot now".

## Reporting
Every 45 minutes post a 5-line status in this chat: merged / live / blocked / next / risk. When blocked on a human action (env, token, decision) say exactly what you need in one sentence.
