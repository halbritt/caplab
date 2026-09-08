import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from caplab.code_agreement import build_code_agreement_report, build_code_reference_report
from test_code_agreement import document


def references(values):
    return {"schema_version": "caplab-code-reference-input/1", "reference_id": "synthetic-reference",
            "judgments": [{"slot": str(i), "code_id": "C1", "value": value,
                           "evidence_locator": f"synthetic://reference/{i}"}
                          for i, value in enumerate(values)]}


class CodeReferenceTests(unittest.TestCase):
    def test_identically_wrong_coders_have_perfect_kappa_and_zero_reference_agreement(self):
        source = document([(True, True), (False, False)] * 2)
        reference = references([False, True] * 2)
        report = build_code_reference_report(source, reference)
        self.assertEqual(report['agreement']['codes'][0]['kappa'], 1)
        self.assertEqual(report['agreement'], build_code_agreement_report(source))
        for row in report['reference_comparisons']:
            self.assertEqual(row['reference_joint_counts'], {'00': 0, '01': 2, '10': 2, '11': 0})
            self.assertEqual(row['reference_agreement'], 0)
            self.assertEqual(row['reference_coverage'], 1)
        self.assertIn('unverified reference', report['interpretation'])
        self.assertNotIn('passed', report)

    def test_asymmetric_matrix_has_explicit_reference_then_coder_orientation(self):
        ref = [False]*5 + [True]*5
        labels = [False]*3 + [True]*2 + [False] + [True]*4
        report = build_code_reference_report(document(list(zip(labels,labels))), references(ref))
        self.assertEqual(report['reference_joint_axes'], ['reference','coder'])
        row = report['reference_comparisons'][0]
        self.assertEqual(row['reference_joint_counts'], {'00':3,'01':2,'10':1,'11':4})
        self.assertEqual(row['reference_agreement'], .7)
        self.assertEqual(row['positive_reference_agreement'], .8)
        self.assertEqual(row['negative_reference_agreement'], .6)
        self.assertEqual(row['positive_reference_labels'], 5)
        self.assertEqual(row['negative_reference_labels'], 5)

    def test_reference_and_coder_missingness_do_not_disappear_from_denominators(self):
        source = document([(True,None),(True,False),(False,True),(True,True)])
        source['judgments'] = [j for j in source['judgments'] if (j['slot'],j['coder_id']) != ('0','a')]
        report = build_code_reference_report(source,references([True,False,None]))
        a,b = report['reference_comparisons']
        for row in (a,b):
            self.assertEqual(row['expected_labels'],4)
            self.assertEqual(row['known_reference_labels'],2)
            self.assertEqual(row['missing_reference_labels'],1)
            self.assertEqual(row['unavailable_reference_labels'],1)
            self.assertEqual(row['positive_reference_labels'],1)
            self.assertEqual(row['compared_labels'],1)
            self.assertEqual(row['reference_coverage'],.5)
            self.assertIsNone(row['positive_reference_agreement'])
        self.assertEqual(a['missing_judgments_on_known_references'],1)
        self.assertEqual(a['unavailable_judgments_on_known_references'],0)
        self.assertEqual(a['reference_agreement'],0)
        self.assertEqual(b['missing_judgments_on_known_references'],0)
        self.assertEqual(b['unavailable_judgments_on_known_references'],1)
        self.assertEqual(b['reference_agreement'],1)

    def test_all_missing_or_unavailable_reference_labels_yield_null_rates(self):
        for ref in (references([]),references([None,None])):
            report = build_code_reference_report(document([(False,False),(True,True)]),ref)
            for row in report['reference_comparisons']:
                self.assertEqual(row['known_reference_labels'],0)
                self.assertEqual(row['compared_labels'],0)
                for field in ('reference_coverage','reference_agreement','positive_reference_agreement','negative_reference_agreement'):
                    self.assertIsNone(row[field])

    def test_absent_class_is_undefined_and_empty_world_codes_stay_visible(self):
        source=document([(False,False)])
        source['worlds']['empty']=['C1','C2']
        report=build_code_reference_report(source,references([False]))
        self.assertEqual(len(report['reference_comparisons']),6)
        for row in report['reference_comparisons']:
            self.assertIsNone(row['positive_reference_agreement'])
            if row['world']=='empty':
                self.assertEqual(row['expected_labels'],0)
                self.assertIsNone(row['reference_agreement'])
            else:
                self.assertEqual(row['negative_reference_agreement'],1)

    def test_world_code_join_cannot_cross_worlds_with_the_same_code_name(self):
        source=document([(False,False)])
        source['worlds']['other']=['C1','C2']
        source['slots'].append({'slot':'other-slot','world':'other'})
        source['judgments'] += [{'slot':'other-slot','coder_id':c,'code_id':'C1','value':True} for c in ('a','b')]
        ref=references([False])
        ref['judgments'].append({'slot':'other-slot','code_id':'C1','value':False,'evidence_locator':'synthetic://other'})
        rows=build_code_reference_report(source,ref)['reference_comparisons']
        by_key={(r['world'],r['code_id'],r['coder_id']):r for r in rows}
        self.assertEqual(by_key['w','C1','a']['reference_agreement'],1)
        self.assertEqual(by_key['other','C1','a']['reference_agreement'],0)
        self.assertEqual(by_key['other','C2','a']['missing_reference_labels'],1)

    def test_inputs_are_unchanged_and_record_order_does_not_change_report(self):
        source=document([(False,True),(True,True)])
        ref=references([False,True])
        before=copy.deepcopy((source,ref))
        report=build_code_reference_report(source,ref)
        self.assertEqual((source,ref),before)
        source['slots'].reverse();source['judgments'].reverse();ref['judgments'].reverse()
        self.assertEqual(build_code_reference_report(source,ref),report)

    def test_reference_contract_rejects_duplicates_unknowns_and_non_boolean_labels(self):
        mutations=[lambda r:r.update(schema_version='other'),lambda r:r.update(reference_id=' '),
                   lambda r:r.update(extra=True),lambda r:r['judgments'].append(copy.deepcopy(r['judgments'][0])),
                   lambda r:r['judgments'][0].update(slot='absent'),lambda r:r['judgments'][0].update(code_id='absent'),
                   lambda r:r['judgments'][0].update(value=1),lambda r:r['judgments'][0].update(value='false'),
                   lambda r:r['judgments'][0].update(evidence_locator=' '),lambda r:r['judgments'][0].pop('evidence_locator')]
        for mutate in mutations:
            ref=references([False]);mutate(ref)
            with self.subTest(ref=ref),self.assertRaises(ValueError):
                build_code_reference_report(document([(False,False)]),ref)
        with self.assertRaises(ValueError):
            build_code_reference_report(document([(False,False)]),None)

    def test_coder_input_contract_is_still_enforced(self):
        source=document([(False,True)])
        source['judgments'][0]['value']=0
        with self.assertRaises(ValueError):
            build_code_reference_report(source,references([False]))


class ReferenceCLITests(unittest.TestCase):
    def invoke(self,source,reference):
        return subprocess.run([sys.executable,'scripts/code_agreement.py',str(source),'--reference',str(reference)],
                              env={**os.environ,'PYTHONPATH':'src'},capture_output=True,text=True,check=False)

    def test_cli_hashes_both_original_inputs_and_preserves_them(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'judgments.json';ref=Path(temp)/'references.json'
            source.write_text(json.dumps(document([(False,False),(True,True)])))
            ref.write_text(json.dumps(references([True,False])))
            before=(source.read_bytes(),ref.read_bytes())
            result=self.invoke(source,ref)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads(result.stdout)
            self.assertEqual(report['schema_version'],'caplab-code-reference-report/1')
            self.assertEqual(report['input_sha256'],hashlib.sha256(before[0]).hexdigest())
            self.assertEqual(report['reference_sha256'],hashlib.sha256(before[1]).hexdigest())
            self.assertEqual(report['reference_comparisons'][0]['reference_agreement'],0)
            self.assertEqual((source.read_bytes(),ref.read_bytes()),before)

    def test_invalid_reference_file_emits_no_report_and_is_not_treated_as_absent(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'judgments.json';ref=Path(temp)/'references.json'
            source.write_text(json.dumps(document([(False,False)])))
            valid=json.dumps(references([False]))
            for bad in ('null',valid.replace('"value": false','"value": false, "value": true'),
                        valid.replace('"value": false','"value": NaN')):
                ref.write_text(bad)
                result=self.invoke(source,ref)
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(result.stdout,'')
                self.assertEqual(ref.read_text(),bad)


if __name__=='__main__':
    unittest.main()
