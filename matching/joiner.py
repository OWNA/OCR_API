# Joiner role is to group together blocks of words which were
# were not considered by Abby as belonging to the same block, but they
# do correspond to the same description sentence, and should therefore
# be merged.

from assignment import CellAssignment
from debug import printAssignment
from constants import *
from line import LineComparator
from exceptions import CellAssignmentOverlap
from utils.items import NewItem
from flags import MIN_LINE_HEIGHT, MIN_WORD_SEPARATION

lineComparator = LineComparator()


def merge(assignment):
    for relevantIndex, relevantPart in enumerate(assignment.relevantParts):
        if relevantPart == DESCRIPTION:
            for lineIndex, productItem in enumerate(assignment.productItems):
                if type(productItem) == NewItem:
                    continue
                cells = assignment.matching[lineIndex][relevantIndex]
                cells = mergeCells(cells, productItem.description)
                assignment.matching[lineIndex][relevantIndex] = cells
    return assignment


def cellsCompare(cell1, cell2):
    """
    Compare two cells to be ordered w.r.t to each others.
    If the cells project along y axis, then we expect that they will not
    overlap along the x axis and their ordering is obvious according to x.
    Otherwise their ordering is obvious according to y.
    We dont allow them to overlap at all and we will throw an exception if
    it happens
    """
    if cell2.page_index < cell1.page_index:
        return 1
    elif cell1.page_index < cell2.page_index:
        return -1
    if cell2.yT < cell1.yB and cell1.yT < cell2.yB:
        if cell1.xR < cell2.xL:
            return -1
        elif cell2.xR < cell1.xL:
            return 1
    elif cell2.yT > cell1.yB:
        return -1
    elif cell2.yT < cell1.yB:
        return 1
    raise CellAssignmentOverlap(cell1, cell2)


def mergeCells(assignmentCells, description):
    if len(assignmentCells) < 2:
        return assignmentCells
    lastCell = None
    newCells = []
    assignmentCells = sorted(assignmentCells, cmp=cellsCompare)
    for cell in assignmentCells:
        newCell = None
        if lastCell and lastCell.page_index == cell.page_index:
            if lastCell.xR > cell.xL and lastCell.yB > cell.yT:
                raise CellAssignmentOverlap(lastCell, cell)
            if (cell.xL - lastCell.xR < MIN_WORD_SEPARATION and
                cell.yT - lastCell.yB < MIN_LINE_HEIGHT):
                value = lastCell.value + ' '  + cell.value
                partMatch = lineComparator.alignNonNumericPart(value, description)
                newCell = CellAssignment(partMatch.score,
                                         lastCell.xL,
                                         cell.xR,
                                         lastCell.yT,
                                         cell.yB,
                                         value,
                                         cell.page_index,
                                         False)
                if (newCell.score > cell.score and
                    newCell.score > lastCell.score):
                    newCells.append(newCell)
                else:
                    newCell = None
        if not newCell and lastCell:
            newCells.append(lastCell)
        lastCell = cell
    if not newCell:
        newCells.append(lastCell)
    return newCells
