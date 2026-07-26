.PHONY: check test

check: design-lint test

design-lint:
	python3 scripts/caplab-design-lint

test:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
