# w09-eval-sweep — pre-registration, the sweep, grading, and the numbers

**Role.** You produce the evidence: commit the pre-registration first, run the sweep, grade derived metrics and rule-discovery fidelity against the sealed world, and hand the orchestrator the numbers for the README and video. Read `prompts/CONTRACTS.md` §2, §8, §9, §11 and `evals/PREREGISTRATION.md` (fill any TBD, commit, note the hash).

**You own:** `evals/` (`PREREGISTRATION.md` edits, `grade.py`, `results.md`), `tests/test_grade.py`, `Makefile` target `grade`. **Do not touch** `unbilled/*` — if the runner has a bug, report it with a minimal repro and let w05 fix it.

**Deliverable.**
1. **Pre-registration:** confirm `evals/PREREGISTRATION.md` states metrics, arms, seeds, materiality, noise floor, canary periods, and the decision rule for "improved" **before** any sweep output exists. Commit; record `git rev-parse HEAD` in `evals/results.md` as the pre-registration hash.
2. **Sweep:** `make sweep` = arm `main` seeds 1,2 over `2026-04..2026-07`, then arm `memory_off` seed 1, then arm `validator_off` seed 1 *only if* the main sweep finished in under 25 minutes. Sized to the account's rate limits: if 429s exceed 10% of calls, restart with `MAX_CONCURRENCY=2`. Record wall-clock and total cost.
3. **`grade.py`:** reads `unbilled.db` + `fixtures/world_truth.json` (allowed here, post-hoc only) and prints a markdown table per arm per close: MAPE, n_scored, precision/recall on negatives, pass@1, pass^2, $/close, seconds, touches, cache hit rate, ledger size, rules added/deprecated/rejected. Adds **rule-discovery fidelity**: for every active `inferred_from_data` rule with a numeric claim (e.g. lag days, run-rate multiplier, rate change), compare to the sealed parameter and mark ok within 15%. Adds the **rejection log** summary (proposed / committed / rolled back with deltas). Writes `evals/results.md` and augments `web/public/data/runs.json` with `rule_discovery` and `summary.notes` (one sentence for any close that regressed and why, if the validator_log explains it).
4. **Honesty block** in `results.md`: which metrics are derived (variance, completeness, cost, latency, touches) vs authored (GL account accuracy), that the sweep's reviewer is the simulated controller, and the 429/retry counts.
5. Commit `web/public/data/*` and `unbilled.db` (small) so the demo runs with no API key.

**Acceptance test:** `python -m pytest tests/test_grade.py -q` (fidelity check on a synthetic rule; MAPE excludes negatives; pending actuals excluded); `make grade` prints the table; `runs.json` validates against the schema in `schemas.py`.

**Constraints.** Do not tune anything after seeing results — if a number is bad, it ships as the honest number; only bugs (crashes, scoring errors) get fixed, and each fix is a commit that says so. Never edit `world_truth.json`.

**Report back:** the results table, the pre-registration hash, total calls / 429s / cost / wall-clock, and the three best rule-discovery examples (rule id, claim, sealed value).

**Time box:** 75 minutes including the sweep.
