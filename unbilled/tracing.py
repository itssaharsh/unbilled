"""Neatlogs tracing bootstrap. Must be imported before `anthropic`/`openai` (see unbilled/__init__.py).

Owned by w03; this is the minimal stub so imports work before w03 lands."""
from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)
_initialised = False


def init() -> bool:
    """Initialise Neatlogs if NEATLOGS_API_KEY is set. Returns True when tracing is active."""
    global _initialised
    if _initialised:
        return True
    key = os.environ.get("NEATLOGS_API_KEY")
    if not key:
        return False
    try:
        import neatlogs  # type: ignore

        instr = ["anthropic"]
        if os.environ.get("LLM_PROVIDER") == "openai_compat":
            instr.append("openai")
        neatlogs.init(api_key=key, workflow_name="unbilled-close", instrumentations=instr)
        _initialised = True
    except Exception as exc:  # pragma: no cover - optional dependency path
        log.warning("neatlogs init failed: %s", exc)
        return False
    return True


init()
