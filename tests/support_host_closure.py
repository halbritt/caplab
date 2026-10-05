"""Synthetic ELF files, loader caches and host trees for host-closure tests.

Everything here is fabricated: tiny 64-bit ELF images that carry just the program
headers and dynamic entries the closure reader consumes, a glibc-format loader cache,
and a directory tree that mirrors the distribution layout (a ``/lib64`` symlink to
``usr/lib64``, an interpreter symlink, versioned library symlinks).  No host file is
read or written.
"""

from __future__ import annotations

import os
import struct
from pathlib import Path

CACHE_MAGIC = b"glibc-ld.so.cache1.1"
LIBC6_X8664 = 0x0303


def synthetic_elf(
    *,
    interpreter: str | None = None,
    needed: tuple[str, ...] = (),
    soname: str | None = None,
    rpath: str | None = None,
    runpath: str | None = None,
    padding: bytes = b"",
) -> bytes:
    """A minimal ELF64 little-endian image: PT_INTERP, PT_LOAD, PT_DYNAMIC and a strtab."""

    strtab = bytearray(b"\0")

    def intern(text: str) -> int:
        offset = len(strtab)
        strtab.extend(text.encode() + b"\0")
        return offset

    entries: list[tuple[int, int]] = [(1, intern(name)) for name in needed]
    if soname is not None:
        entries.append((14, intern(soname)))
    if rpath is not None:
        entries.append((15, intern(rpath)))
    if runpath is not None:
        entries.append((29, intern(runpath)))
    headers = 2 + (interpreter is not None)
    interp = b"" if interpreter is None else interpreter.encode() + b"\0"
    interp_offset = 64 + 56 * headers
    strtab_offset = interp_offset + len(interp)
    dynamic_offset = strtab_offset + len(strtab)
    dynamic_offset += -dynamic_offset % 8
    entries.append((5, strtab_offset))
    entries.append((0, 0))
    dynamic = b"".join(struct.pack("<qQ", tag, value) for tag, value in entries)
    total = dynamic_offset + len(dynamic)

    def program_header(kind: int, offset: int, size: int) -> bytes:
        return struct.pack("<IIQQQQQQ", kind, 4, offset, offset, offset, size, size, 8)

    program_headers = b""
    if interpreter is not None:
        program_headers += program_header(3, interp_offset, len(interp))
    program_headers += program_header(1, 0, total)
    program_headers += program_header(2, dynamic_offset, len(dynamic))
    header = bytearray(64)
    header[:7] = b"\x7fELF\x02\x01\x01"
    struct.pack_into(
        "<HHIQQQIHHHHHH", header, 16, 3, 62, 1, 0, 64, 0, 0, 64, 56, headers, 64, 0, 0
    )
    image = bytes(header) + program_headers + interp
    image += (
        bytes(strtab) + b"\0" * (dynamic_offset - strtab_offset - len(strtab)) + dynamic
    )
    return image + padding


def synthetic_cache(entries: list[tuple[str, str, int, int]]) -> bytes:
    """A glibc new-format ``ld.so.cache``: (soname, path, flags, hwcap) entries."""

    strings = bytearray()
    offsets: dict[str, int] = {}

    def intern(text: str) -> int:
        if text not in offsets:
            offsets[text] = 48 + 24 * len(entries) + len(strings)
            strings.extend(text.encode() + b"\0")
        return offsets[text]

    table = b"".join(
        struct.pack("<iIIIQ", flags, intern(soname), intern(path), 0, hwcap)
        for soname, path, flags, hwcap in entries
    )
    header = CACHE_MAGIC + struct.pack("<II", len(entries), len(strings))
    header += bytes([2, 0, 0, 0]) + struct.pack("<IIII", 0, 0, 0, 0)
    assert len(header) == 48
    return header + table + bytes(strings)


class SyntheticHost:
    """A directory tree that looks like a small dynamically linked installation.

    ``/usr/bin/caplab-synthetic-tool`` needs ``libalpha.so.1`` and ``libc.so.6``; its interpreter is
    ``/lib64/ld-test.so.2``, reached through the usual two symlinks.  Libraries sit in
    ``/usr/lib/x86_64-linux-gnu`` and are named by the loader cache through the ``/lib``
    symlink, as on the real host.
    """

    EXECUTABLE = "/usr/bin/caplab-synthetic-tool"
    INTERPRETER = "/lib64/ld-test.so.2"
    LIBDIR = "/usr/lib/x86_64-linux-gnu"

    def __init__(self, root: Path) -> None:
        self.root = root
        for directory in ("/usr/bin", self.LIBDIR, "/usr/lib64", "/etc"):
            (root / directory.lstrip("/")).mkdir(parents=True, exist_ok=True)
        for directory in (
            "usr",
            "usr/bin",
            "usr/lib",
            "usr/lib/x86_64-linux-gnu",
            "usr/lib64",
            "etc",
        ):
            os.chmod(root / directory, 0o755)
        os.chmod(root, 0o755)
        os.symlink("usr/lib64", root / "lib64")
        os.symlink("usr/lib", root / "lib")
        os.symlink(
            "../lib/x86_64-linux-gnu/ld-test.so.2", root / "usr/lib64/ld-test.so.2"
        )
        self.write(
            self.EXECUTABLE,
            synthetic_elf(
                interpreter=self.INTERPRETER, needed=("libalpha.so.1", "libc.so.6")
            ),
            0o755,
        )
        self.write(
            f"{self.LIBDIR}/ld-test.so.2", synthetic_elf(soname="ld-test.so.2"), 0o755
        )
        self.write(
            f"{self.LIBDIR}/libc.so.6",
            synthetic_elf(needed=("ld-test.so.2",), soname="libc.so.6"),
            0o755,
        )
        self.write(
            f"{self.LIBDIR}/libalpha.so.1.0",
            synthetic_elf(needed=("libc.so.6",), soname="libalpha.so.1"),
            0o644,
        )
        os.symlink("libalpha.so.1.0", root / "usr/lib/x86_64-linux-gnu/libalpha.so.1")
        self.write_cache()

    def path(self, name: str) -> Path:
        return self.root / name.lstrip("/")

    def write(self, name: str, payload: bytes, mode: int) -> None:
        target = self.path(name)
        if target.exists() or target.is_symlink():
            target.unlink()
        target.write_bytes(payload)
        os.chmod(target, mode)

    def write_cache(
        self, extra: list[tuple[str, str, int, int]] = (), replace: dict | None = None
    ) -> None:
        entries = {
            "ld-test.so.2": "/lib/x86_64-linux-gnu/ld-test.so.2",
            "libalpha.so.1": "/lib/x86_64-linux-gnu/libalpha.so.1",
            "libc.so.6": "/lib/x86_64-linux-gnu/libc.so.6",
            "libunrelated.so.3": "/lib/x86_64-linux-gnu/libunrelated.so.3",
        }
        entries.update(replace or {})
        rows = [(name, path, LIBC6_X8664, 0) for name, path in entries.items()] + list(
            extra
        )
        self.write("/etc/ld.so.cache", synthetic_cache(rows), 0o644)
