# w04-tools-estimator — the five tools and the Estimator (Generator) loop

**Role.** You build what the model actually uses: the tool layer over the ledger and precedent store, and the per-vendor decision loop with the confidence gate, prompt-cache layout, and cost accounting. Read `prompts/CONTRACTS.md` §4 (`estimator.py`), §5, §6, §7 first, then Anthropic's "writing tools for agents" principles summarized in §5 (consolidated tools, `response_format`, instructive errors).

**You own:** `unbilled/tools.py`, `unbilled/estimator.py`, `unbilled/prompts/estimator_system.md` (create the dir), `tests/test_tools.py`, `tests/test_estimator.py`. **Do not touch** `ledger.py`, `precedent.py`, `llm.py`, `run.py`.

**Deliverable — `tools.py`.** JSON schemas (strict) + implementations for tools 1, 2, 3, 5 in CONTRACTS §5 (tool 4 `precedent_propose` is exposed only to the Reflector; define its schema here too, w06 imports it). Every error path returns the instructive text from §5; never raise through to the model. `TOOLSET_ESTIMATOR = [...]`, `dispatch(name, input, ctx) -> ToolResult(content, is_error)`; log every call (name, ms, chars returned). `precedent_search` marks returned rules `applied` when they are later cited.

**Deliverable — `estimator.py`.** `decide(vendor_id, period, *, seed, memory_on, temperature, ledger, store, llm)`:
1. Build `system` = `[stable rules block, always_on rules block]` (cache breakpoint on the second; **nothing time-varying before it**; rules sorted by id) when `memory_on`; with `memory_on=False` the second block is a fixed sentence "No precedents available."
2. First user message: the vendor's card (name, terms, default account), the period, `precedent_search` results for `f"{vendor} accrual {period}"` (k=8, vendor scope + global), and the instruction to decide.
3. Tool loop: up to `MAX_TOOL_CALLS = 4` tool calls (tools 1, 2, 3, 5), all `tool_result`s for one assistant turn returned in one user message; parse inputs with `json.loads`; then force the final answer as a structured `Decision` via `output_schema` (one extra call if the model didn't produce it).
4. Confidence gate: `should_accrue and confidence >= 0.85` → call `close_post_accrual` (if the model didn't) → `route=auto_posted`; else `escalated`. `should_accrue=false` with confidence ≥ 0.85 → no entry.
5. Workpaper: markdown with sections *Conclusion · Method · Evidence (bill ids, PO ids, history stats) · Precedents applied (rule ids) · Reversal*; store on the Decision.
6. Return `(Decision, Usage)` with tokens, cache_read, cost, latency, tool_calls.

**System prompt (`estimator_system.md`, ≤ 60 lines):** role = accrual preparer; definitions (accrual = received-not-invoiced; auto-reversing; materiality max(10%, $500)); method selection guidance (PO-based when a PO has receipts and no bill; run-rate for recurring vendors; contract for retainers; usage-linked when history correlates with a driver; none when the bill already arrived or the vendor is prepaid/terminated); how to cite precedents by id; be conservative on confidence (≥0.85 only with ≥3 periods of consistent history or a received PO); output the JSON decision.

**Acceptance test:** `python -m pytest tests/test_tools.py tests/test_estimator.py -q` with `LLM_PROVIDER=stub` (tool schemas validate with `additionalProperties:false`; double-count error text; a canned stub trajectory ends in a posted JE; memory_off produces the fixed block). Then with a real key: `LLM_PROVIDER=anthropic python -m unbilled.run --period 2026-04 --arm main --seed 1` (once w05 is merged) completes with ≥1 auto-post and ≥1 escalation and prints `cache_read_input_tokens > 0` for vendor #2 — paste the numbers in the PR.

**Constraints.** Model rules in CONTRACTS §7. Keep every prompt under ~3k tokens (concise tool results; the UI does not need prose). No `datetime.now()` in prompts. Log the full message list for the first vendor of each close to `logs/` (gitignored) for debugging.

**Report back:** average tool calls, tokens, cost and latency per vendor on the real model; the auto-post/escalation split for 2026-04; anything in the tool contracts you had to adjust.

**Time box:** 90 minutes.
