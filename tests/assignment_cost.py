import unittest
from matching.assignment import Assignment, emptyLight
from matching.constants import *
from matching.cost import computeCost, computeLightCost
from matching.debug import printAssignment
from utils.items import OrderedItem
from utils.files import SimpleWord


RELEVANT_PARTS = [QUANTITY, DESCRIPTION, TOTAL_VALUE]
OPTIONS = {'justify': LEFT}
PRODUCT_ITEMS = [
    OrderedItem('', '', 'Best pudding', '', '', '', 100, 100, 100, 100, 1),
    OrderedItem('', '', 'Healthy lettuce', '', '', '', 100, 100, 100, 100, 1),
    OrderedItem('', '', 'Fresh eggs', '', '', '', 50, 50, 150, 150, 3)
]


def assign(line_index, relevant_index, index, ass):
    ass.matching[line_index][relevant_index] = (
        [ass.matching[line_index][relevant_index][index]])

def soft_assign(line_index, relevant_index, index, light_ass):
    light_ass[line_index][relevant_index] = index


class TestAssignmentCost(unittest.TestCase):

    def run_assignment_test(self, ass, cost_array, assignment_array):
        light_ass = emptyLight(ass)
        light_cost = 0
        for expected_cost, (line_index, relevant_index, index) in zip(
                cost_array, assignment_array):
            soft_assign(line_index, relevant_index, index, light_ass)
            light_cost = computeLightCost(ass, light_cost, light_ass,
                                          line_index, relevant_index, OPTIONS)
            if expected_cost is not None:
                self.assertAlmostEquals(expected_cost, light_cost)
        for line_index, relevant_index, index in assignment_array:
            assign(line_index, relevant_index, index, ass)
        cost = computeCost(ass, OPTIONS)
        self.assertAlmostEquals(expected_cost, cost)


class TestSinglePageAssignmentCost(TestAssignmentCost):

    def test_empty_assignment(self):
        ass = Assignment(PRODUCT_ITEMS, RELEVANT_PARTS, [])
        ass.build()
        cost = computeCost(ass, OPTIONS)
        self.assertAlmostEquals(0, cost)

    def test_one_assignment_matching(self):
        ass = Assignment(PRODUCT_ITEMS, RELEVANT_PARTS, [
            SimpleWord('best pudding', 0, 0, 0, 0),
            SimpleWord('100', 50, 50, 0, 0),
            SimpleWord('1', 100, 100, 0, 0),
        ])
        ass.build()
        cost = computeCost(ass, OPTIONS)
        self.assertAlmostEquals(0, cost)
        self.run_assignment_test(ass, [
            0,
            0,
            0
        ], [
            (0, 0, 1),
            (0, 1, 0),
            (0, 2, 0),
        ])

    def test_one_assignment_differs(self):
        ass = Assignment(PRODUCT_ITEMS, RELEVANT_PARTS, [
            SimpleWord('bast padding', 0, 0, 0, 0),
            SimpleWord('100', 50, 50, 20, 20),
            SimpleWord('1', 100, 100, 40, 40),
        ])
        ass.build()
        cost = computeCost(ass, OPTIONS)
        self.assertAlmostEquals(1, cost)
        self.run_assignment_test(ass, [
            0,
            1 + (1600 * 2) / 3. / 400,
            1 + (1600 * 2 + 400 * 4) / 3. / 400,
        ], [
            (0, 0, 1),
            (0, 1, 0),
            (0, 2, 0),
        ])

    def test_two_assignments(self):
        ass = Assignment(PRODUCT_ITEMS, RELEVANT_PARTS, [
            SimpleWord('best pudding', 0, 0, 0, 0),
            SimpleWord('100', 50, 50, 20, 20),
            SimpleWord('1', 100, 100, 40, 40),
            SimpleWord('Healthy lettuce', 30, 30, 100, 100),
            SimpleWord('100', 80, 80, 120, 120),
            SimpleWord('1', 130, 130, 140, 140),
        ])
        ass.build()
        cost = computeCost(ass, OPTIONS)
        self.assertAlmostEquals(1, cost)
        self.run_assignment_test(ass, [
            0,
            (1600 * 2) / 3. / 400,
            (1600 * 2 + 400 * 4) / 3. / 400,
            (1600 * 2 + 400 * 4) / 3. / 400 + 2 * 900 / 900. / 2.,
            (1600 * 4 + 400 * 4) / 3. / 400 + 4 * 900 / 900. / 2.,
            (1600 * 4 + 400 * 8) / 3. / 400 + 6 * 900 / 900. / 2.
        ], [
            (0, 0, 1),
            (0, 1, 0),
            (0, 2, 0),
            (1, 0, 3),
            (1, 1, 0),
            (1, 2, 2),
        ])

    def test_three_assignments(self):
        ass = Assignment(PRODUCT_ITEMS, RELEVANT_PARTS, [
            SimpleWord('best pudding', 0, 0, 0, 0),
            SimpleWord('100', 50, 50, 20, 20),
            SimpleWord('1', 100, 100, 40, 40),

            SimpleWord('Healthy lettuce', 30, 30, 100, 100),
            SimpleWord('100', 80, 80, 120, 120),
            SimpleWord('1', 130, 130, 140, 140),

            SimpleWord('Fresh eggs', 60, 60, 200, 200),
            SimpleWord('150', 110, 110, 220, 220),
            SimpleWord('3', 160, 160, 240, 240),
        ])
        ass.build()
        cost = computeCost(ass, OPTIONS)
        column_cost = (900 * 4 + 3600 * 2) / 900. / 3.
        self.assertAlmostEquals(column_cost, cost)

        self.run_assignment_test(ass, [
            0,
            (1600 * 2) / 3. / 400,
            (1600 * 2 + 400 * 4) / 3. / 400,
            (1600 * 2 + 400 * 4) / 3. / 400 + 2 * 900 / 900. / 3.,
            (1600 * 4 + 400 * 4) / 3. / 400 + 4 * 900 / 900. / 3.,
            (1600 * 4 + 400 * 8) / 3. / 400 + 6 * 900 / 900. / 3.,
            (1600 * 4 + 400 * 8) / 3. / 400 + (8 * 900 + 3600 * 2) / 900. / 3.,
            (1600 * 6 + 400 * 8) / 3. / 400 + (10 * 900 + 3600 * 4) / 900. / 3.,
            (1600 * 6 + 400 * 12) / 3. / 400 + (12 * 900 + 3600 * 6) / 900. / 3.,
        ], [
            (0, 0, 1),
            (0, 1, 0),
            (0, 2, 0),
            (1, 0, 3),
            (1, 1, 0),
            (1, 2, 2),
            (2, 0, 5),
            (2, 1, 0),
            (2, 2, 4),
        ])


class TestMultiPageAssignmentCost(TestAssignmentCost):

    def test_two_assignments(self):
        ass = Assignment(PRODUCT_ITEMS, RELEVANT_PARTS, [
            SimpleWord('best pudding', 0, 0, 0, 0, page_index=0),
            SimpleWord('100', 50, 50, 20, 20, page_index=0),
            SimpleWord('1', 100, 100, 40, 40, page_index=0),
            SimpleWord('Healthy lettuce', 30, 30, 100, 100, page_index=1),
            SimpleWord('100', 80, 80, 120, 120, page_index=1),
            SimpleWord('1', 130, 130, 140, 140, page_index=1),
        ])
        ass.build()
        cost = computeCost(ass, OPTIONS)
        self.assertAlmostEquals(0, cost)

        self.run_assignment_test(ass, [
            0,
            (1600 * 2) / 3. / 400,
            (1600 * 2 + 400 * 4) / 3. / 400,
            (1600 * 2 + 400 * 4) / 3. / 400,
            (1600 * 4 + 400 * 4) / 3. / 400,
            (1600 * 4 + 400 * 8) / 3. / 400
        ], [
            (0, 0, 1),
            (0, 1, 0),
            (0, 2, 0),
            (1, 0, 3),
            (1, 1, 0),
            (1, 2, 2),
        ])

    def test_three_assignments(self):
        ass = Assignment(PRODUCT_ITEMS, RELEVANT_PARTS, [
            SimpleWord('best pudding', 0, 0, 0, 0, page_index=0),
            SimpleWord('100', 50, 50, 20, 20, page_index=0),
            SimpleWord('1', 100, 100, 40, 40, page_index=0),

            SimpleWord('Healthy lettuce', 30, 30, 100, 100, page_index=0),
            SimpleWord('100', 80, 80, 120, 120, page_index=0),
            SimpleWord('1', 130, 130, 140, 140, page_index=0),

            SimpleWord('Fresh eggs', 60, 60, 200, 200, page_index=1),
            SimpleWord('150', 110, 110, 220, 220, page_index=1),
            SimpleWord('3', 160, 160, 240, 240, page_index=1),
        ])
        ass.build()
        cost = computeCost(ass, OPTIONS)
        column_cost = (900 * 2) / 900. / 3.
        self.assertAlmostEquals(column_cost, cost)

        self.run_assignment_test(ass, [
            0,
            (1600 * 2) / 3. / 400,
            (1600 * 2 + 400 * 4) / 3. / 400,
            (1600 * 2 + 400 * 4) / 3. / 400 + 2 * 900 / 900. / 3.,
            (1600 * 4 + 400 * 4) / 3. / 400 + 4 * 900 / 900. / 3.,
            (1600 * 4 + 400 * 8) / 3. / 400 + 6 * 900 / 900. / 3.,
            (1600 * 4 + 400 * 8) / 3. / 400 + 6 * 900 / 900. / 3.,
            (1600 * 6 + 400 * 8) / 3. / 400 + 6 * 900 / 900. / 3.,
            (1600 * 6 + 400 * 12) / 3. / 400 + 6 * 900 / 900. / 3.,
        ], [
            (0, 0, 1),
            (0, 1, 0),
            (0, 2, 0),
            (1, 0, 3),
            (1, 1, 0),
            (1, 2, 2),
            (2, 0, 5),
            (2, 1, 0),
            (2, 2, 4),
        ])


if __name__ == '__main__':
    unittest.main()
