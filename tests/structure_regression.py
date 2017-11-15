import unittest

from table.segmenter import segment_and_label_from_raw_ocr
from utils.files import XMLFile
from table.pdf import segment_and_label_pdf
from termcolor import colored
from tabulate import tabulate
import json


debug = False


class TestStructureExtractor(unittest.TestCase):

    def compare_truth(self, table, headers, truth_filename):
        truth = json.load(open(truth_filename, 'r'))
        expected_headers = truth['headers']
        expected_table = truth['table']
        print truth_filename
        print tabulate(table, headers)
        self.assertEquals(expected_headers, headers)
        self.assertEquals(expected_table, table)

    def run_image_extractor(self, structure_id):
        directory = 'data/production/structure/{}'.format(structure_id)
        xml_filename = '{}/abbyy.xml'.format(directory)
        text_filename = '{}/abbyy.txt'.format(directory)
        truth_filename = '{}/truth.json'.format(directory)
        xml_file = XMLFile(xml_filename)
        xml_file.parseWithVariants(split=True)
        f = open(text_filename)
        lines = []
        for line in f.readlines():
            if line.strip():
                lines.append(line.strip())
        table, headers = segment_and_label_from_raw_ocr(lines, xml_file.words)
        if debug:
            print json.dumps({
                "filename": truth_filename,
                "headers": headers,
                "table": table,
            }, indent=4)
        self.compare_truth(table, headers, truth_filename)

    def run_pdf_extractor(self, structure_id):
        directory = 'data/production/structure/{}'.format(structure_id)
        file_url = '{}/file.pdf'.format(directory)
        truth_filename = '{}/truth.json'.format(directory)
        table, headers = segment_and_label_pdf(file_url)
        if debug:
            print json.dumps({
                "filename": truth_filename,
                "headers": headers,
                "table": table,
            }, indent=4)
        self.compare_truth(table, headers, truth_filename)

    def test_image_empty(self):
        self.run_image_extractor(158)

    def test_imafe_qffs(self):
        pass
        #self.run_image_extractor(26)

    def test_image_bidvest(self):
        self.run_image_extractor(42)

    def test_pdf_global_food_wine(self):
        self.run_pdf_extractor(30)

    def test_pdf_bidfood(self):
        self.run_pdf_extractor(27)
        self.run_pdf_extractor(40)
        self.run_pdf_extractor(54)
        self.run_pdf_extractor(138)

    def test_pdf_bidfood_invoice(self):
        self.run_pdf_extractor(199)


if __name__ == '__main__':
    unittest.main()
