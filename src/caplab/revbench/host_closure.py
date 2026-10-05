"""Pin and recheck the host files a directly executed Bubblewrap loads.

The external-token bundle runs the root-controlled ``/usr/bin/bwrap`` as it is
installed, under that path's existing host permission.  A normal ELF load reads
host files this process cannot snapshot atomically, so the bundle pins what the
load will use and this module checks it immediately before every launch:

* the executable and its ``PT_INTERP`` interpreter, including each symlink and
  directory on their paths;
* every library the executable needs, transitively, as the loader cache names it;
* the loader inputs that can change which file is chosen: the cache entries of
  exactly those libraries (including any hardware-capability variants),
  ``/etc/ld.so.preload``, and the absence of ``RPATH``/``RUNPATH`` and of any
  library outside the pinned set.  The launch environment is empty, so
  ``LD_LIBRARY_PATH`` and the other loader variables are closed by construction.

Trust boundary, stated rather than hidden: a checked file can still be changed
by a privileged host maintainer between this check and the loader's reads.  The
bundle selects the assumption that privileged maintainers leave this closure
alone during an authorized administration; nothing here resists a malicious root
or proves an unobserved privileged change did not happen.  Callers only read and
check; nothing in this module writes, publishes or removes a host file.

Every refusal is a fixed code naming a category and a public member id, never a
path component or file content.
"""

from __future__ import annotations

import errno
import os
import stat
import struct
from collections import deque
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from caplab.runtime.canonical import canonical_json, sha256_hex

CLOSURE_SCHEMA = "caplab-revbench-host-closure/1"
CHECK_SCHEMA = "caplab-revbench-host-closure-check/1"
TRUST_ASSUMPTION = (
    "privileged-host-maintainers-do-not-change-the-pinned-closure-"
    "during-an-authorized-administration"
)
_MAX_LINKS = 40
_MAX_FILE_BYTES = 64 * 1024 * 1024
_CACHE_PATH = "/etc/ld.so.cache"
_PRELOAD_PATH = "/etc/ld.so.preload"
_CACHE_MAGIC = b"glibc-ld.so.cache1.1"
_PT_LOAD, _PT_DYNAMIC, _PT_INTERP = 1, 2, 3
_DT_NULL, _DT_NEEDED, _DT_STRTAB, _DT_SONAME, _DT_RPATH, _DT_RUNPATH = (
    0,
    1,
    5,
    14,
    15,
    29,
)


class HostClosureError(ValueError):
    """A pinned host file is missing, changed, writable or ambiguously resolved."""


def _refuse(category: str, member: str) -> HostClosureError:
    return HostClosureError(f"host_closure_{category}:{member}")


def closure_sha256(pinned: Mapping[str, Any]) -> str:
    """Identity of one pinned closure description."""

    return sha256_hex(canonical_json(pinned))


# --- ELF and loader-cache readers (bounded, read-only) ---------------------------------


def elf_dynamic(payload: bytes) -> dict[str, Any]:
    """Interpreter, needed names, soname and search paths of a 64-bit little-endian ELF."""

    if (
        len(payload) < 64
        or payload[:4] != b"\x7fELF"
        or payload[4] != 2
        or payload[5] != 1
    ):
        raise HostClosureError("host_closure_elf_unsupported")
    phoff = struct.unpack_from("<Q", payload, 0x20)[0]
    phentsize, phnum = struct.unpack_from("<HH", payload, 0x36)
    if phentsize != 56 or phnum > 512 or phoff + phentsize * phnum > len(payload):
        raise HostClosureError("host_closure_elf_unsupported")
    loads: list[tuple[int, int, int]] = []
    dynamic: tuple[int, int] | None = None
    interpreter: str | None = None
    for index in range(phnum):
        p_type, _flags, offset, vaddr, _paddr, filesz, _memsz, _align = (
            struct.unpack_from("<IIQQQQQQ", payload, phoff + index * phentsize)
        )
        if offset + filesz > len(payload):
            raise HostClosureError("host_closure_elf_unsupported")
        if p_type == _PT_LOAD:
            loads.append((vaddr, offset, filesz))
        elif p_type == _PT_DYNAMIC:
            dynamic = (offset, filesz)
        elif p_type == _PT_INTERP:
            raw = payload[offset : offset + filesz]
            if not raw.endswith(b"\0"):
                raise HostClosureError("host_closure_elf_unsupported")
            interpreter = raw[:-1].decode("utf-8", "strict")

    def string(index: int, strtab: int) -> str:
        position = _file_offset(loads, strtab) + index
        end = payload.find(b"\0", position)
        if end < 0:
            raise HostClosureError("host_closure_elf_unsupported")
        return payload[position:end].decode("utf-8", "strict")

    needed: list[int] = []
    soname: int | None = None
    rpath: list[int] = []
    runpath: list[int] = []
    strtab: int | None = None
    if dynamic is not None:
        offset, size = dynamic
        for index in range(min(size // 16, 4096)):
            tag, value = struct.unpack_from("<qQ", payload, offset + 16 * index)
            if tag == _DT_NULL:
                break
            if tag == _DT_NEEDED:
                needed.append(value)
            elif tag == _DT_STRTAB:
                strtab = value
            elif tag == _DT_SONAME:
                soname = value
            elif tag == _DT_RPATH:
                rpath.append(value)
            elif tag == _DT_RUNPATH:
                runpath.append(value)
    try:
        if (needed or soname is not None or rpath or runpath) and strtab is None:
            raise HostClosureError("host_closure_elf_unsupported")
        return {
            "interpreter": interpreter,
            "needed": [string(value, strtab) for value in needed] if strtab else [],
            "soname": None if soname is None else string(soname, strtab),
            "rpath": [string(value, strtab) for value in rpath] if strtab else [],
            "runpath": [string(value, strtab) for value in runpath] if strtab else [],
        }
    except UnicodeError:
        raise HostClosureError("host_closure_elf_unsupported") from None


def _file_offset(loads: Sequence[tuple[int, int, int]], address: int) -> int:
    for vaddr, offset, filesz in loads:
        if vaddr <= address < vaddr + filesz:
            return offset + (address - vaddr)
    raise HostClosureError("host_closure_elf_unsupported")


def parse_ld_so_cache(payload: bytes) -> list[dict[str, Any]]:
    """Entries of a glibc ``ld.so.cache`` (new format), as plain data."""

    base = payload.find(_CACHE_MAGIC)
    if base < 0 or base % 8 != 0 or len(payload) < base + 48:
        raise HostClosureError("host_closure_cache_unsupported")
    count, strings = struct.unpack_from("<II", payload, base + 20)
    table = base + 48
    if (
        count > 1_000_000
        or table + 24 * count > len(payload)
        or base + strings > len(payload) + 1
    ):
        raise HostClosureError("host_closure_cache_unsupported")

    def read(offset: int) -> str:
        start = base + offset
        end = payload.find(b"\0", start)
        if end < 0:
            raise HostClosureError("host_closure_cache_unsupported")
        return payload[start:end].decode("utf-8", "strict")

    entries = []
    try:
        for index in range(count):
            flags, key, value, osversion, hwcap = struct.unpack_from(
                "<iIIIQ", payload, table + 24 * index
            )
            entries.append(
                {
                    "soname": read(key),
                    "path": read(value),
                    "flags": flags,
                    "osversion": osversion,
                    "hwcap": hwcap,
                }
            )
    except UnicodeError:
        raise HostClosureError("host_closure_cache_unsupported") from None
    return entries


# --- path walking ------------------------------------------------------------------------


def _host(root: Path, path: str) -> str:
    return str(root) + path if str(root) != "/" else path


def _read(root: Path, path: str, member: str) -> bytes:
    try:
        descriptor = os.open(
            _host(root, path), os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
        )
    except FileNotFoundError:
        raise _refuse("member_missing", member) from None
    except OSError:
        raise _refuse("member_unreadable", member) from None
    try:
        size = os.fstat(descriptor).st_size
        if not 0 < size <= _MAX_FILE_BYTES:
            raise _refuse("member_changed", member)
        chunks, total = [], 0
        while total <= size:
            chunk = os.read(descriptor, 1 << 20)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        payload = b"".join(chunks)
        if len(payload) != size:
            raise _refuse("member_changed", member)
        return payload
    finally:
        os.close(descriptor)


def _step(root: Path, path: str, member: str) -> dict[str, Any]:
    try:
        info = os.lstat(_host(root, path))
    except FileNotFoundError:
        raise _refuse("member_missing", member) from None
    except OSError:
        raise _refuse("member_unreadable", member) from None
    mode = stat.S_IMODE(info.st_mode)
    base = {"path": path, "uid": info.st_uid, "gid": info.st_gid}
    if stat.S_ISLNK(info.st_mode):
        return {**base, "kind": "symlink", "target": os.readlink(_host(root, path))}
    if stat.S_ISDIR(info.st_mode):
        return {**base, "kind": "directory", "mode": format(mode, "04o")}
    if stat.S_ISREG(info.st_mode):
        return {**base, "kind": "file", "mode": format(mode, "04o")}
    raise _refuse("member_changed", member)


def resolve_chain(
    root: Path, path: str, member: str
) -> tuple[list[dict[str, Any]], str]:
    """Every directory, symlink and file visited resolving ``path``; also its real path."""

    if not isinstance(path, str) or not path.startswith("/") or path.startswith("//"):
        raise _refuse("resolution_ambiguous", member)
    pending = deque(PurePosixPath(path).parts[1:])
    steps = [_step(root, "/", member)]
    current = "/"
    links = 0
    while pending:
        name = pending.popleft()
        if name in ("", "."):
            continue
        if name == "..":
            current = str(PurePosixPath(current).parent)
            continue
        candidate = str(PurePosixPath(current) / name)
        step = _step(root, candidate, member)
        steps.append(step)
        if step["kind"] == "symlink":
            links += 1
            if links > _MAX_LINKS:
                raise _refuse("resolution_ambiguous", member)
            target = PurePosixPath(step["target"])
            if target.is_absolute():
                current = "/"
                pending = deque(target.parts[1:]) + pending
            else:
                pending = deque(target.parts) + pending
        elif step["kind"] == "directory":
            current = candidate
        else:
            if pending:
                raise _refuse("resolution_ambiguous", member)
            current = candidate
    return steps, current


def _file_capabilities_present(root: Path, path: str) -> bool:
    try:
        os.getxattr(_host(root, path), "security.capability", follow_symlinks=False)
    except OSError as error:
        if error.errno in (errno.ENODATA, errno.ENOTSUP, errno.EOPNOTSUPP):
            return False
        return True
    return True


# --- capture (derive pins from the host) ----------------------------------------------------


def _member_description(
    root: Path, path: str, member: str
) -> tuple[dict[str, Any], bytes]:
    steps, real = resolve_chain(root, path, member)
    payload = _read(root, real, member)
    return (
        {
            "path": path,
            "resolution": steps,
            "real_path": real,
            "sha256": sha256_hex(payload),
            "byte_count": len(payload),
        },
        payload,
    )


def capture_host_closure(
    executable_path: str = "/usr/bin/bwrap", *, root: Path = Path("/")
) -> dict[str, Any]:
    """Describe the closure the host would load for ``executable_path`` right now.

    This reads public static state only (ELF headers, the loader cache and file
    metadata); it never executes anything.  The result is what a new bundle pins.
    """

    executable, payload = _member_description(root, executable_path, "executable")
    dynamic = elf_dynamic(payload)
    if dynamic["interpreter"] is None or dynamic["rpath"] or dynamic["runpath"]:
        raise _refuse("resolution_ambiguous", "executable")
    interpreter, interpreter_payload = _member_description(
        root, dynamic["interpreter"], "interpreter"
    )
    interpreter_soname = PurePosixPath(dynamic["interpreter"]).name
    cache = parse_ld_so_cache(_read(root, _CACHE_PATH, "loader-cache"))
    by_soname: dict[str, list[dict[str, Any]]] = {}
    for entry in cache:
        by_soname.setdefault(entry["soname"], []).append(entry)
    libraries: dict[str, dict[str, Any]] = {}
    cache_entries: dict[str, list[dict[str, Any]]] = {}
    queue = deque(dynamic["needed"])
    while queue:
        soname = queue.popleft()
        if soname in libraries or soname == interpreter_soname:
            continue
        entries = by_soname.get(soname, [])
        if (
            len(entries) != 1
            or entries[0]["hwcap"] != 0
            or "glibc-hwcaps" in entries[0]["path"]
        ):
            raise _refuse("resolution_ambiguous", soname)
        description, library_payload = _member_description(
            root, entries[0]["path"], soname
        )
        library_dynamic = elf_dynamic(library_payload)
        if library_dynamic["rpath"] or library_dynamic["runpath"]:
            raise _refuse("resolution_ambiguous", soname)
        libraries[soname] = {
            "soname": soname,
            **description,
            "needed": library_dynamic["needed"],
        }
        cache_entries[soname] = [dict(entries[0])]
        queue.extend(library_dynamic["needed"])
    return {
        "schema_version": CLOSURE_SCHEMA,
        "trust_assumption": TRUST_ASSUMPTION,
        "launch_environment": "empty",
        "executable": {**executable, "needed": dynamic["needed"]},
        "interpreter": {
            **interpreter,
            "soname": interpreter_soname,
            "pt_interp": dynamic["interpreter"],
        },
        "libraries": [libraries[name] for name in sorted(libraries)],
        "loader_inputs": {
            "cache": {
                "path": _CACHE_PATH,
                "resolution": resolve_chain(root, _CACHE_PATH, "loader-cache")[0],
                "entries": cache_entries,
            },
            "preload": {"path": _PRELOAD_PATH, "state": "absent"},
            "search_path": "empty-environment-without-rpath-or-runpath-cache-entries-only",
            "hardware_capabilities": "pinned-cache-entries-carry-no-hwcap-or-glibc-hwcaps-variant",
        },
    }


# --- verification (immediately before each launch) --------------------------------------------


def _check_chain(
    pinned: Sequence[Mapping[str, Any]],
    actual: Sequence[Mapping[str, Any]],
    member: str,
    trusted_uid: int,
) -> None:
    if list(pinned) != list(actual):
        raise _refuse("member_changed", member)
    for step in actual:
        if step["uid"] != trusted_uid:
            raise _refuse("member_writable", member)
        if step["kind"] != "symlink" and int(step["mode"], 8) & 0o022:
            raise _refuse("member_writable", member)


def _check_member(
    root: Path, pinned: Mapping[str, Any], member: str, trusted_uid: int
) -> tuple[bytes, dict[str, Any]]:
    steps, real = resolve_chain(root, pinned["path"], member)
    if real != pinned["real_path"]:
        raise _refuse("member_changed", member)
    _check_chain(pinned["resolution"], steps, member, trusted_uid)
    final = steps[-1]
    if final["kind"] != "file":
        raise _refuse("member_changed", member)
    if int(final["mode"], 8) & 0o7000 or _file_capabilities_present(root, real):
        raise _refuse("member_privileged", member)
    payload = _read(root, real, member)
    if len(payload) != pinned["byte_count"] or sha256_hex(payload) != pinned["sha256"]:
        raise _refuse("member_changed", member)
    return payload, elf_dynamic(payload)


def verify_host_closure(
    pinned: Mapping[str, Any], *, root: Path = Path("/"), trusted_uid: int = 0
) -> dict[str, Any]:
    """Recheck the pinned closure against the host; return the retained check facts.

    ``root`` and ``trusted_uid`` exist so tests can use a synthetic tree owned by
    the test user; the launch path always uses ``/`` and root (uid 0).
    """

    if (
        not isinstance(pinned, Mapping)
        or pinned.get("schema_version") != CLOSURE_SCHEMA
    ):
        raise HostClosureError("host_closure_description_invalid")
    try:
        executable = pinned["executable"]
        interpreter = pinned["interpreter"]
        libraries = {entry["soname"]: entry for entry in pinned["libraries"]}
        cache_pin = pinned["loader_inputs"]["cache"]
        preload_pin = pinned["loader_inputs"]["preload"]
    except (KeyError, TypeError):
        raise HostClosureError("host_closure_description_invalid") from None
    if (
        pinned.get("launch_environment") != "empty"
        or preload_pin.get("state") != "absent"
    ):
        raise HostClosureError("host_closure_description_invalid")

    _payload, dynamic = _check_member(root, executable, "executable", trusted_uid)
    if (
        dynamic["interpreter"] != interpreter["pt_interp"]
        or interpreter["path"] != interpreter["pt_interp"]
        or dynamic["rpath"]
        or dynamic["runpath"]
        or dynamic["needed"] != executable["needed"]
    ):
        raise _refuse("resolution_ambiguous", "executable")
    _check_member(root, interpreter, "interpreter", trusted_uid)

    if os.path.lexists(_host(root, _PRELOAD_PATH)):
        raise _refuse("resolution_ambiguous", "preload")
    cache_steps, _real = resolve_chain(root, cache_pin["path"], "loader-cache")
    _check_chain(cache_pin["resolution"], cache_steps, "loader-cache", trusted_uid)
    by_soname: dict[str, list[dict[str, Any]]] = {}
    for entry in parse_ld_so_cache(_read(root, cache_pin["path"], "loader-cache")):
        by_soname.setdefault(entry["soname"], []).append(entry)

    reachable: set[str] = set()
    queue = deque(executable["needed"])
    allowed_without_file = {interpreter["soname"]}
    while queue:
        soname = queue.popleft()
        if soname in reachable or soname in allowed_without_file:
            continue
        reachable.add(soname)
        library = libraries.get(soname)
        if library is None:
            raise _refuse("resolution_ambiguous", soname)
        if by_soname.get(soname) != cache_pin["entries"].get(soname):
            raise _refuse("resolution_ambiguous", soname)
        if cache_pin["entries"][soname][0]["path"] != library["path"]:
            raise _refuse("resolution_ambiguous", soname)
        _library_payload, library_dynamic = _check_member(
            root, library, soname, trusted_uid
        )
        if (
            library_dynamic["rpath"]
            or library_dynamic["runpath"]
            or library_dynamic["needed"] != library["needed"]
        ):
            raise _refuse("resolution_ambiguous", soname)
        queue.extend(library_dynamic["needed"])
    if reachable != set(libraries):
        raise _refuse("resolution_ambiguous", "closure")
    return {
        "closure_sha256": closure_sha256(pinned),
        "member_count": 2 + len(libraries),
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Print the closure the host would load now (read-only); used to derive a new bundle's pins."""

    import argparse
    import json

    parser = argparse.ArgumentParser(prog="python -m caplab.revbench.host_closure")
    parser.add_argument("--executable", default="/usr/bin/bwrap")
    args = parser.parse_args(argv)
    try:
        document = capture_host_closure(args.executable)
    except HostClosureError as error:
        print(str(error))
        return 2
    print(json.dumps(document, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
