import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from reviewer_evidence_assessment import compare_assessments


class EvidenceAssessmentTests(unittest.TestCase):
    def test_matching_labels_do_not_establish_semantic_support(self):
        inputs={'documents':[{'document_id':'d','findings':[{'finding_id':'f','reported':{'claim_status':'uncertain','acceptance_effect':'advise'}}]}]}
        expected={'entries':[{'document_id':'d','finding_id':'f','defect_assessment':'mixed','duplicate_of':None,'required_evidence_groups':[['source.txt']]}]}
        output={'entries':[{'document_id':'d','finding_id':'f','reported_claim_status':'uncertain','acceptance_effect':'advise','defect_assessment':'mixed','duplicate_of':None,'reason':'The specific cutoff is false but deployment relevance is unknown.','evidence':[{'path':'source.txt','start_line':1,'end_line':1,'support':'Alleged support'}]}]}
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'source.txt').write_text('unrelated literal words\n')
            result=compare_assessments(inputs,expected,output,root)
            self.assertTrue(result['all_structural_and_label_checks_match'])
            self.assertFalse(result['semantic_support_verified'])
            self.assertFalse(result['scorer_accepted'])
            output['entries'][0]['acceptance_effect']='block'
            result=compare_assessments(inputs,expected,output,root)
            self.assertFalse(result['all_structural_and_label_checks_match'])


    def test_missing_or_duplicate_findings_cannot_pass_as_complete(self):
        inputs={'documents':[{'document_id':'d','findings':[{'finding_id':'f','reported':{'claim_status':'asserted','acceptance_effect':'block'}}]}]}
        expected={'entries':[{'document_id':'d','finding_id':'f','defect_assessment':'unresolved','duplicate_of':None,'required_evidence_groups':[]}]}
        row={'document_id':'d','finding_id':'f','reported_claim_status':'asserted','acceptance_effect':'block','defect_assessment':'unresolved','duplicate_of':None,'reason':'The requirement is not established.','evidence':[]}
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for entries in ([],[row,row]):
                with self.assertRaises(ValueError):compare_assessments(inputs,expected,{'entries':entries},root)
            row['evidence']=[{'path':'../outside','start_line':1,'end_line':1,'support':'Claimed evidence outside the task.'}]
            result=compare_assessments(inputs,expected,{'entries':[row]},root)
            self.assertFalse(result['all_structural_and_label_checks_match'])
            self.assertEqual(result['observations'][0]['citations'][0]['location']['status'],'unsafe-path')


if __name__=='__main__':unittest.main()
