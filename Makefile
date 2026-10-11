PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python)

.PHONY: all setup raw clean-data label train rules export all bench test api web fetch-data reset stats report

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

report:
	@mkdir -p docs/report/figures
	npx -y @mermaid-js/mermaid-cli -i docs/report/figures/pipeline_arch.mmd -o docs/report/figures/pipeline_arch.png -b white -s 2
	npx -y @mermaid-js/mermaid-cli -i docs/report/figures/serving_arch.mmd -o docs/report/figures/serving_arch.png -b white -s 2
	@if [ -f docs/report/template.docx ]; then $(PYTHON) scripts/tune_template.py; fi
	pandoc docs/report/report.md -o docs/report/report.docx --resource-path=docs/report --toc --number-sections $$(if [ -f docs/report/template.docx ]; then echo "--reference-doc=docs/report/template.docx"; fi)
	soffice --headless --convert-to pdf --outdir docs/report docs/report/report.docx


