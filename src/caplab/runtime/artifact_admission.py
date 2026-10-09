"""One-shot artifact-rater helpers/roots using existing native SDK custody.

This names a new namespace administration; it establishes no scientific Binding
qualification or provider-authenticated account identity.
"""
from __future__ import annotations
import copy
import json
from datetime import datetime
from pathlib import Path
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.runtime.native_admission import NativeCalibrationAdmission, initialize_domain
from caplab.revbench.custody import LiveExecutionCustodyError, _ensure_owned_directory
from caplab.revbench.shared_admission import SharedAdmissionEnrollment, _read, _retain

SCHEMA = 'caplab-artifact-rater-shared-admission/1'

class ArtifactRaterAdmission(NativeCalibrationAdmission):
    gate_destination = '/dev/caplab-launch-gate.py'

    @classmethod
    def read(cls, path, manifest_path, output_root, model, effort):
        raw = _read(Path(path)); d = json.loads(raw)
        fields = {'schema_version','manifest_sha256','output_root','model','effort','expires_at',
                  'native_home','codex_executable','codex_sha256','enrollment_path','enrollment_sha256',
                  'native_policy_path','native_policy_sha256'}
        if not isinstance(d, dict) or set(d) != fields or any(not isinstance(d[k],str) or not d[k] for k in fields):
            raise LiveExecutionCustodyError('artifact_enrollment_invalid')
        output_root = Path(output_root).absolute()
        if (d['schema_version'] != SCHEMA or d['manifest_sha256'] != sha256_hex(_read(Path(manifest_path)))
            or d['output_root'] != str(output_root) or d['model'] != model or d['effort'] != effort):
            raise LiveExecutionCustodyError('artifact_identity_mismatch')
        try:
            expires = datetime.fromisoformat(d['expires_at'])
            if expires.utcoffset() is None:
                raise ValueError('timezone missing')
        except ValueError as error:
            raise LiveExecutionCustodyError('artifact_expiry_invalid') from error
        for k in ('native_home','codex_executable','enrollment_path','native_policy_path'):
            if not Path(d[k]).is_absolute():
                raise LiveExecutionCustodyError('artifact_path_invalid')
        if (sha256_hex(_read(Path(d['codex_executable']))) != d['codex_sha256']
            or sha256_hex(_read(Path(d['enrollment_path']))) != d['enrollment_sha256']
            or sha256_hex(_read(Path(d['native_policy_path']))) != d['native_policy_sha256']):
            raise LiveExecutionCustodyError('artifact_input_pin_changed')
        if not (Path(d['native_home']) / '.codex').is_dir():
            raise LiveExecutionCustodyError('artifact_native_home_unavailable')
        e = SharedAdmissionEnrollment.read(d['enrollment_path'])
        from caplab.catalog.discovery import admitted, load_native_policy
        policy = load_native_policy(Path(d['native_policy_path']))
        if (e.selection.native['model_id'] != model or e.selection.native['effort'] != effort
            or e.selection.native['native_harness_id'] != 'codex'
            or not admitted(e.selection.native, policy)):
            raise LiveExecutionCustodyError('artifact_catalog_native_tuple_mismatch')
        home = e.selection.profile['config_home']
        if home is not None and home != str(Path(d['native_home']) / '.codex'):
            raise LiveExecutionCustodyError('artifact_catalog_config_home_mismatch')
        profile = {'schema_version':'caplab-artifact-rater-declared-profile/1',
            'profile_id':e.selection.profile['id'],
            **{k:e.selection.profile[k] for k in ('host','account_id','config_home')},
            'native_home':d['native_home']}
        if sha256_hex(canonical_json(profile)) != e.document['credential_profile_sha256']:
            raise LiveExecutionCustodyError('artifact_declared_profile_pin_mismatch')
        self = cls(); self.parent = output_root; self.domain = initialize_domain(output_root)
        if (e.document['custody_domain_id'] != self.domain or e.document['caller_id'] != 'caplab'
            or 'sdk_source_tree_sha256' not in e.document):
            raise LiveExecutionCustodyError('artifact_custody_mapping_mismatch')
        self.family = 'artifact-rater'; self.configuration = copy.deepcopy(d)
        self.manifest = {'campaign_id':'artifact-rater-'+d['manifest_sha256'],
            'manifest_sha256':d['manifest_sha256'],'expires_at':d['expires_at']}
        self.root = _ensure_owned_directory(output_root / 'shared-launches','assignments')
        self.enrollments = {'rater':e}
        from caplab.runtime import native_admission, canonical
        from caplab.revbench import custody, shared_admission, process_tree, codex
        from caplab.retrieval import exec_gate
        from caplab import artifact_rater_cli
        modules=(native_admission,canonical,custody,shared_admission,process_tree,codex,exec_gate,artifact_rater_cli)
        self.receipt={'schema_version':SCHEMA,'configuration':d,'config_file_sha256':sha256_hex(raw),
            'enrollment':e.document,'declared_profile':profile,
            'identity_basis':'operator-declared-account-domain','authenticated_provider_identity':False,
            'containment':'artifact-native-read-only-root-explicit-gate-v1',
            'runtime_sources':{m.__name__:sha256_hex(Path(m.__file__).read_bytes()) for m in modules}}
        self.receipt['runtime_sources'][__name__]=sha256_hex(Path(__file__).read_bytes())
        self.receipt_sha=sha256_hex(canonical_json(self.receipt))
        if not (output_root/'artifact-admission.json').exists() and any(
            (output_root/p).exists() for p in ('rater.json','scores','manifest.json')):
            raise LiveExecutionCustodyError('artifact_existing_unenrolled_output')
        _retain(output_root/'shared-launches','enrollment-'+self.receipt_sha+'.json',self.receipt)
        _retain(output_root,'artifact-admission.json',{'enrollment_sha256':self.receipt_sha})
        return self

    def describe(self):
        return {**copy.deepcopy(self.receipt),'covered_launches':['codex-version','artifact-scoring-attempt'],
            'residual_scope':'Other helpers/producers and unenrolled artifact runs are not covered.'}

    def run_native(self, command, *, cwd, assignment, timeout, input=None):
        """Execute exactly the native artifact argv, inside an observed namespace."""
        d=self.configuration
        if sha256_hex(_read(Path(d['codex_executable']))) != d['codex_sha256']:
            raise LiveExecutionCustodyError('artifact_executable_changed')
        if not isinstance(command,list) or command[:1] != ['codex']:
            raise LiveExecutionCustodyError('artifact_command_invalid')
        cwd=Path(cwd).resolve(strict=True)
        if command != ['codex','--version']:
            expected=['codex','exec','--ignore-user-config','--ignore-rules','--strict-config',
                '--sandbox','read-only','--cd',str(cwd),'--skip-git-repo-check','--model',d['model'],
                '--config',f'model_reasoning_effort="{d["effort"]}"','--output-schema',
                str(cwd.parent/'schema.json'),'--json','--output-last-message',
                str(cwd.parent/'last-message.txt'),'-']
            if command != expected or input is None:
                raise LiveExecutionCustodyError('artifact_command_invalid')
        elif input is not None:
            raise LiveExecutionCustodyError('artifact_version_input_invalid')
        if not cwd.is_relative_to(self.parent):
            raise LiveExecutionCustodyError('artifact_workspace_outside_custody')
        # Same host-native filesystem reads and shared network as the original
        # CLI; only the output tree, temporary workspace and native Codex home
        # are writable. Custody is overmounted read-only inside the namespace.
        argv=['/usr/bin/bwrap','--unshare-all','--share-net','--new-session','--die-with-parent',
            '--ro-bind','/','/','--dev','/dev','--proc','/proc','--tmpfs','/tmp',
            '--ro-bind',d['codex_executable'],d['codex_executable'],
            '--bind',str(self.parent),str(self.parent),
            '--bind',d['native_home']+'/.codex',d['native_home']+'/.codex',
            '--ro-bind',str(self.parent/'shared-launches'),str(self.parent/'shared-launches'),
            '--chdir',str(cwd),'--setenv','HOME',d['native_home'],
            '--setenv','CODEX_HOME',d['native_home']+'/.codex',
            '--setenv','PATH',str(Path(d['codex_executable']).parent)+':/usr/bin:/bin',
            '--',d['codex_executable']]+command[1:]
        return super().run(argv,cwd=cwd,subject='rater',assignment=assignment,timeout=timeout,input=input,
            native_launch_sha256=sha256_hex(canonical_json({'codex_sha256':d['codex_sha256'],
                'command':command,'timeout_seconds':timeout,'stdin_sha256':None if input is None else sha256_hex(input)})))
