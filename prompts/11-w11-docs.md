# w11-docs — README, AO usage evidence, architecture

**Role.** You write the submission's reading material for judges who will spend ~4 minutes on the repo. Read `prompts/CONTRACTS.md` §0, `evals/results.md`, `docs/AO_USAGE.md` (orchestrator-maintained table), `docs/DEMO_SCRIPT.md`, and `git log --oneline`.

**You own:** `README.md`, `docs/ARCHITECTURE.md`, `docs/AO_USAGE.md` (finalize; keep the orchestrator's rows), `docs/screenshots/` captions. **Do not touch** code.

**README — use these six headings verbatim, in this order** (the hackathon's Notion requires them): `## What your project does` · `## How to run it` · `## Which track you are submitting to` · `## What agent workflow you built` · `## What improved across iterations` · `## Any demo or live links`. Then: `## Architecture and evaluation method`, `## Honesty notes`, `## How we used AO`, `## Credits`.
- Top of file: one-line pitch, the one hard number from `evals/results.md` (e.g. "accrual estimate error 34% → 8% over four closes, measured against the invoices that actually arrived"), a 1280-px screenshot, and a 4-line "why this is not a categorization agent" paragraph (accruals are for bills that don't exist yet).
- **How to run it:** `python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`, `cp .env.example .env`, `make demo` (works with **no API key** from committed data), then the optional real-model path (`LLM_PROVIDER=anthropic make close PERIOD=2026-04`, `make sweep`, `make grade`).
- **What agent workflow you built:** the loop diagram (Mermaid: Estimator → confidence gate → Review Queue → Reflector → Curator → Validator → Precedent Ledger → next close), the five tools with one line each, the four memory kinds, the confidence gate, the reversal mechanics (never mutate bill dates).
- **What improved across iterations:** paste the results table from `evals/results.md` (all arms), the rejection-log summary, three rule-discovery examples with sealed values, the pre-registration commit hash, and one paragraph on cost/speed (cache hit rate, $/close, batched reflection).
- **Honesty notes:** sealed synthetic world (why and how it's sealed); derived vs authored metrics; the sweep's reviewer is simulated, the demo's is human; what was cut for time.
- **How we used AO:** session count, orchestrator + worker split, the table from `docs/AO_USAGE.md`, the `ao/<session-id>/root` branch trail (`git branch -r | grep ao/`), the reviewer session on the validator PR, and anything AO routed back (only if it really happened).
- **Credits:** Anthropic SDK, rapidfuzz, FastAPI, Vite/React/Tailwind/Recharts, Neatlogs; research the design cites (ACE — Zhang et al. 2025; Anthropic's evals and writing-tools posts). No fabricated customer names or metrics.

**`docs/ARCHITECTURE.md`:** 1 page — components, data flow, storage, the cache layout, the Validator decision rule, and a table of failure modes → handling (429s, tool errors, double-count, pending actuals, token expiry).

**Acceptance test:** every README link resolves; every command in "How to run it" was executed by you in a fresh venv; `docs/AO_USAGE.md` lists every session name that appears in `ao session ls --all --include-terminated` (ask the orchestrator to paste that output).

**Constraints.** Plain, specific prose; no marketing adjectives; numbers only from `evals/results.md`. Under 250 lines of README.

**Report back:** the README outline with line counts and any claim you could not source.

**Time box:** 60 minutes.
