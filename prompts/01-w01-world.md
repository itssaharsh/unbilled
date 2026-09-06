# w01-world — sealed synthetic world generator

**Role.** You build the deterministic "world" that every other component consumes: a small company's vendors, chart of accounts, purchase orders, and vendor bills across 13 periods, plus a **sealed** ground-truth file the agent never sees. Read `prompts/CONTRACTS.md` §0–§2 first.

**You own:** `unbilled/world.py`, `fixtures/*`, `tests/test_world.py`, the `world` target in `Makefile`. **Do not touch** anything else.

**Deliverable.**
- `python -m unbilled.world` (also `make world`) regenerates `fixtures/vendors.json`, `coa.json`, `bills.json`, `pos.json`, `world_truth.json` byte-identically from `WORLD_SEED=20260906` (use `random.Random(seed)`; no `datetime.now()`; sort all lists by id).
- 12 vendors with sealed latent params (CONTRACTS §2): 8 accrual-relevant (patterns: 3× monthly_recurring, 2× po_receipt, 1× quarterly_arrears, 1× usage_linked, 1× one_off) and **4 negative cases** (negative_prepaid: annual bill in 2025-09 covering 12 months; negative_early_invoice: bills always received before close_date; negative_terminated: last service 2026-01; and one monthly vendor whose bills for Apr–Jul arrive *before* close, so no accrual is due in those periods). Realistic names ("Acme Legal LLP", "Northwind Cloud Services", "Brightline Facilities"), memos, and amounts $800–$45,000. One rate change (+8%) on a monthly vendor in 2026-05. One quarterly vendor billed in arrears (service Q, invoice ~25 days after quarter end).
- Invoice lag per bill drawn from the vendor's `N(lag_mean_days, lag_sd_days)`, clipped to [3, 60]; `received_date = last day of service_period + lag`. Bills for the history periods are all received. Late tail: some Apr–Jul bills legitimately arrive after the *next* close (lag > ~35 days) — the truth file records `arrives_by_close_of` accordingly.
- POs for po_receipt vendors: issued at period start, `received_pct` reaches 1.0 by period end, `received_date` set; bill arrives with lag.
- `world_truth.json` per CONTRACTS §2: for every period 2025-08..2026-07 and every vendor, `should_accrue` (true iff a service was consumed in that period and its bill's `received_date > close_date(period)`), `true_amount` (that bill's amount, or 0), `invoice_bill_id`, `arrives_by_close_of`.
- Sanity invariants (assert in tests): for every `should_accrue=true` truth row there is exactly one bill with that `service_period` and `vendor_id`; negatives have `should_accrue=false` in Apr–Jul; at close 2026-04 there are ≥6 vendors with `should_accrue=true`; trailing-3-month history exists for every accrual-relevant vendor by 2026-02.
- A `fixtures/README.md` (10 lines) describing files and the close-date convention, and stating that `world_truth.json` is sealed.

**Acceptance test (run before opening the PR):** `make world && python -m pytest tests/test_world.py -q` passes; running `make world` twice yields no git diff (`git status --porcelain fixtures/` empty).

**Constraints.** Pure stdlib + pydantic. No network. Keep `world.py` under ~350 lines; comment the latent-parameter table at the top. Do not import `world_truth.json` anywhere except tests.

**Report back** in one paragraph: vendor table (id, name, pattern, negative?), how many truth rows are `should_accrue=true` per demo period, and any invariant you could not satisfy.

**Time box:** 60 minutes.
