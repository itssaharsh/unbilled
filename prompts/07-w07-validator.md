# w07-validator — admission gate for memory writes

**Role.** You build the component that makes the learning claim falsifiable: before a candidate Precedent Ledger is committed, replay it on two already-closed canary periods with known actuals and commit only if it measurably beats the incumbent. Read `prompts/CONTRACTS.md` §3 (`validator_log`), §4 (`validator.py`, `PrecedentStore.snapshot/restore`), §7.

**You own:** `unbilled/validator.py`, `tests/test_validator.py`. **Do not touch** `precedent.py`, `estimator.py`, `run.py` (if `run.py` needs a hook, describe it in the PR; w05 owns it).

**Deliverable — `evaluate(candidate_snapshot, incumbent_snapshot, *, llm, ledger, store) -> ValidatorResult`.**
1. For each snapshot: `store.restore(snapshot)`; for each canary period in `CANARY_PERIODS = ["2026-02","2026-03"]` and each accrual-relevant vendor (skip vendors with no truth row that period), call `estimator.decide(..., memory_on=True, temperature=0.0, seed=0)` **without posting or escalating** (pass a no-op ledger wrapper so `close_post_accrual` records but does not write), collect `amount`, `should_accrue`, cost.
2. Score against actuals that are *already known at the canary's close+1* (read from the `estimate`/bills data via the ledger, not from `world_truth.json`): MAPE over positives, precision/recall over negatives, total cost.
3. Decision: `commit` iff `mape_candidate <= mape_incumbent - NOISE_FLOOR_PTS/100` **and** `cost_candidate <= COST_TOLERANCE * cost_incumbent` **and** recall did not drop by more than 0.1; else `rollback`.
4. On `commit`: leave the candidate restored; set `canary_delta` on every rule added/updated by the ops. On `rollback`: `store.restore(incumbent_snapshot)`, then re-insert the candidate's new rules with `status="rejected"` and `canary_delta` (so the UI can show *REJECTED · rolled back · +0.04 MAPE*). Always write a `validator_log` row with both scores and the ops evaluated.
5. Cache the canary replay of the incumbent per snapshot id (in-memory dict + `validator_log`) so repeated evaluations don't re-spend.

**Cost guard.** 2 periods × ≤8 vendors × 2 snapshots = ≤32 `decide()` calls per evaluation; use `MAX_CONCURRENCY`. If the run's arm is `validator_off`, `run.py` skips you entirely (nothing to do here).

**Acceptance test:** `python -m pytest tests/test_validator.py -q` with `LLM_PROVIDER=stub` where the stub's `decide()` output depends on which rules are present: one test where the candidate improves (commit), one where it regresses (rollback restores the incumbent byte-for-byte and marks the new rules `rejected` with a delta), one where cost balloons (rollback despite better MAPE). With a real key after w04/w05/w06: run Apr→May and paste the `validator_log` row.

**Constraints.** Deterministic: temperature 0, fixed vendor order, no randomness. Never read `world_truth.json`. Keep under ~200 lines.

**Report back:** the decision rule as implemented, the May validator_log row (real model), and how long one evaluation takes.

**Time box:** 60 minutes.
