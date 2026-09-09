"""Prepare a source-pinned Codex child expectation, independent of trace contents."""

from contextlib import ExitStack
from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath

from caplab.native_capture_invocation import _digest
from caplab.native_launch_configuration import _validated_launch_configuration
from caplab.task_capture_verify import _digest as _require_digest, _identity, _open, _read_file, _require


_PLATFORM = 'node_modules/@openai/codex-linux-x64'
_BINARY = _PLATFORM + '/vendor/x86_64-unknown-linux-musl/bin/codex'
_SOURCES = (
    ('bin/codex.js', '61b0194f3bb6534439c8d26a3ed57d0805f84b884588b761795323eeb92fcf70'),
    ('package.json', '302ed64d0846795501768be9f60f78133688c0c09162c76e80a8a04b045664cb'),
    (_PLATFORM + '/package.json', '7faa8bf27c4647662dae29b7e429b3dc394d718d273af0045e1aa99d2fb1bb37'),
)


@dataclass(frozen=True)
class CodexChildSourceEvidence:
    expected_invocation_sha256: str
    expected_launch_sha256: str
    expected_binary_sha256: str
    max_installation_bytes: int


def _inspect_sources(root: Path, evidence: CodexChildSourceEvidence) -> list[dict]:
    _require(root.is_absolute() and root != Path('/') and root.resolve() == root,
             'installation root must be a resolved absolute directory')
    remaining = evidence.max_installation_bytes
    records, identities = [], []
    with ExitStack() as stack:
        directories = {'.': stack.enter_context(_open(None, root, directory=True))}
        identities.append((None, root, _identity(os.fstat(directories['.']))))
        for relative, expected in (*_SOURCES, (_BINARY, evidence.expected_binary_sha256)):
            parts = PurePosixPath(relative).parts
            parent, prefix = directories['.'], ''
            for part in parts[:-1]:
                prefix = prefix + '/' + part if prefix else part
                if prefix not in directories:
                    directories[prefix] = stack.enter_context(_open(parent, part, directory=True))
                    identities.append((parent, part, _identity(os.fstat(directories[prefix]))))
                parent = directories[prefix]
            before = _identity(os.stat(parts[-1], dir_fd=parent, follow_symlinks=False))
            _, size, sha = _read_file(parent, parts[-1], min(remaining, 1024 * 1024)
                                     if relative != _BINARY else remaining, retain=False)
            _require(sha == expected, 'unsupported or changed Codex source: ' + relative)
            identities.append((parent, parts[-1], before))
            records.append({'path': relative, 'bytes': size, 'sha256': sha})
            remaining -= size
        try:
            os.stat('.modules.yaml', dir_fd=directories['node_modules'], follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError('unsupported package-manager ownership metadata')
        for parent, name, before in identities:
            _require(_identity(os.stat(name, dir_fd=parent, follow_symlinks=False)) == before,
                     'installation changed during source inspection')
    return records


def prepare_codex_child_configuration(
    policy_path: Path, invocation: dict, launch: dict, installation_root: Path, *,
    evidence: CodexChildSourceEvidence,
) -> dict:
    """Read selected sources and prepare a conditional expectation; never launch or persist.

    Caller owns independent anchors, stable trusted filesystem ancestors and source
    lifetime. Namespace/runtime assumptions still require separate verification.
    Borrowed configuration objects must not change during this synchronous call.
    """
    _require(isinstance(evidence, CodexChildSourceEvidence), 'invalid Codex child source evidence')
    _require_digest(evidence.expected_binary_sha256)
    _require(type(evidence.max_installation_bytes) is int and 0 < evidence.max_installation_bytes <= 1024**3,
             'invalid installation byte allowance')
    rebuilt = _validated_launch_configuration(policy_path, invocation, launch,
        expected_invocation_sha256=evidence.expected_invocation_sha256,
        expected_launch_sha256=evidence.expected_launch_sha256)
    _require(rebuilt['command'][0] == 'codex', 'child source profile requires Codex')
    environment = dict(rebuilt['environment'])
    _require(not {'NODE_OPTIONS', 'NODE_PATH', 'npm_config_user_agent', 'npm_execpath'} & environment.keys(),
             'unsupported Node or package-manager environment')
    root = Path(installation_root)
    sources = _inspect_sources(root, evidence)
    for key in ('CODEX_MANAGED_BY_NPM', 'CODEX_MANAGED_BY_BUN', 'CODEX_MANAGED_BY_PNPM', 'CODEX_MANAGED_BY_VITE_PLUS'):
        environment.pop(key, None)
    environment.update(CODEX_MANAGED_PACKAGE_ROOT='/opt/native', CODEX_MANAGED_BY_NPM='1')
    executable = '/opt/native/' + _BINARY
    prepared = {'schema': 'caplab.codex-child-configuration/v1', 'profile': 'codex-0.153.4-linux-x64/v1',
        'invocation_sha256': evidence.expected_invocation_sha256,
        'launch_configuration_sha256': evidence.expected_launch_sha256,
        'installation_root': str(root), 'source_files': sources,
        'executable': executable, 'command': [executable] + rebuilt['command'][1:],
        'environment': environment, 'cwd': rebuilt['cwd'],
        'namespace_assumptions': {
            'node_platform': 'linux', 'node_arch': 'x64', 'installation_mount': '/opt/native',
            'entrypoint_symlink': {'/toolbin/codex': '/opt/native/bin/codex.js'},
            'absent_paths': ['/node_modules', '/opt/node_modules', '/toolbin/node_modules'],
            'source_mount_readonly_and_unchanged': True, 'node_default_module_resolution': True},
        'selected_source_bytes_verified': True, 'namespace_assumptions_verified': False,
        'executed_bytes_verified': False, 'execution_authorized': False,
        'binding_complete': False, 'study_eligible': False}
    prepared['child_configuration_sha256'] = _digest(prepared)
    return prepared
