# REVIEW — reviewer-session prompt for the validator PR (`ao review trigger`)

You are reviewing the PR that implements `unbilled/validator.py`, the admission gate that decides whether a candidate Precedent Ledger is committed. This code produces the project's headline evidence, so a silent bug here fakes the whole result. Read `prompts/CONTRACTS.md` §4 (`validator.py`, `PrecedentStore.snapshot/restore`) and §11, then the diff.

Check, in this order, and cite file:line for every finding:
1. **Leakage:** does any code path read `fixtures/world_truth.json` or the simulated controller? (Must not.) Are canary actuals taken only from bills visible at the canary period's close+1?
2. **Determinism:** temperature 0 on replays; fixed vendor ordering; no randomness; the same snapshot evaluated twice yields identical scores.
3. **Decision rule:** commit iff `mape_candidate <= mape_incumbent - 0.02` and `cost_candidate <= 1.1 * cost_incumbent` and recall drop ≤ 0.1. Off-by-sign errors and percent-vs-fraction mixups are the classic bug — verify with the tests' numbers.
4. **Rollback correctness:** after rollback the store equals the incumbent snapshot byte-for-byte, and the candidate's new rules exist with `status='rejected'` and a populated `canary_delta`.
5. **Cost guard:** ≤32 model calls per evaluation; the incumbent replay is cached per snapshot id.
6. **Logging:** exactly one `validator_log` row per evaluation with both scores and the ops.
7. **Tests:** do the three required scenarios (commit / rollback / cost-balloon rollback) actually assert the store state, or only the return value?

Output: a ranked list of findings (blocking / should-fix / nit), each with a concrete fix, then a one-line verdict: approve or request changes.
