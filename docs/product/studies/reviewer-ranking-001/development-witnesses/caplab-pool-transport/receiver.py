"""Deterministic subprocess endpoint; supplies no reviewer-quality judgment."""
import hashlib
import json
from pathlib import Path
import sys
import time

config_path = Path(sys.argv[1])
config = json.loads(config_path.read_text())
events = config_path.parent / 'events'
events.mkdir(exist_ok=True)
event = events / str(len(list(events.iterdir())) + 1)
event.mkdir()
prompt = sys.stdin.read() if config['mode'] == 'stdin' else (sys.argv[2] if len(sys.argv) > 2 else '')
(event / 'prompt.txt').write_text(prompt)
body, delivery = '', 'absent'
if prompt:
    if config['direct']:
        body, delivery = prompt, config['mode']
    else:
        if not prompt.startswith(config['contract']):
            raise ValueError('received prompt does not contain the original contract')
        remaining = prompt[len(config['contract']):]
        prefix = 'The body under review is too large to inline. Read it in full from this file before deciding: '
        if remaining.startswith(prefix):
            path = Path(remaining[len(prefix):].strip())
            if not path.resolve().is_relative_to(Path('/capture').resolve()):
                raise ValueError('spill path outside private capture')
            body, delivery = path.read_text(), 'file'
        else:
            body, delivery = remaining, config['mode']
(event / 'body.txt').write_text(body)
digest = hashlib.sha256(body.encode()).hexdigest()
arm = next((key for key, value in config['expected_bodies'].items() if value == digest), None)
if prompt and arm is None:
    raise ValueError('received body bytes differ from either original arm')
behavior = config['behavior'] if arm == config.get('affected_arm') else 'healthy'
if not prompt:
    behavior = 'absent'
receipt = {'prompt_bytes': len(prompt.encode()), 'body_bytes': len(body.encode()),
           'body_sha256': digest, 'arm': arm, 'delivery': delivery, 'behavior': behavior}
(event / 'received.json').write_text(json.dumps(receipt, sort_keys=True) + '\n')
if behavior == 'timeout':
    time.sleep(5)
if behavior in ('empty', 'absent'):
    response = ''
elif behavior == 'invalid':
    response = json.dumps({'status': 'completed-without-a-verdict'})
else:
    response = json.dumps({'verdict': 'accept', 'findings': []})
(event / 'response.txt').write_text(response)
sys.stdout.write(response)
