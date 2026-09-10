#!/usr/bin/python3 -I
"""Record dispatch only; never execute the supervisor argument."""
import json
import os
from pathlib import Path
import sys

output = Path(sys.argv[4]) if len(sys.argv) > 4 else None
Path('/capture/dispatch.json').write_text(json.dumps({
    'recorder': True, 'selected_executable': sys.argv[0], 'argv': sys.argv[1:],
    'environment': {key: os.environ.get(key) for key in
                    ('ZAI_API_KEY', 'OPENROUTER_API_KEY', 'PATH', 'PYTHONPATH')},
    'output_exists': output.is_dir() if output else False,
    'supervisor_executed': False}, indent=2, sort_keys=True) + '\n')
raise SystemExit(int(os.environ['WITNESS_EXIT']))
