# depotsync

Mirrors build artifacts out of a flat content archive into a destination
directory tree, driven by a JSON manifest. Used by the release pipeline
to populate deploy hosts.

## Usage

    depotsync -manifest depot.json -archive /srv/archive -dest /srv/deploy

## Manifest

    {
      "entries": [
        {"name": "release/app.bin", "key": "blobs/aa11"},
        {"name": "extras/debug-symbols.tar", "key": "blobs/bb22", "optional": true}
      ]
    }

- `name` — destination-relative path the object is written to.
- `key` — the object's key (path) in the archive.
- `optional` — marks extras that not every archive carries. If the
  archive does not have the object, the run skips that entry and moves
  on; anything else the manifest lists is required.

## Behaviour

- **Incremental.** An entry whose destination file already exists is
  skipped, so repeated runs only copy what is missing.
- Each run ends with a one-line summary:
  `sync complete: N synced, M skipped`.

## Development

    go build ./...
    go test ./...
