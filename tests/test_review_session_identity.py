"""Synthetic session contradiction checks; no native calls or historical evidence."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from caplab.review_dissent.native import assess_native_review_model, build_native_review_capture, load_native_review_instrument, render_native_review_cell

MODEL='claude-fable-5'
SUBJECT={'native_harness_id':'claude-code','model_id':MODEL}


def events():
    return [{'type':'system','subtype':'init','model':MODEL,'session_id':'session-A'},
            {'type':'assistant','session_id':'session-A','message':{'model':MODEL,'content':[]}},
            {'type':'result','subtype':'success','is_error':False,'session_id':'session-A'}]


def raw(trace):
    return b''.join((json.dumps(event,ensure_ascii=False)+'\n').encode() for event in trace)


class NativeSessionIdentityTests(unittest.TestCase):
    def assess(self, trace):
        before=copy.deepcopy(trace); content=raw(trace)
        result=assess_native_review_model(SUBJECT,content)
        self.assertEqual(trace,before)
        self.assertEqual(result['native_stdout_sha256'],hashlib.sha256(content).hexdigest())
        return result

    def test_explicit_root_conflicts_prevent_model_match(self):
        for index in (0,1,2):
            with self.subTest(index=index):
                trace=events();trace[index]['session_id']='session-B'
                result=self.assess(trace)
                self.assertEqual(result['status'],'model-unverified')
                self.assertEqual(result['reason'],'native-session-evidence-invalid')
                self.assertTrue(result['session_errors'])

    def test_invalid_explicit_ids_prevent_match_without_normalization(self):
        for invalid in (None,'','  ',1,False,[],{}):
            with self.subTest(invalid=invalid):
                trace=events();trace[1]['session_id']=invalid
                self.assertEqual(self.assess(trace)['status'],'model-unverified')
        trace=events();trace[1]['session_id']='session-A '
        self.assertEqual(self.assess(trace)['status'],'model-unverified')

    def test_matching_ids_are_observations_not_full_linkage(self):
        result=self.assess(events())
        self.assertEqual(result['status'],'native-model-match')
        self.assertEqual([e['session_id'] for e in result['session_ids']],['session-A']*3)
        self.assertNotIn('session_errors',result)
        trace=events();del trace[1]['session_id']
        self.assertEqual(self.assess(trace)['status'],'native-model-match')
        trace=events();del trace[1]
        self.assertEqual(self.assess(trace)['status'],'model-unverified')

    def test_documented_child_scope_is_separate_from_root(self):
        for kind in ('assistant','user','stream_event','tool_progress'):
            with self.subTest(kind=kind):
                trace=events();child={'type':kind,'session_id':'child-B','parent_tool_use_id':'tool-1'}
                if kind=='assistant':child['message']={'model':MODEL,'content':[]}
                if kind=='stream_event':child['event']={'type':'message_stop'}
                trace.insert(2,child)
                result=self.assess(trace)
                self.assertEqual(result['status'],'native-model-match')
                self.assertEqual(result['session_ids'][2]['parent_tool_use_id'],'tool-1')
                self.assertNotIn('session_errors',result)

    def test_invalid_scope_cannot_hide_a_root_conflict(self):
        for invalid in ('',0,False,[],{}):
            trace=events();trace[1].update(session_id='session-B',parent_tool_use_id=invalid)
            self.assertEqual(self.assess(trace)['status'],'model-unverified')
        for index in (0,2):
            trace=events();trace[index].update(session_id='session-B',parent_tool_use_id='fake-child')
            self.assertEqual(self.assess(trace)['status'],'model-unverified')

    def test_nested_quoted_ids_are_not_session_observations(self):
        trace=events()
        trace[1]['message']['content']=[{'type':'text','text':'session_id: different\u2028quoted'},
            {'type':'tool_use','id':'tool-1','name':'Read','input':{'session_id':'different'}}]
        result=self.assess(trace)
        self.assertEqual(result['status'],'native-model-match')
        self.assertEqual(len(result['session_ids']),3)

    def test_model_mismatch_precedence_is_preserved(self):
        trace=events();trace[1].update(session_id='different')
        trace[1]['message']['model']='another-model'
        result=self.assess(trace)
        self.assertEqual(result['status'],'model-mismatch')
        self.assertEqual(result['reason'],'native-model-substitution-or-mismatch')
        self.assertTrue(result['session_errors'])

    def test_session_conflict_withholds_score_and_preserves_assignment(self):
        instrument=load_native_review_instrument(Path(__file__).parents[1]/'docs/product/studies/review-dissent-001/native-instrument.json')
        with tempfile.TemporaryDirectory() as directory:
            task=Path(directory)/'task';render_native_review_cell(instrument,'r03',task)
            (task/'REVIEW.json').write_text(json.dumps({'verdict':'needs_revision','findings':[],'summary':'Synthetic review.'}))
            def capture(trace):
                return build_native_review_capture(instrument,cell_id='r03',subject_id='fable',task_root=task,
                    native_jsonl=raw(trace),status='completed',observation_sha256='a'*64,campaign_manifest_sha256='b'*64)
            baseline=capture(events());trace=events();trace[1]['session_id']='different'
            result=capture(trace)
            self.assertIsNotNone(baseline['mechanical']['score'])
            self.assertIsNone(result['mechanical']['score'])
            self.assertEqual(result['outcome'],'identity-unavailable')
            self.assertEqual(result['status'],baseline['status'])
            self.assertEqual(result['subject_seal'],baseline['subject_seal'])


if __name__=='__main__':unittest.main()
