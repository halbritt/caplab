"""One-shot in-sandbox startup gate; EOF refuses rather than launching argv.

The native supervisor owns stdin. Consume exactly its release byte, leaving
all subsequent request bytes untouched for the actual command after exec.
This is a startup stage of the same protected outer launch, not a new harness.
"""
import os
import sys


def main():
    if len(sys.argv) < 2 or os.read(0, 1) != b'\x01':
        return 78
    os.execv(sys.argv[1], sys.argv[1:])


if __name__ == '__main__':
    raise SystemExit(main())
