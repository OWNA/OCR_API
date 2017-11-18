import unittest

import json
from utils.files import XMLFile, SimpleWord
from ocrapi.api.parser import parse_orders
from ocrapi.api.order_match import find_best_soft_match
from matching.optimizer import optimizeMatching
from matching.structure import Structure
from matching.debug import printAssignment
from table.matcher import segment_and_label_with_matching
from termcolor import colored
from tabulate import tabulate


class TestInvoiceMatching(unittest.TestCase):

    def equals(item1, item2):
        return (
            item1['description'] == item2['description'] and
            abs(item1['quantity'] - item2['quantity']) < 0.01 and
            abs(item1['price'] - item2['price']) < 0.01
        )
        return True

    def run_matcher(self, invoice_id):

        xmlFile = XMLFile('data/production/images/{}/abbyy.xml'.format(invoice_id))
        xmlFile.parseWithVariants()
        orders = parse_orders(
            json.load(open('data/production/images/{}/order.json'.format(invoice_id))))
        distance, (order_id, items) = find_best_soft_match(orders, xmlFile.words)

        bestCost, bestAssignment = optimizeMatching(xmlFile.words, items)
        for (t, h) in segment_and_label_with_matching(xmlFile.words,
                                                      bestAssignment):
            continue
            print tabulate(t, h)
        #printAssignment(bestAssignment)

        structure = Structure(bestAssignment)

        output = structure.get_json()
        expected_output = json.load(open(
            'data/production/images/{}/truth.json'.format(invoice_id)))

        self.assertLessEqual(len(expected_output), len(output))

        for item1, item2 in zip(expected_output, output):
            self.assertEqual(item1['description'], item2['description'])
            self.assertAlmostEqual(item1['quantity'], item2['quantity'])
            self.assertAlmostEqual(item1['price'], item2['price'])

    def test_invoice_matching_qffs(self):
        # Invoice 1135131 QFFS
        # Missing rows due to blur https://trello.com/c/S0RR3LqP
        #self.run_matcher(409) # Blur
        # Scanned version
        self.run_matcher(408) # Scan
        # Missing fractional digit https://trello.com/c/xDd8wgAG
        #self.run_matcher(405) # Photo

    def test_invoice_matching_jubilee(self):

        # Invoice 16270 Jubilee
        # Multi column quantity https://trello.com/c/AcprXW31
        #self.run_matcher(311)
        # Missing digit 1 in hundred position https://trello.com/c/WrD48qFu
        #self.run_matcher(169)
        self.run_matcher(518)

        # Invoice 15786 Jubilee
        # GST price column not recognized https://trello.com/c/efxpdNWe
        #self.run_matcher(334)
        #self.run_matcher(333)
        pass

    def test_invoice_matching_bidvest(self):
        # Missing rows and error in quantity reading
        # self.run_matcher(558)
        pass

    def test_invoice_matching_bidfood(self):
        self.run_matcher(589)
        pass

    def test_invoice_matching_test_wholesaler(self):
        # Invoice 1234567 Test Wholesaler
        self.run_matcher(296)
        pass

    def test_invoice_matching_test_costco(self):
        # Invoice 101138 Costco
        self.run_matcher(283)
        pass


if __name__ == '__main__':
    unittest.main()
