# w06-reflector — the Reflector (learning step)

**Role.** Once per close, after actuals have been scored, you turn evidence into **typed delta ops** for the Precedent Ledger. This is the component that makes the agent get better; it runs on the stronger model, once per close (batched), never per vendor. Read `prompts/CONTRACTS.md` §3, §4 (`reflector.py`, `DeltaOp`), §7, and the `precedent_propose` schema in `tools.py`.

**You own:** `unbilled/reflector.py`, `unbilled/prompts/reflector_system.md`, `tests/test_reflector.py`. **Do not touch** `estimator.py`, `precedent.py`, `validator.py`, `run.py`.

**Deliverable — `reflect(period, *, store, llm) -> list[DeltaOp]`.**
- Input assembled from SQLite: for the period just closed — every `estimate` row with `human_action` (approve/edit/reject + reason code + note); every estimate from earlier periods that got `scored_in_period == period` (estimate vs actual, variance, method used, cited rules); tool errors logged in the period (`tool_fact` candidates); the current active rules (`store.always_on(40)` + all vendor-scoped rules touched this period).
- Call the Reflector model with `thinking={"type":"adaptive"}` and a single strict tool `propose_delta_ops(delta_ops: [...])` (`tool_choice` auto + explicit instruction to call it exactly once). The model outputs ≤ 12 ops per close. Each `add` op must carry: `kind` (accrual_method | cutoff_lag | coding | tool_fact), `scope` (`vendor:Vxx` or `global`), `trigger`, `action` (plain English; for accrual_method include a JSON snippet like `{"method":"run_rate","window":3,"multiplier":1.08}`), `rationale` citing bill ids / variance numbers, `source` (`human_correction` when it derives from a reason code; `inferred_from_data` when derived from variance or history patterns; `tool_error`), `provenance`.
- Rules for good ops (put in the system prompt): one behavior per rule; prefer updating an existing rule over adding a near-duplicate; deprecate a rule that led to a `harmful` outcome twice; never encode the exact actual amount as a rule (that's leakage, the Validator will reject it anyway) — encode the *method* and its parameters; `cutoff_lag` rules state a lag in days with the observed sample size; `inferred_from_data` rules must quote the evidence (≥3 observations).
- Post-process: validate each op against `DeltaOp`; drop ops that reference unknown rule ids; cap at 12; return them (the runner calls `store.propose` and the Validator).

**System prompt (`reflector_system.md`, ≤ 50 lines):** you are the senior accountant reviewing the junior's accrual estimates after the fact; explain *why* each estimate was off, generalize into reusable precedents, write them in the controller's voice, and be conservative.

**Acceptance test:** `python -m pytest tests/test_reflector.py -q` with `LLM_PROVIDER=stub` (stub returns a canned `propose_delta_ops` call; test validation, capping, unknown-id dropping, leakage filter that rejects an `action` containing a dollar amount equal to a scored actual). With a real key, after w04+w05 are merged: run `2026-04` then `2026-05`; paste the delta ops from May and confirm May MAPE < Apr MAPE in the PR (gate G2) — if not, iterate on the system prompt within your time box and document what changed.

**Constraints.** CONTRACTS §7 (no temperature/budget_tokens on Sonnet 5 / Opus 5). Log the full reflection input/output to `logs/reflect_<period>.json` (gitignored). Keep the input under ~12k tokens by summarizing history tables.

**Report back:** the ops produced for 2026-05 (ids, kinds, sources), the MAPE before/after, and any prompt changes you made.

**Time box:** 60 minutes.
