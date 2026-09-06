# w02-ledger-precedent — ledger backend + Precedent Ledger store

**Role.** You build the two data layers: the `LedgerClient` fixture backend (what the agent reads and writes, filtered by close date) and the `PrecedentStore` (the agent's memory, with the deterministic Curator merge and snapshot/restore). Read `prompts/CONTRACTS.md` §2–§4, §9 first. Use the pydantic models in `unbilled/schemas.py` (do not redefine them; if one is missing, add it there in a clearly separated block and say so in the PR).

**You own:** `unbilled/ledger.py`, `unbilled/precedent.py`, `tests/test_ledger.py`, `tests/test_precedent.py`. **Do not touch** `world.py`, `tools.py`, `estimator.py`, anything in `web/`.

**Deliverable — `ledger.py`.**
- `FixtureBackend(LedgerClient)` loading `fixtures/*.json` once; `get_period_context(period, response_format)` returns only bills/POs with `received_date <= close_date(period)`, the vendor master, active expense accounts, and `anticipated_vendors` (active vendors with no bill for `service_period == period` visible at close but with ≥2 prior bills; include `typical_amount` = trailing-3 mean, `typical_lag_days`). Concise mode caps `arrived_bills` at 60 (most recent) and adds a `truncation_notice` string telling the agent to call `vendor_history` per vendor.
- `vendor_history(vendor_id, as_of_period, months)` computes per-period amounts, `lag_days` (received − last day of service period), trailing-3 mean, lag mean/sd, `periods_with_no_bill`, all as of the close date (no leakage of later bills).
- `post_accrual(je)` validates balance (sum debits == sum credits, 2 lines: Dr expense / Cr 2100), sets `entry_date` = last day of period, `reversal_date` = first day of next period, writes `journal` row, returns `JournalEntryOut`. `unpost(journal_id)` sets status `unposted`. Raise `LedgerError` with the instructive messages from CONTRACTS §5 (double-count, unknown account).
- `get_ledger()` returns FixtureBackend by default; `QboBackend` is a stub raising `NotImplementedError("see w10")` — keep the class so w10 can fill it.

**Deliverable — `precedent.py`.** Implement `PrecedentStore` exactly per CONTRACTS §4: `search` (rapidfuzz `fuzz.token_set_ratio` over `trigger + " " + action`, active rules, optional kind / vendor scope filter incl. `global`), `always_on` (top-n by helpful−harmful then id), `propose(ops, period)` (Curator: `add` → new `PRE-NNN` id, status `proposed` if `source == inferred_from_data` else `active`; dedupe against existing rules when `token_set_ratio > 88` → convert to `update` that merges rationale and bumps version; `update` → in-place with version bump; `deprecate` → status `deprecated`; after any merge, auto-deprecate rules with `harmful > helpful`), `mark`, `snapshot`/`restore` (full-table JSON dump into `ledger_snapshot`, restore replaces the table), `export_history(path)` (one line per snapshot, CONTRACTS §9). IDs are zero-padded and monotonic; never reuse.

**Acceptance test:** `python -m pytest tests/test_ledger.py tests/test_precedent.py -q` — must cover: close-date filtering hides a bill received on day 6; anticipated_vendors excludes vendors that billed this period; JE balance check; double-count error text; dedupe at 89 vs 87 similarity; auto-deprecate when harmful > helpful; snapshot → mutate → restore round-trips byte-for-byte.

**Constraints.** SQLite via the connection factory in `config.py`; no ORM; deterministic ordering everywhere (`ORDER BY`), because prompt caching depends on byte-stable rule blocks.

**Report back:** public method list with one-line semantics, and any CONTRACTS ambiguity you resolved.

**Time box:** 60 minutes.
