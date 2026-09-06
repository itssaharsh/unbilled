"""Configuration, paths, period helpers, and the SQLite schema (CONTRACTS §1, §3)."""
from __future__ import annotations

import calendar
import os
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

FIXTURES_DIR = Path(os.environ.get("UNBILLED_FIXTURES_DIR", ROOT / "fixtures"))
DATA_DIR = Path(os.environ.get("UNBILLED_DATA_DIR", ROOT / "web" / "public" / "data"))
DB_PATH = Path(os.environ.get("UNBILLED_DB_PATH", ROOT / "unbilled.db"))
LOGS_DIR = ROOT / "logs"

WORLD_SEED = int(os.environ.get("WORLD_SEED", "20260906"))
ALL_PERIODS = [f"2025-{m:02d}" for m in range(8, 13)] + [f"2026-{m:02d}" for m in range(1, 9)]
HISTORY_PERIODS = ALL_PERIODS[:6]            # 2025-08 .. 2026-01
CANARY_PERIODS = ["2026-02", "2026-03"]
DEMO_PERIODS = ["2026-04", "2026-05", "2026-06", "2026-07"]
LAST_PERIOD = "2026-08"                      # exists only so July's actuals arrive

MATERIALITY_PCT = 0.10
MATERIALITY_ABS = 500.0
CONFIDENCE_THRESHOLD = 0.85
MAX_TOOL_CALLS = 4
ACCRUED_LIABILITIES_ACCOUNT = "2100"

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "stub")
ESTIMATOR_MODEL = os.environ.get("ESTIMATOR_MODEL", "claude-haiku-4-5")
REFLECTOR_MODEL = os.environ.get("REFLECTOR_MODEL", "claude-sonnet-5")
MAX_CONCURRENCY = int(os.environ.get("MAX_CONCURRENCY", "4"))
LEDGER_BACKEND = os.environ.get("LEDGER_BACKEND", "fixture")


def parse_period(p: str) -> tuple[int, int]:
    y, m = p.split("-")
    return int(y), int(m)


def period_str(y: int, m: int) -> str:
    return f"{y:04d}-{m:02d}"


def next_period(p: str) -> str:
    y, m = parse_period(p)
    return period_str(y + (m == 12), 1 if m == 12 else m + 1)


def prev_period(p: str) -> str:
    y, m = parse_period(p)
    return period_str(y - (m == 1), 12 if m == 1 else m - 1)


def period_start(p: str) -> date:
    y, m = parse_period(p)
    return date(y, m, 1)


def period_end(p: str) -> date:
    y, m = parse_period(p)
    return date(y, m, calendar.monthrange(y, m)[1])


def close_date(p: str) -> date:
    """Close for period P happens on day 5 of P+1; bills received on/before this date are visible."""
    return period_start(next_period(p)) + timedelta(days=4)


def within_materiality(estimate: float, actual: float) -> bool:
    return abs(estimate - actual) <= max(MATERIALITY_PCT * abs(actual), MATERIALITY_ABS)


DDL = """
CREATE TABLE IF NOT EXISTS precedent (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  scope TEXT NOT NULL,
  trigger TEXT NOT NULL,
  action TEXT NOT NULL,
  rationale TEXT NOT NULL,
  source TEXT NOT NULL,
  provenance TEXT NOT NULL,
  applied INTEGER DEFAULT 0, helpful INTEGER DEFAULT 0, harmful INTEGER DEFAULT 0,
  status TEXT NOT NULL,
  canary_delta TEXT,
  created_period TEXT NOT NULL, updated_period TEXT NOT NULL, version INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS estimate (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, period TEXT NOT NULL, vendor_id TEXT NOT NULL,
  arm TEXT NOT NULL, seed INTEGER NOT NULL,
  should_accrue INTEGER NOT NULL, method TEXT, amount REAL, confidence REAL, account_id TEXT,
  cited_rule_ids TEXT,
  route TEXT NOT NULL,
  human_action TEXT, human_reason_code TEXT, human_note TEXT, final_amount REAL,
  actual_amount REAL, variance_pct REAL, scored_in_period TEXT,
  in_tokens INTEGER, out_tokens INTEGER, cache_read_tokens INTEGER, cost_usd REAL, latency_ms INTEGER, tool_calls INTEGER,
  workpaper_md TEXT, journal_id TEXT, rationale TEXT
);
CREATE INDEX IF NOT EXISTS idx_estimate_run ON estimate(run_id);
CREATE INDEX IF NOT EXISTS idx_estimate_period_vendor ON estimate(period, vendor_id, arm, seed);
CREATE TABLE IF NOT EXISTS journal (
  journal_id TEXT PRIMARY KEY, period TEXT, vendor_id TEXT, estimate_id INTEGER,
  entry_date TEXT, reversal_date TEXT, lines TEXT,
  status TEXT,
  external_ref TEXT
);
CREATE TABLE IF NOT EXISTS run (
  run_id TEXT PRIMARY KEY, period TEXT, arm TEXT, seed INTEGER, started_at TEXT, finished_at TEXT,
  ledger_snapshot_before TEXT, ledger_snapshot_after TEXT, totals TEXT
);
CREATE TABLE IF NOT EXISTS ledger_snapshot (snapshot_id TEXT PRIMARY KEY, created_at TEXT, period TEXT, rules TEXT);
CREATE TABLE IF NOT EXISTS validator_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT, arm TEXT, seed INTEGER, candidate_snapshot TEXT, incumbent_snapshot TEXT,
  mape_incumbent REAL, mape_candidate REAL, cost_incumbent REAL, cost_candidate REAL,
  recall_incumbent REAL, recall_candidate REAL,
  decision TEXT,
  delta_ops TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS escalation (
  escalation_id TEXT PRIMARY KEY, estimate_id INTEGER, period TEXT, vendor_id TEXT, status TEXT, created_at TEXT, resolved_at TEXT
);
CREATE TABLE IF NOT EXISTS tool_error (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, period TEXT, vendor_id TEXT, tool TEXT, message TEXT, created_at TEXT
);
"""


def get_conn(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open (and initialise) the SQLite database. Callers close the connection."""
    path = Path(db_path) if db_path else DB_PATH
    conn = sqlite3.connect(str(path), isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(DDL)
