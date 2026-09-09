"""Identify effective native launch configuration separately from its prepared base."""

from dataclasses import dataclass
from pathlib import Path

from caplab.exec_trace import inspect_exec_trace, inspect_exec_termination
from caplab.native_capture_invocation import _digest
from caplab.native_runtime import _validated_invocation
from caplab.task_capture_verify import _digest as _require_digest, _require


@dataclass(frozen=True)
class NativeLaunchContext:
    profile: str
    fixture_port: int | None = None


@dataclass(frozen=True)
class NativeLaunchTraceEvidence:
    expected_invocation_sha256: str
    expected_launch_sha256: str
    expected_trace_sha256: str
    expected_pid: int
    max_trace_bytes: int


def build_native_launch_configuration(
    policy_path: Path, invocation: dict, *, expected_invocation_sha256: str,
    context: NativeLaunchContext,
) -> dict:
    """Build a prospective configuration, without authorization, persistence or I/O beyond policy reads."""
    plan = _validated_invocation(policy_path, invocation, expected_invocation_sha256)
    _require(isinstance(context, NativeLaunchContext), 'invalid native launch context')
    command, environment = list(plan['command']), dict(plan['environment'])
    if context.profile == 'canonical-native/v1':
        _require(context.fixture_port is None, 'canonical launch cannot have a fixture port')
        purpose = 'native-capture'
    elif context.profile == 'codex-scripted-local/v1':
        _require(plan['base_subject']['native_harness_id'] == 'codex', 'scripted local launch requires Codex')
        port = context.fixture_port
        _require(type(port) is int and 1 <= port <= 65535, 'invalid local fixture port')
        endpoint = f'http://127.0.0.1:{port}'
        command[-2:-2] = ['-c', f'chatgpt_base_url="{endpoint}"', '-c', f'openai_base_url="{endpoint}"',
                          '-c', 'check_for_update_on_startup=false']
        environment.update(CODEX_REFRESH_TOKEN_URL_OVERRIDE=endpoint + '/oauth/token',
            RUST_LOG='codex_core::stream_events_utils=trace,codex_core::tools::router=trace,'
                     'codex_core::tools::code_mode=trace,codex_core::codex=debug')
        purpose = 'scripted-protocol-diagnostic'
    else:
        raise ValueError('unsupported native launch profile')
    launch = {'schema': 'caplab.native-launch-configuration/v1',
              'invocation_sha256': plan['invocation_sha256'], 'profile': context.profile,
              'fixture_port': context.fixture_port, 'command': command,
              'environment': environment, 'cwd': plan['cwd'],
              'canonical_invocation_agrees': context.profile == 'canonical-native/v1', 'purpose': purpose,
              'execution_authorized': False, 'binding_complete': False, 'study_eligible': False}
    launch['launch_configuration_sha256'] = _digest(launch)
    return launch


def inspect_native_launch_trace(
    policy_path: Path, invocation: dict, launch: dict, trace_path: Path, *,
    evidence: NativeLaunchTraceEvidence, require_termination: bool = False,
) -> dict:
    """Rebuild an anchored launch and compare its exact command with exec evidence.

    The caller owns independent anchors, authenticated PID, tracer provenance,
    cwd/source linkage and bounded loading of the borrowed configuration objects.
    A successful exec is neither native task success nor a complete Binding.
    Required termination names this entrypoint PID, not a child binary's outcome.
    """
    _require(isinstance(evidence, NativeLaunchTraceEvidence), 'invalid native launch trace evidence')
    _require(type(require_termination) is bool, 'invalid termination requirement')
    _require_digest(evidence.expected_launch_sha256)
    _require(isinstance(launch, dict), 'invalid native launch configuration')
    unsigned = {key: value for key, value in launch.items() if key != 'launch_configuration_sha256'}
    _require(launch.get('launch_configuration_sha256') == evidence.expected_launch_sha256
             and _digest(unsigned) == evidence.expected_launch_sha256, 'native launch configuration hash differs')
    rebuilt = build_native_launch_configuration(policy_path, invocation,
        expected_invocation_sha256=evidence.expected_invocation_sha256,
        context=NativeLaunchContext(launch.get('profile'), launch.get('fixture_port')))
    _require(_digest(rebuilt) == _digest(launch), 'native launch differs from its declared profile')
    inspector = inspect_exec_termination if require_termination else inspect_exec_trace
    check = inspector(trace_path, expected_trace_sha256=evidence.expected_trace_sha256,
        expected_pid=evidence.expected_pid, expected_executable='/toolbin/' + rebuilt['command'][0],
        expected_command=rebuilt['command'], expected_environment=rebuilt['environment'],
        max_trace_bytes=evidence.max_trace_bytes)
    return {'schema': 'caplab.native-launch-exec-link/v2' if require_termination else 'caplab.native-launch-exec-link/v1',
            'invocation_sha256': evidence.expected_invocation_sha256,
            'launch_configuration_sha256': evidence.expected_launch_sha256,
            'profile': rebuilt['profile'], 'canonical_invocation_agrees': rebuilt['canonical_invocation_agrees'],
            'entrypoint_argv_environment_agree': True,
            'exec_trace': check['exec_trace'] if require_termination else check,
            **({'entrypoint_termination': check} if require_termination else {}),
            'cwd_source_linked': False, 'binding_complete': False,
            'native_capture_complete': None, 'study_eligible': False}
