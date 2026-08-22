.PHONY: check test leaderboard

check: test

test:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v

leaderboard:
	PYTHONPATH=src python3 scripts/build_leaderboard.py
