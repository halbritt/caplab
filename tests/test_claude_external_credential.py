import hashlib
import json
import os
from pathlib import Path
import tempfile
import time
import unittest

from caplab.claude_external_credential import open_claude_external_credential
from caplab.codex_external_credential import ExternalCredentialError


class ClaudeCredentialTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/'credentials.json'
        self.access='synthetic-access-token-for-native-review-0001'
        self.refresh='synthetic-refresh-token-never-delivered-0002'
        self.document={'claudeAiOauth':{'accessToken':self.access,'refreshToken':self.refresh,
            'expiresAt':int((time.time()+3600)*1000),'scopes':['user:inference']}}
        self.write()

    def write(self):
        self.path.write_text(json.dumps(self.document));self.path.chmod(0o600)
        self.digest=hashlib.sha256(self.path.read_bytes()).hexdigest()

    def open(self,**kwargs):
        return open_claude_external_credential(self.path,expected_source_sha256=self.digest,
            minimum_access_lifetime_seconds=kwargs.get('lifetime',1000))

    def test_sealed_descriptor_contains_only_access_and_closes(self):
        with self.open() as credential:
            fd=credential.descriptor
            self.assertEqual(os.read(fd,65536),self.access.encode())
            with self.assertRaises(OSError):os.write(fd,b'overwrite')
            self.assertNotIn(self.access,repr(credential))
            self.assertNotIn(self.refresh,repr(credential))
        with self.assertRaises(OSError):os.fstat(fd)
        self.assertEqual(json.loads(self.path.read_text()),self.document)

    def test_guard_catches_both_tokens_across_chunks_and_allows_code(self):
        with self.open() as credential:
            for secret in (self.access,self.refresh):
                guard=credential.quarantine_factory()
                retained=guard.feed(b'ordinary source '+secret[:12].encode())
                retained+=guard.feed(secret[12:].encode()+b' trailing')+guard.finish()
                self.assertTrue(guard.quarantined)
                self.assertNotIn(secret.encode(),retained)
            guard=credential.quarantine_factory();raw=b'def max_items(): return 1\n'
            self.assertEqual(guard.feed(raw)+guard.finish(),raw)
            self.assertFalse(guard.quarantined)

    def test_expiry_scope_and_pin_refuse_before_delivery(self):
        with self.assertRaises(ExternalCredentialError):
            with self.open(lifetime=7200):pass
        self.document['claudeAiOauth']['scopes']=[];self.write()
        with self.assertRaises(ExternalCredentialError):
            with self.open():pass
        self.document['claudeAiOauth']['scopes']=['user:inference'];self.write()
        self.digest='0'*64
        with self.assertRaises(ExternalCredentialError):
            with self.open():pass

    def test_unsafe_source_and_duplicate_json_have_fixed_diagnostics(self):
        self.path.chmod(0o644)
        with self.assertRaises(ExternalCredentialError):
            with self.open():pass
        self.path.chmod(0o600)
        self.path.write_text('{"claudeAiOauth":{},"claudeAiOauth":{"accessToken":"'+self.access+'"}}')
        self.digest=hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaises(ExternalCredentialError) as caught:
            with self.open():pass
        self.assertNotIn(self.access,str(caught.exception))
        target=self.path.with_name('link');target.symlink_to(self.path)
        with self.assertRaises(ExternalCredentialError):
            with open_claude_external_credential(target,expected_source_sha256=self.digest,minimum_access_lifetime_seconds=100):pass


if __name__=='__main__':unittest.main()
