from constants import *
from flags import MIN_NUMERIC_SCORE_MATCH, MIN_LINE_HEIGHT


def getSmallestColumnCost(columnX, lines_count, remainingCount):
    columnX = np.array(columnX, dtype=np.float64)
    averageX = np.average(columnX)
    columnX -= averageX
    columnX = columnX * columnX
    return 2 * np.sum(columnX) * remainingCount / 900. / lines_count


def getSmallestLineCost(lineY, columns_count, remainingCount):
    lineY = np.array(lineY, dtype=np.float64)
    averageY = np.average(lineY)
    lineY -= averageY
    lineY = lineY * lineY
    return 2 * np.sum(lineY) * remainingCount / 400. / columns_count


def computeCost(assignment, options, debug=False):
    cost = 0
    for line_index, productItem in enumerate(assignment.productItems):
        for relevant_index, _ in enumerate(assignment.relevantParts):
            if len(assignment.matching[line_index][relevant_index]) != 1:
                continue
            match_cost = 0
            column_cost = 0
            line_cost = 0
            lines_count = 0
            columns_count = 0
            ass1 = assignment.matching[line_index][relevant_index][0]
            match_cost = 4 * (1 - ass1.score)
            for other_line_index, _ in enumerate(assignment.productItems):
                if len(assignment.matching[other_line_index][relevant_index]) == 0:
                    continue
                lines_count += 1
                if len(assignment.matching[other_line_index][relevant_index]) != 1:
                    continue
                ass2 = assignment.matching[other_line_index][relevant_index][0]
                justify = options['justify']
                if ass2.page_index == ass1.page_index:
                    column_cost += (ass1.getX(options) - ass2.getX(options))**2
            for other_column, _ in enumerate(assignment.relevantParts):
                if len(assignment.matching[line_index][other_column]) == 0:
                    continue
                columns_count += 1
                if len(assignment.matching[line_index][other_column]) != 1:
                    continue
                ass2 = assignment.matching[line_index][other_column][0]
                if ass2.page_index == ass1.page_index:
                    line_cost += (ass1.getY() - ass2.getY())**2
                else:
                    line_cost += INFINITE_COST
            if lines_count:
                column_cost = column_cost / lines_count / 900.
            if columns_count:
                line_cost = line_cost / columns_count / 400.
            if debug:
                print '{},{} - line:{:10.4f}, col:{:10.4f}, match:{:10.4f}, {}'.format(
                    line_index, relevant_index,
                    line_cost, column_cost, match_cost, productItem)
            cost += line_cost + column_cost + match_cost
    return cost


def computeLightCost(assignment,
                     previousCost,
                     lightAssignment,
                     line_index,
                     relevant_index,
                     options,
                     debug=False):
    lines_count = 0
    columns_count = 0
    column_cost = 0
    line_cost = 0
    match_cost = 0
    relevantPart = assignment.relevantParts[relevant_index]
    productItem = assignment.productItems[line_index]
    # Compute incremental matching cost
    ass1Index = lightAssignment[line_index][relevant_index]
    if ass1Index != EMPTY:
        ass1 = assignment.matching[line_index][relevant_index][ass1Index]
        # Make updates to match quantity and price
        # See https://trello.com/c/k3CYqw1B
        if (relevantPart == TOTAL_VALUE or relevantPart == VALUE):
            scoreBefore = ass1.score
            assert assignment.quantityIndex != None
            qAssIndex = lightAssignment[line_index][assignment.quantityIndex]
            assert qAssIndex != EMPTY
            qAss = assignment.matching[line_index][assignment.quantityIndex][qAssIndex]
            if not ass1.newItem:
                if relevantPart == TOTAL_VALUE:
                    ass1.updateNumericScore(
                        productItem.totalUnitPrice * float(qAss.value))
                else:
                    ass1.updateNumericScore(
                        productItem.unitPrice * float(qAss.value))
        if ass1.score < MIN_NUMERIC_SCORE_MATCH and not ass1.newItem:
            match_cost = INFINITE_COST
        else:
            match_cost = 4 * (1 - ass1.score)
    else:
        match_cost = 4
    # Compute incremental column cost
    for other_line_index, _ in enumerate(assignment.productItems):
        if len(assignment.matching[other_line_index][relevant_index]) == 0:
            continue
        lines_count += 1
        if other_line_index == line_index:
            continue
        ass2Index = lightAssignment[other_line_index][relevant_index]
        if ass2Index == -1:
            continue
        if ass2Index == EMPTY or ass1Index == EMPTY:
            if relevantPart == DESCRIPTION:
                column_cost += 90000
            continue
        ass2 = assignment.matching[other_line_index][relevant_index][ass2Index]
        if ass2.page_index == ass1.page_index:
            column_cost += (ass1.getX(options) - ass2.getX(options))**2
        # Prevent duplicate matching
        if (other_line_index != line_index and
            abs(ass1.getY() - ass2.getY()) < MIN_LINE_HEIGHT):
            column_cost += INFINITE_COST
    if lines_count:
        column_cost = 2 * column_cost / lines_count / 900.
    # Compute incremental line cost
    for other_column, otherRelevantPart in enumerate(assignment.relevantParts):
        if len(assignment.matching[line_index][other_column]) == 0:
            continue
        columns_count += 1
        if other_column == relevant_index:
            continue
        ass2Index = lightAssignment[line_index][other_column]
        if ass2Index == -1:
            continue
        if (ass2Index == EMPTY and
            otherRelevantPart == DESCRIPTION and
            ass1Index != EMPTY):
            # If the description is empty, all other columns should be
            line_cost += INFINITE_COST
        if ass2Index == EMPTY or ass1Index == EMPTY:
            line_cost += 400
            continue
        ass2 = assignment.matching[line_index][other_column][ass2Index]
        if ass2.page_index == ass1.page_index:
            line_cost += (ass1.getY() - ass2.getY())**2
        else:
            line_cost += INFINITE_COST
    if columns_count:
        line_cost = 2 * line_cost / columns_count / 400.
    if debug:
        print '{}'.format(lightAssignment)
        print 'incr - line:{:10.4f}, col:{:10.4f}, match:{:10.4f}, {}'.format(
            line_cost, column_cost, match_cost, assignment.productItems[line_index])
        print previousCost + line_cost + column_cost + match_cost
    return previousCost + line_cost + column_cost + match_cost
