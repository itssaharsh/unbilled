"""Pydantic models shared across modules (CONTRACTS §4, §5, §9, §10). Owned by the orchestrator."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Kind = Literal["accrual_method", "cutoff_lag", "coding", "tool_fact"]
Source = Literal["human_correction", "inferred_from_data", "tool_error"]
Status = Literal["proposed", "active", "deprecated", "rejected"]
Method = Literal["po_based", "run_rate", "contract", "usage", "none"]
Arm = Literal["main", "memory_off", "validator_off"]
Route = Literal["auto_posted", "escalated", "no_entry"]
ReasonCode = Literal[
    "wrong_method", "wrong_period", "should_not_accrue", "immaterial", "superseded_by_po", "vendor_terms_changed"
]
ResponseFormat = Literal["concise", "detailed"]


# ---------- world / ledger ----------
class Vendor(BaseModel):
    vendor_id: str
    name: str
    default_account_id: str
    terms_days: int = 30
    po_required: bool = False
    active: bool = True
    category: str = ""


class Account(BaseModel):
    account_id: str
    name: str
    type: Literal["expense", "liability", "asset", "equity", "revenue"]
    active: bool = True


class Bill(BaseModel):
    bill_id: str
    vendor_id: str
    invoice_date: str
    received_date: str
    service_period: str
    amount: float
    account_id: str
    memo: str = ""
    po_id: str | None = None


class PurchaseOrder(BaseModel):
    po_id: str
    vendor_id: str
    amount: float
    issued_date: str
    received_pct: float = 0.0
    received_date: str | None = None
    status: Literal["open", "closed"] = "open"


class AnticipatedVendor(BaseModel):
    vendor_id: str
    name: str
    last_service_period_billed: str | None = None
    typical_amount: float | None = None
    typical_lag_days: float | None = None


class PeriodContext(BaseModel):
    period: str
    close_date: str
    arrived_bills: list[Bill]
    open_pos: list[PurchaseOrder]
    anticipated_vendors: list[AnticipatedVendor]
    active_expense_accounts: list[Account]
    vendors: list[Vendor]
    truncation_notice: str | None = None


class HistoryRow(BaseModel):
    service_period: str
    amount: float
    account_id: str
    received_date: str
    lag_days: int
    po_id: str | None = None


class HistoryStats(BaseModel):
    mean_amount: float | None = None
    trailing_3_mean: float | None = None
    lag_mean_days: float | None = None
    lag_sd_days: float | None = None
    periods_with_no_bill: list[str] = Field(default_factory=list)
    n_bills: int = 0


class VendorHistory(BaseModel):
    vendor_id: str
    as_of_period: str
    per_period: list[HistoryRow]
    stats: HistoryStats
    open_pos: list[PurchaseOrder] = Field(default_factory=list)


class JournalLine(BaseModel):
    account_id: str
    debit: float = 0.0
    credit: float = 0.0
    memo: str = ""


class JournalEntryIn(BaseModel):
    period: str
    vendor_id: str
    amount: float
    expense_account_id: str
    memo: str = ""
    estimate_id: int | None = None


class JournalEntryOut(BaseModel):
    journal_id: str
    status: Literal["posted", "reversed", "unposted"]
    entry_date: str
    reversal_date: str
    lines: list[JournalLine]
    external_ref: str | None = None


# ---------- precedent ledger ----------
class Rule(BaseModel):
    id: str
    kind: Kind
    scope: str
    trigger: str
    action: str
    rationale: str
    source: Source
    provenance: dict[str, Any] = Field(default_factory=dict)
    applied: int = 0
    helpful: int = 0
    harmful: int = 0
    status: Status = "active"
    canary_delta: dict[str, Any] | None = None
    created_period: str = ""
    updated_period: str = ""
    version: int = 1


class RuleDraft(BaseModel):
    kind: Kind
    scope: str
    trigger: str
    action: str
    rationale: str
    source: Source
    provenance: dict[str, Any] = Field(default_factory=dict)


class DeltaOp(BaseModel):
    op: Literal["add", "update", "deprecate"]
    rule_id: str | None = None
    rule: RuleDraft | None = None
    reason: str = ""


class ProposeResult(BaseModel):
    added: list[str] = Field(default_factory=list)
    updated: list[str] = Field(default_factory=list)
    deprecated: list[str] = Field(default_factory=list)
    deduped: list[str] = Field(default_factory=list)
    auto_deprecated: list[str] = Field(default_factory=list)


# ---------- estimator ----------
class Decision(BaseModel):
    vendor_id: str
    period: str
    should_accrue: bool
    method: Method
    amount: float = 0.0
    confidence: float = Field(ge=0.0, le=1.0)
    account_id: str
    cited_rule_ids: list[str] = Field(default_factory=list)
    rationale: str = ""
    workpaper_md: str = ""


DECISION_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["vendor_id", "period", "should_accrue", "method", "amount", "confidence", "account_id",
                 "cited_rule_ids", "rationale", "workpaper_md"],
    "properties": {
        "vendor_id": {"type": "string"},
        "period": {"type": "string"},
        "should_accrue": {"type": "boolean"},
        "method": {"type": "string", "enum": ["po_based", "run_rate", "contract", "usage", "none"]},
        "amount": {"type": "number"},
        "confidence": {"type": "number"},
        "account_id": {"type": "string"},
        "cited_rule_ids": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
        "workpaper_md": {"type": "string"},
    },
}


class Usage(BaseModel):
    in_tokens: int = 0
    out_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    tool_calls: int = 0
    model: str = ""

    def add(self, other: "Usage") -> "Usage":
        return Usage(
            in_tokens=self.in_tokens + other.in_tokens,
            out_tokens=self.out_tokens + other.out_tokens,
            cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens,
            cache_write_tokens=self.cache_write_tokens + other.cache_write_tokens,
            cost_usd=self.cost_usd + other.cost_usd,
            latency_ms=self.latency_ms + other.latency_ms,
            tool_calls=self.tool_calls + other.tool_calls,
            model=self.model or other.model,
        )


# ---------- llm ----------
class ToolSpec(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


class ToolCall(BaseModel):
    id: str
    name: str
    input: dict[str, Any]


class LLMResponse(BaseModel):
    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    usage: Usage = Field(default_factory=Usage)
    stop_reason: str = ""
    raw: Any = None


# ---------- runner / validator ----------
class CloseResult(BaseModel):
    run_id: str
    period: str
    arm: Arm
    seed: int
    n_vendors: int
    auto_posted: int
    escalated: int
    no_entry: int
    touches: int
    usage: Usage
    seconds: float
    ledger_snapshot_before: str | None = None
    ledger_snapshot_after: str | None = None
    validator_decision: str | None = None
    delta_ops: int = 0


class ValidatorResult(BaseModel):
    decision: Literal["commit", "rollback"]
    mape_incumbent: float | None
    mape_candidate: float | None
    cost_incumbent: float
    cost_candidate: float
    recall_incumbent: float | None = None
    recall_candidate: float | None = None
    rejected_rule_ids: list[str] = Field(default_factory=list)
    committed_rule_ids: list[str] = Field(default_factory=list)


# ---------- exports (web/public/data) ----------
class CloseSummary(BaseModel):
    period: str
    seeds: list[int]
    mape: float | None
    n_scored: int
    precision: float | None
    recall: float | None
    pass_at_1: float | None
    pass_k: float | None
    cost_usd: float
    seconds: float
    touches: int
    auto_posted: int
    escalated: int
    cache_hit_rate: float | None = None
    ledger_size: int = 0
    rules_added: int = 0
    rules_deprecated: int = 0
    rules_rejected: int = 0
    validator_decision: str | None = None


class ArmResult(BaseModel):
    closes: list[CloseSummary]


class ValidatorLogRow(BaseModel):
    period: str
    mape_incumbent: float | None
    mape_candidate: float | None
    cost_delta_pct: float | None
    decision: str
    ops: int


class RuleDiscovery(BaseModel):
    rule_id: str
    claim: str
    inferred: float | None
    sealed: float | None
    ok: bool | None


class RunsSummary(BaseModel):
    mape_first: float | None = None
    mape_last: float | None = None
    touches_first: int | None = None
    touches_last: int | None = None
    cost_first: float | None = None
    cost_last: float | None = None
    notes: dict[str, str] = Field(default_factory=dict)


class RunsJson(BaseModel):
    generated_at: str
    world_seed: int
    materiality: dict[str, float]
    periods: list[str]
    arms: dict[str, ArmResult]
    validator_log: list[ValidatorLogRow] = Field(default_factory=list)
    rule_discovery: list[RuleDiscovery] = Field(default_factory=list)
    summary: RunsSummary = Field(default_factory=RunsSummary)


class WorksheetRow(BaseModel):
    vendor_id: str
    name: str
    last3_actuals: list[float]
    method: Method | None
    estimate: float | None
    confidence: float | None
    cited_rule_ids: list[str]
    route: Route
    human_action: str | None = None
    human_reason_code: str | None = None
    human_note: str | None = None
    final_amount: float | None = None
    actual: float | None = None
    actual_pending_until: str | None = None
    variance_pct: float | None = None
    journal_id: str | None = None
    reversal_date: str | None = None
    workpaper_md: str | None = None
    account_id: str | None = None
    estimate_id: int | None = None
    rationale: str | None = None


# ---------- api ----------
class ReviewRequest(BaseModel):
    period: str
    vendor_id: str
    action: Literal["approve", "edit", "reject"]
    amount: float | None = None
    reason_code: ReasonCode | None = None
    note: str = ""
    reviewer: str = "controller"


class UnpostRequest(BaseModel):
    journal_id: str


class RuleEditRequest(BaseModel):
    rule_id: str
    trigger: str | None = None
    action: str | None = None
    rationale: str | None = None
    status: Status | None = None
