"""Remove only opaque native reasoning ciphertext before credential guarding.

This projection preserves readable evidence; it is not a credential filter.
Both returned objects still require the normal credential guard before storage.
"""
from __future__ import annotations

import hashlib
import json
import re


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('nonfinite JSON value')


def project_rollout(raw: bytes) -> tuple[bytes, dict]:
    lines, omissions = [], []
    for index, line in enumerate(raw.splitlines(keepends=True), start=1):
        row = json.loads(line, object_pairs_hook=unique_object, parse_constant=reject_constant)
        if not isinstance(row, dict):
            raise ValueError('native JSONL object required')
        payload = row.get('payload')
        if row.get('type') == 'response_item' and isinstance(payload, dict) and payload.get('type') == 'reasoning':
            opaque = payload.get('encrypted_content')
            if opaque is not None:
                if not isinstance(opaque, str):
                    raise ValueError('unexpected opaque reasoning shape')
                encoded = opaque.encode('utf-8')
                omissions.append({'row': index, 'field': 'payload.encrypted_content',
                                  'bytes': len(encoded), 'sha256': digest(encoded)})
                del payload['encrypted_content']
                ending = b'\r\n' if line.endswith(b'\r\n') else b'\n' if line.endswith(b'\n') else b''
                line = json.dumps(row, ensure_ascii=True, allow_nan=False, separators=(',', ':')).encode() + ending
        lines.append(line)
    projected = b''.join(lines)
    return projected, {'schema': 'caplab.codex-readable-rollout-projection/v1',
                       'original_bytes': len(raw), 'original_sha256': digest(raw),
                       'projected_bytes': len(projected), 'projected_sha256': digest(projected),
                       'omissions': omissions}


def verify_projection(projected: bytes, receipt: dict) -> None:
    """Check retained projection and omission shapes, not discarded raw bytes."""
    if (receipt['schema'] != 'caplab.codex-readable-rollout-projection/v1'
            or receipt['projected_bytes'] != len(projected)
            or receipt['projected_sha256'] != digest(projected)
            or not re.fullmatch('[0-9a-f]{64}', receipt['original_sha256'])
            or type(receipt['original_bytes']) is not int or receipt['original_bytes'] < 0):
        raise ValueError('projection receipt mismatch')
    unchanged, checked = project_rollout(projected)
    if unchanged != projected or checked['omissions']:
        raise ValueError('opaque content remains in projection')
    rows = projected.splitlines()
    seen = set()
    for omission in receipt['omissions']:
        index = omission['row']
        if (type(index) is not int or not 1 <= index <= len(rows) or index in seen
                or omission['field'] != 'payload.encrypted_content'
                or type(omission['bytes']) is not int or omission['bytes'] < 0
                or not re.fullmatch('[0-9a-f]{64}', omission['sha256'])):
            raise ValueError('invalid omission receipt')
        seen.add(index)
        row = json.loads(rows[index - 1])
        payload = row.get('payload')
        if (row.get('type') != 'response_item' or not isinstance(payload, dict)
                or payload.get('type') != 'reasoning' or 'encrypted_content' in payload):
            raise ValueError('omission is not an opaque reasoning field')
