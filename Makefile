PYTHON ?= python3
MARKER_VERSION ?= marker-pdf 1.10.2

.PHONY: books books-check check doctrine-check test

books:
	BOOKS_MARKER_VERSION="$(MARKER_VERSION)" ./scripts/convert-books

books-check:
	BOOKS_MARKER_VERSION="$(MARKER_VERSION)" ./scripts/convert-books --check

test:
	$(PYTHON) -m unittest discover -s tests -v

doctrine-check:
	$(PYTHON) doctrine/tools/build_chapter_coverage.py --check
	$(PYTHON) doctrine/tools/build_gold_queue.py --check
	$(PYTHON) doctrine/tools/build_routing_index.py --check
	$(PYTHON) doctrine/tools/build_section_map.py --check
	$(PYTHON) doctrine/tools/sync_concepts_to_graph.py --check
	$(PYTHON) doctrine/tools/merge_graph_fragments.py --check
	$(PYTHON) doctrine/tools/validate_doctrine.py

check: test books-check doctrine-check
