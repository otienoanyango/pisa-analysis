import unittest
from unittest import TestCase
import os
import json

from pisa_utils import analyse

test_data_path= os.path.join('tests', 'data')

class TestJsonFile(TestCase):
        
    def test_json_output_equal_result(self):

        ref_data_file = os.path.join(test_data_path,'test_result.json')
        with open(ref_data_file) as test_file:
            ref_json = json.load(test_file)

        pisa_config_file=os.path.join(test_data_path,'pisa.cfg')

        ap= analyse.AnalysePisa(pdbid_id="6nxr", assembly_id="1", pisa_config = pisa_config_file, output_dir=test_data_path, force=True, result_json_file="output.json", input_dir=test_data_path)
        
        ap.run_process()

        output_data_file = os.path.join(test_data_path,'output.json')
        with open(output_data_file) as output_file:
            out_json = json.load(output_file)

        self.assertEqual(ref_json, out_json)
        
if __name__ == '__main__':
    unittest.main()

        

