PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python)

.PHONY: all setup raw clean-data label train rules export all bench test api web fetch-data reset

setup:
	@if [ ! -d .venv ]; then python3.12 -m venv .venv 2>/dev/null || python3 -m venv .venv; fi
	.venv/bin/pip install -r requirements-dev.txt
	cd frontend && npm ci

raw:
	$(PYTHON) -m etl.raw

clean-data:
	$(PYTHON) -m etl.profile
	$(PYTHON) -m etl.clean

label:
	$(PYTHON) -m etl.label

train:
	$(PYTHON) -m ml.train

rules:
	$(PYTHON) -m mining.rules

export:
	$(PYTHON) -m ml.export_runtime

all:
	$(PYTHON) -m etl.pipeline

bench:
	$(PYTHON) -m mining.fpgrowth_bench

test:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m pytest -q

api:
	$(PYTHON) -m uvicorn api.main:app --reload --port 8000

web:
	cd frontend && npm run dev

fetch-data:
	gh release download data-v3 --dir data/

reset:
	rm -rf data/*.parquet data/*.csv data/stats artifacts/*.pkl artifacts/*.parquet

stats:
	PYTHONPATH=. $(PYTHON) scripts/collect_stats.py

