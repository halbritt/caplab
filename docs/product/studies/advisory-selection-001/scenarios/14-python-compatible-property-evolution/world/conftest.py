# Make the in-tree package importable when running bare `pytest` as well as
# `python -m pytest`.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
