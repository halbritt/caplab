PYTHON ?= python3

.PHONY: books books-check check test

books:
	./scripts/convert-books

books-check:
	./scripts/convert-books --check

test:
	$(PYTHON) -m unittest discover -s tests -v

check: test books-check
