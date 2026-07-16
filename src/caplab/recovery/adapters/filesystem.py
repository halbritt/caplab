"""P5-only local-copy adapter with atomic replacement and removal."""

from __future__ import annotations

import os
import secrets

from caplab.runtime.adapters.filesystem import FilesystemCopyStore


class FilesystemCustodyStore(FilesystemCopyStore):
    def replace(self, key: str, data: bytes) -> None:
        if not isinstance(data, bytes):
            raise TypeError("local-copy replacement payload must be bytes")
        parent, filename = self._open_parent(key, create=True)
        temporary = f".caplab-p5-{secrets.token_hex(16)}"
        try:
            descriptor = os.open(
                temporary,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                0o440,
                dir_fd=parent,
            )
            with os.fdopen(descriptor, "wb", closefd=True) as stream:
                os.fchown(stream.fileno(), -1, self.group_id)
                os.fchmod(stream.fileno(), 0o440)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(
                temporary,
                filename,
                src_dir_fd=parent,
                dst_dir_fd=parent,
            )
            os.fsync(parent)
        finally:
            try:
                os.unlink(temporary, dir_fd=parent)
            except FileNotFoundError:
                pass
            os.close(parent)

    def remove(self, key: str) -> None:
        try:
            parent, filename = self._open_parent(key, create=False)
        except FileNotFoundError:
            return
        try:
            os.unlink(filename, dir_fd=parent)
            os.fsync(parent)
        except FileNotFoundError:
            return
        finally:
            os.close(parent)

    def keys(self) -> set[str]:
        keys: set[str] = set()
        for path in self.root.rglob("*"):
            if path.is_symlink():
                raise ValueError("local-copy namespace contains a symlink")
            if not path.is_file():
                continue
            key = path.relative_to(self.root).as_posix()
            self._parts(key)
            self.read(key)
            keys.add(key)
        return keys
