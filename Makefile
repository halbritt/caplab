PYTHON ?= python3

.PHONY: books books-check check doctrine-check test

books:
	./scripts/convert-books

books-check:
	./scripts/convert-books --check

test:
	$(PYTHON) -m unittest discover -s tests -v

doctrine-check:
	$(PYTHON) doctrine/tools/build_chapter_coverage.py --check
	$(PYTHON) doctrine/tools/build_gold_queue.py --check
	$(PYTHON) doctrine/tools/build_routing_index.py --check
	$(PYTHON) doctrine/tools/sync_concepts_to_graph.py --check
	$(PYTHON) doctrine/tools/merge_graph_fragments.py --check
	$(PYTHON) doctrine/tools/validate_doctrine.py

check: test books-check doctrine-check
