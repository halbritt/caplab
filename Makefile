PYTHON ?= python3
GO ?= go
MARKER_VERSION ?= marker-pdf 1.10.2
DOCTRINE_ASSEMBLER ?= doctrine/bin/assemble-packet
DOCTRINE_INDEX ?= doctrine/runtime/doctrine-index.sqlite3
DOCTRINE_GO_SOURCES := $(wildcard doctrine/cmd/assemble-packet/*.go) \
	$(wildcard doctrine/internal/packet/*.go) doctrine/go.mod doctrine/go.sum \
	doctrine/tools/build_packet_assembler.py

.PHONY: books books-check check doctrine-assembler doctrine-benchmark \
	doctrine-check doctrine-go-test doctrine-index doctrine-index-check \
	doctrine-parity doctrine-runtime test

books:
	BOOKS_MARKER_VERSION="$(MARKER_VERSION)" ./scripts/convert-books

books-check:
	BOOKS_MARKER_VERSION="$(MARKER_VERSION)" ./scripts/convert-books --check

test:
	$(PYTHON) -m unittest discover -s tests -v

doctrine-index:
	$(PYTHON) doctrine/tools/build_doctrine_index.py --out "$(DOCTRINE_INDEX)"

doctrine-index-check:
	$(PYTHON) doctrine/tools/build_doctrine_index.py --out "$(DOCTRINE_INDEX)" --check

doctrine-assembler: $(DOCTRINE_ASSEMBLER)

$(DOCTRINE_ASSEMBLER): $(DOCTRINE_GO_SOURCES)
	GO="$(GO)" $(PYTHON) doctrine/tools/build_packet_assembler.py --out "$(DOCTRINE_ASSEMBLER)"

doctrine-go-test:
	cd doctrine && CGO_ENABLED=0 GOTOOLCHAIN=local $(GO) test ./...

doctrine-runtime: doctrine-index doctrine-assembler

doctrine-parity:
	$(PYTHON) -m unittest -v tests.test_go_packet_assembler

doctrine-benchmark: doctrine-runtime
	$(PYTHON) doctrine/tools/benchmark_assemble_packet.py \
		--candidate "$(DOCTRINE_ASSEMBLER)" --index "$(DOCTRINE_INDEX)"

doctrine-check:
	$(PYTHON) doctrine/tools/build_chapter_coverage.py --check
	$(PYTHON) doctrine/tools/build_gold_queue.py --check
	$(PYTHON) doctrine/tools/build_routing_index.py --check
	$(PYTHON) doctrine/tools/build_section_map.py --check
	$(PYTHON) doctrine/tools/sync_concepts_to_graph.py --check
	$(PYTHON) doctrine/tools/merge_graph_fragments.py --check
	$(PYTHON) doctrine/tools/build_doctrine_index.py --out "$(DOCTRINE_INDEX)" --check
	$(PYTHON) doctrine/tools/validate_doctrine.py

check: test books-check doctrine-check doctrine-go-test
