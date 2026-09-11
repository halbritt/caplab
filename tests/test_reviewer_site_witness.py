from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from reviewer_site_witness import capture_inventory
from verify_reviewer_site_witness import assess_view, assess_http


class SiteWitnessTests(unittest.TestCase):
    def test_rendered_nameplate_cannot_pass_with_clipping_or_script_elements(self):
        view={'viewport':320,'scrollWidth':320,'nameplate':{'text':'AI Newsroom','href':'/',
            'rect':{'x':18,'right':290,'width':272,'height':34}},'mark':None,'scriptElements':0,
            'bodyText':'<script>fixture()</script> Local model release <img src=x onerror=fixture()>','icon':None}
        self.assertTrue(all(assess_view('base',view).values()))
        view['nameplate']['rect']['right']=340
        view['scriptElements']=1
        result=assess_view('base',view)
        self.assertFalse(result['nameplate_within_viewport'])
        self.assertFalse(result['source_text_rendered_literally'])

    def test_successful_private_path_and_wrong_svg_type_remain_failures(self):
        self.assertFalse(assess_http({'path':'/escape.svg','method':'GET','status':200,'headers':{}},'icon')['expected_status'])
        row={'path':'/icon.svg','method':'GET','status':200,'headers':{'Content-type':'text/plain'}}
        self.assertFalse(assess_http(row,'icon')['asset_mime'])

    def test_capture_inventory_preserves_namespace_links_without_reading_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/'capture';root.mkdir()
            outside=Path(directory)/'private';outside.write_text('not a captured file')
            (root/'outside').symlink_to(outside)
            (root/'public').symlink_to('/capture/site-builds/edition-example')
            rows=capture_inventory(root)
            self.assertEqual(len(rows),2)
            self.assertTrue(all('sha256' not in row for row in rows))
            self.assertEqual(rows[1]['symlink'],'/capture/site-builds/edition-example')


if __name__=='__main__':unittest.main()
