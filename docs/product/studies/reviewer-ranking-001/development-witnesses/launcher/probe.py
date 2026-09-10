"""Capture the original launcher's process result independently of its status."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

command = sys.argv[1:]
result = subprocess.run(command, capture_output=True, timeout=7)
root = Path('/capture')
(root / 'launcher.stdout').write_bytes(result.stdout)
(root / 'launcher.stderr').write_bytes(result.stderr)
(root / 'observation.json').write_text(json.dumps({
    'command': command, 'returncode': result.returncode,
    'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
    'stderr_sha256': hashlib.sha256(result.stderr).hexdigest()}, indent=2, sort_keys=True) + '\n')
