"""Atomic, create-only local-copy storage beneath an owned root."""

from __future__ import annotations

import os
import re
import secrets
import stat
from pathlib import Path

from ..errors import CopyMismatch


CONTENT_KEY = re.compile(r"\Aobjects/sha256/([0-9a-f]{2})/([0-9a-f]{64})\Z")


class FilesystemCopyStore:
    def __init__(self, root: Path) -> None:
        if root.is_symlink() or not root.is_absolute():
            raise ValueError("local-copy root must be an absolute non-symlink path")
        metadata = root.lstat()
        if not stat.S_ISDIR(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o750:
            raise ValueError("local-copy root must be a directory with mode 0750")
        self.root = root
        self.group_id = metadata.st_gid

    @staticmethod
    def _parts(key: str) -> tuple[str, ...]:
        match = CONTENT_KEY.fullmatch(key)
        if match is None or match.group(1) != match.group(2)[:2]:
            raise ValueError("local-copy key is not a canonical content-addressed key")
        return tuple(key.split("/"))

    def _open_parent(self, key: str, *, create: bool) -> tuple[int, str]:
        parts = self._parts(key)
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        descriptor = os.open(self.root, flags)
        try:
            for component in parts[:-1]:
                created = False
                try:
                    child = os.open(component, flags, dir_fd=descriptor)
                except FileNotFoundError:
                    if not create:
                        raise
                    os.mkdir(component, mode=0o750, dir_fd=descriptor)
                    child = os.open(component, flags, dir_fd=descriptor)
                    created = True
                except OSError as error:
                    raise ValueError(
                        "local-copy namespace contains a non-directory or symlink"
                    ) from error
                try:
                    child_metadata = os.fstat(child)
                    if (
                        child_metadata.st_gid != self.group_id
                        or stat.S_IMODE(child_metadata.st_mode) != 0o750
                    ):
                        if not created:
                            raise ValueError(
                                "local-copy directory has unsafe ownership or mode"
                            )
                        os.fchown(child, -1, self.group_id)
                        os.fchmod(child, 0o750)
                    if created:
                        os.fsync(child)
                        os.fsync(descriptor)
                except BaseException:
                    os.close(child)
                    raise
                os.close(descriptor)
                descriptor = child
            return descriptor, parts[-1]
        except BaseException:
            os.close(descriptor)
            raise

    def read(self, key: str) -> bytes | None:
        try:
            parent, filename = self._open_parent(key, create=False)
        except FileNotFoundError:
            return None
        try:
            try:
                descriptor = os.open(
                    filename,
                    os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC,
                    dir_fd=parent,
                )
            except FileNotFoundError:
                return None
            except OSError as error:
                raise ValueError("local-copy entry is not a regular non-symlink file") from error
            with os.fdopen(descriptor, "rb", closefd=True) as stream:
                metadata = os.fstat(stream.fileno())
                if (
                    not stat.S_ISREG(metadata.st_mode)
                    or metadata.st_gid != self.group_id
                    or stat.S_IMODE(metadata.st_mode) != 0o440
                ):
                    raise ValueError("local-copy entry has unsafe type, ownership, or mode")
                return stream.read()
        finally:
            os.close(parent)

    def write(self, key: str, data: bytes) -> None:
        existing = self.read(key)
        if existing is not None:
            if existing != data:
                raise CopyMismatch(f"refusing non-identical local copy at {key}")
            return

        parent, filename = self._open_parent(key, create=True)
        temporary = f".caplab-{secrets.token_hex(16)}"
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
            try:
                os.link(
                    temporary,
                    filename,
                    src_dir_fd=parent,
                    dst_dir_fd=parent,
                    follow_symlinks=False,
                )
            except FileExistsError:
                existing = self.read(key)
                if existing != data:
                    raise CopyMismatch(f"refusing non-identical local copy at {key}")
            os.fsync(parent)
        finally:
            try:
                os.unlink(temporary, dir_fd=parent)
            except FileNotFoundError:
                pass
            os.close(parent)
