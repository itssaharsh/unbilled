# w03-llm-tracing — provider abstraction, cost accounting, Neatlogs

**Role.** You build the only module that talks to a model. Two providers behind one normalized interface, exact cost/latency/cache accounting, retries, and Neatlogs tracing. Read `prompts/CONTRACTS.md` §4 (`llm.py`), §6, §7 first. Use the official `anthropic` SDK for Claude and the `openai` SDK for the OpenAI-compatible path; never call Claude through the OpenAI client.

**You own:** `unbilled/llm.py`, `unbilled/tracing.py`, `tests/test_llm.py`, `scripts/smoke_llm.py`. **Do not touch** anything else.

**Deliverable.**
- `LLMProvider.chat(...)` per CONTRACTS §4 returning `LLMResponse(text, tool_calls, usage, cost_usd, latency_ms, raw_stop_reason)`.
- `AnthropicProvider` (SDK **1.x**, see CONTRACTS §7 — `temperature` goes in `extra_body`, never as a kwarg): `client.messages.create(model, system=[...blocks...], messages, tools, tool_choice, max_tokens, extra_body={"temperature": t} only when t is not None and the model is Haiku 4.5, output_config={"format": {...}} when `output_schema` given, thinking={"type":"adaptive"} only for the reflector role)`. Tools get `strict: True`. Apply `cache_control: {"type":"ephemeral"}` to the last system block when `cache_prefix_blocks > 0`. Read `usage.input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`; cost from `PRICES` (cache reads billed at 10% of input price, cache writes at 125%). Never pass `temperature`/`top_p`/`budget_tokens` to Sonnet 5 / Opus 5; never pass `output_config.effort` to Haiku 4.5.
- `OpenAICompatProvider` (base_url + key from env): tools → `functions`/`tools` format; JSON output via `response_format={"type":"json_schema", ...}` if the server accepts it, else instruct in the system prompt and `json.loads` the text with **one** repair retry. Same normalized usage/cost (`PRICES` for `glm-4-7-flash`, `gpt-5-nano`: treat unknown models as $0).
- `get_provider(role)` chooses by `LLM_PROVIDER`, `ESTIMATOR_MODEL`, `REFLECTOR_MODEL`. Also `StubProvider` (deterministic canned responses keyed by a hash of the last user message) so `run.py`, tests, and the UI worker can run with **no API key**; `LLM_PROVIDER=stub` selects it.
- Retries: SDK default plus an outer loop of 3 on 429/5xx/timeouts with 5→10→20 s + jitter; log each 429 with the model and elapsed time (this evidence goes in the README's cost section).
- `tracing.init()` → `neatlogs.init(api_key, workflow_name="unbilled-close", instrumentations=[...])` if `NEATLOGS_API_KEY` is set, else no-op; it **must be imported before `anthropic`** — `unbilled/__init__.py` should import `tracing` first (coordinate: add one line there and say so in the PR).
- `scripts/smoke_llm.py`: one tool-call round trip + one structured-output call per configured provider, prints usage, cost, cache_read, latency; with `--burst 10` fires 10 concurrent tiny calls and prints how many 429s occurred (rate-limit check for the human).

**Acceptance test:** `python -m pytest tests/test_llm.py -q` (stub provider + request-shaping tests that assert forbidden params are absent per model); `LLM_PROVIDER=stub python scripts/smoke_llm.py` runs; if a real key is present, `python scripts/smoke_llm.py --burst 10` completes and prints numbers.

**Constraints.** No global mutable state other than a lazily created client. Keep the module under ~300 lines. Type everything.

**Report back:** measured latency/cost per provider, whether `cache_read_input_tokens` was > 0 on the second identical call, the 429 count from the burst, and whether the OpenAI-compatible endpoint honoured `tools` and `response_format`.

**Time box:** 45 minutes.
