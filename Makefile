.PHONY: all clean profile etl label train mine

all: clean etl label train mine

clean_artifacts:
	rm -f data/*.parquet
	rm -f artifacts/*.json
	rm -f artifacts/*.pkl
	rm -f artifacts/*.parquet

profile:
	.venv/bin/python -m etl.profile

etl:
	.venv/bin/python -m etl.clean
	.venv/bin/python -m etl.normalize
	.venv/bin/python scripts/generate_autocomplete.py

label:
	.venv/bin/python -m etl.label

train:
	.venv/bin/python -m ml.features
	.venv/bin/python -m ml.train
	.venv/bin/python -m ml.predict

mine:
	.venv/bin/python -m mining.apriori
	.venv/bin/python -m mining.rules

release_data:
	gh release create data-v1 data/dataset.parquet data/baskets.parquet artifacts/skill_vocab.json artifacts/skills_autocomplete.json --notes "Data release"

release_model:
	gh release create model-v1 artifacts/classifier.pkl artifacts/label_encoder.pkl artifacts/role_profiles.json artifacts/metrics.json --notes "Model release"
