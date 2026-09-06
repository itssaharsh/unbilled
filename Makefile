PY ?= python
PERIOD ?= 2026-04

.PHONY: world test close sweep export grade demo

world:
	$(PY) -m unbilled.world

test:
	$(PY) -m pytest -q

close:
	$(PY) -m unbilled.run --period $(PERIOD) --arm main --seed 1

sweep:
	$(PY) -m unbilled.run --sweep

export:
	$(PY) -c "from unbilled.metrics import export_all; from unbilled.config import DB_PATH, DATA_DIR; export_all(DB_PATH, DATA_DIR)"

grade:
	$(PY) evals/grade.py

demo:
	@echo "Starting API on :8787 and Vite dev server; Ctrl-C stops both"
	@(uvicorn unbilled.api:app --port 8787 & npm --prefix web run dev; wait)
